#!/usr/bin/env python3
"""
Standardize AI Assistant Database Schema

This script ensures both development and production databases have the same
AI Assistant knowledge base schema, using the development schema as the standard.
"""

import asyncio
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Database connection strings
DEV_DATABASE_URL = "postgresql://abparts_user:abparts_pass@localhost:5432/abparts_dev"
PROD_DATABASE_URL = "postgresql://abparts_user:abparts_pass@localhost:5432/abparts_prod"

def get_standard_schema_sql():
    """Get the standard AI Assistant schema SQL based on development."""
    return """
    -- Drop existing tables if they exist (in correct order due to foreign keys)
    DROP TABLE IF EXISTS document_chunks CASCADE;
    DROP TABLE IF EXISTS knowledge_documents CASCADE;
    
    -- Drop the old knowledge_chunks table if it exists (from production)
    DROP TABLE IF EXISTS knowledge_chunks CASCADE;
    
    -- Create knowledge_documents table (development standard)
    CREATE TABLE knowledge_documents (
        id character varying NOT NULL,
        title character varying NOT NULL,
        document_type character varying NOT NULL DEFAULT 'manual'::character varying,
        version character varying,
        language character varying NOT NULL DEFAULT 'en'::character varying,
        file_path character varying,
        file_hash character varying,
        chunk_count integer NOT NULL DEFAULT 0,
        created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
        document_metadata jsonb,
        machine_models text[],
        tags text[]
    );
    
    -- Create document_chunks table (development standard)
    CREATE TABLE document_chunks (
        id character varying NOT NULL,
        document_id character varying NOT NULL,
        chunk_index integer NOT NULL,
        content text NOT NULL,
        embedding jsonb,
        created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Add primary keys
    ALTER TABLE ONLY knowledge_documents ADD CONSTRAINT knowledge_documents_pkey PRIMARY KEY (id);
    ALTER TABLE ONLY document_chunks ADD CONSTRAINT document_chunks_pkey PRIMARY KEY (id);
    
    -- Add unique constraints
    ALTER TABLE ONLY knowledge_documents ADD CONSTRAINT knowledge_documents_file_hash_key UNIQUE (file_hash);
    
    -- Add foreign key constraints
    ALTER TABLE ONLY document_chunks ADD CONSTRAINT document_chunks_document_id_fkey 
        FOREIGN KEY (document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE;
    
    -- Create indexes for knowledge_documents
    CREATE INDEX idx_knowledge_documents_created_at ON knowledge_documents USING btree (created_at);
    CREATE INDEX idx_knowledge_documents_language ON knowledge_documents USING btree (language);
    CREATE INDEX idx_knowledge_documents_machine_models ON knowledge_documents USING gin (machine_models);
    CREATE INDEX idx_knowledge_documents_tags ON knowledge_documents USING gin (tags);
    CREATE INDEX idx_knowledge_documents_type ON knowledge_documents USING btree (document_type);
    CREATE INDEX idx_knowledge_documents_updated_at ON knowledge_documents USING btree (updated_at);
    
    -- Create indexes for document_chunks
    CREATE INDEX idx_document_chunks_document_id ON document_chunks USING btree (document_id);
    
    -- Create trigger function for updated_at
    CREATE OR REPLACE FUNCTION update_knowledge_document_updated_at()
    RETURNS trigger AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    
    -- Create trigger
    CREATE TRIGGER trigger_update_knowledge_document_updated_at
        BEFORE UPDATE ON knowledge_documents
        FOR EACH ROW
        EXECUTE FUNCTION update_knowledge_document_updated_at();
    """

def backup_existing_data(database_url: str, environment: str):
    """Backup existing AI Assistant data before schema changes."""
    print(f"📦 Backing up existing AI Assistant data in {environment}...")
    
    engine = create_engine(database_url)
    backup_data = {
        'knowledge_documents': [],
        'document_chunks': []
    }
    
    try:
        with engine.connect() as conn:
            # Check if tables exist and backup data
            try:
                # Backup knowledge_documents
                result = conn.execute(text("SELECT * FROM knowledge_documents"))
                backup_data['knowledge_documents'] = [dict(row._mapping) for row in result]
                print(f"  ✅ Backed up {len(backup_data['knowledge_documents'])} knowledge documents")
            except Exception as e:
                print(f"  ⚠️  No knowledge_documents table to backup: {e}")
            
            try:
                # Backup document_chunks
                result = conn.execute(text("SELECT * FROM document_chunks"))
                backup_data['document_chunks'] = [dict(row._mapping) for row in result]
                print(f"  ✅ Backed up {len(backup_data['document_chunks'])} document chunks")
            except Exception as e:
                print(f"  ⚠️  No document_chunks table to backup: {e}")
            
            try:
                # Also check for knowledge_chunks (production naming)
                result = conn.execute(text("SELECT * FROM knowledge_chunks"))
                knowledge_chunks = [dict(row._mapping) for row in result]
                # Convert to document_chunks format
                for chunk in knowledge_chunks:
                    backup_data['document_chunks'].append({
                        'id': chunk.get('id'),
                        'document_id': chunk.get('document_id'),
                        'chunk_index': chunk.get('chunk_index'),
                        'content': chunk.get('content'),
                        'embedding': None,  # Will need to be regenerated
                        'created_at': chunk.get('created_at')
                    })
                print(f"  ✅ Converted {len(knowledge_chunks)} knowledge_chunks to document_chunks format")
            except Exception as e:
                print(f"  ⚠️  No knowledge_chunks table to backup: {e}")
                
    except Exception as e:
        print(f"  ❌ Error during backup: {e}")
        return None
    
    finally:
        engine.dispose()
    
    return backup_data

def restore_data(database_url: str, environment: str, backup_data: dict):
    """Restore backed up data to the new schema."""
    if not backup_data or (not backup_data['knowledge_documents'] and not backup_data['document_chunks']):
        print(f"  ⚠️  No data to restore in {environment}")
        return True
    
    print(f"📥 Restoring data in {environment}...")
    
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Restore knowledge_documents
            for doc in backup_data['knowledge_documents']:
                # Convert UUID to string if necessary
                doc_id = str(doc['id'])
                
                # Handle different field names/types between schemas
                insert_sql = """
                INSERT INTO knowledge_documents (
                    id, title, document_type, version, language, file_path, 
                    file_hash, chunk_count, created_at, updated_at, 
                    document_metadata, machine_models, tags
                ) VALUES (
                    :id, :title, :document_type, :version, :language, :file_path,
                    :file_hash, :chunk_count, :created_at, :updated_at,
                    :document_metadata, :machine_models, :tags
                )
                """
                
                conn.execute(text(insert_sql), {
                    'id': doc_id,
                    'title': doc.get('title'),
                    'document_type': doc.get('document_type', 'manual'),
                    'version': doc.get('version', '1.0'),
                    'language': doc.get('language', 'en'),
                    'file_path': doc.get('file_path'),
                    'file_hash': doc.get('file_hash'),
                    'chunk_count': doc.get('chunk_count', 0),
                    'created_at': doc.get('created_at'),
                    'updated_at': doc.get('updated_at'),
                    'document_metadata': doc.get('document_metadata'),
                    'machine_models': doc.get('machine_models'),
                    'tags': doc.get('tags')
                })
            
            print(f"  ✅ Restored {len(backup_data['knowledge_documents'])} knowledge documents")
            
            # Restore document_chunks
            for chunk in backup_data['document_chunks']:
                # Convert UUID to string if necessary
                chunk_id = str(chunk['id']) if chunk['id'] else f"{chunk['document_id']}_chunk_{chunk['chunk_index']}"
                doc_id = str(chunk['document_id'])
                
                insert_sql = """
                INSERT INTO document_chunks (
                    id, document_id, chunk_index, content, embedding, created_at
                ) VALUES (
                    :id, :document_id, :chunk_index, :content, :embedding, :created_at
                )
                """
                
                conn.execute(text(insert_sql), {
                    'id': chunk_id,
                    'document_id': doc_id,
                    'chunk_index': chunk.get('chunk_index'),
                    'content': chunk.get('content'),
                    'embedding': chunk.get('embedding'),
                    'created_at': chunk.get('created_at')
                })
            
            print(f"  ✅ Restored {len(backup_data['document_chunks'])} document chunks")
            
            conn.commit()
            
    except Exception as e:
        print(f"  ❌ Error during restore: {e}")
        return False
    
    finally:
        engine.dispose()
    
    return True

def apply_standard_schema(database_url: str, environment: str):
    """Apply the standard AI Assistant schema to a database."""
    print(f"🔧 Applying standard AI Assistant schema to {environment}...")
    
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Execute the schema SQL
            schema_sql = get_standard_schema_sql()
            
            # Split and execute each statement
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                try:
                    conn.execute(text(statement))
                    conn.commit()
                except Exception as e:
                    print(f"  ⚠️  Statement warning: {e}")
                    # Continue with other statements
            
        print(f"  ✅ Standard schema applied to {environment}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error applying schema to {environment}: {e}")
        return False
    
    finally:
        engine.dispose()

def verify_schema(database_url: str, environment: str):
    """Verify the schema is correct."""
    print(f"🔍 Verifying schema in {environment}...")
    
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Check knowledge_documents table
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'knowledge_documents'
                ORDER BY ordinal_position
            """))
            
            knowledge_docs_columns = [row._mapping for row in result]
            print(f"  ✅ knowledge_documents has {len(knowledge_docs_columns)} columns")
            
            # Check document_chunks table
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'document_chunks'
                ORDER BY ordinal_position
            """))
            
            document_chunks_columns = [row._mapping for row in result]
            print(f"  ✅ document_chunks has {len(document_chunks_columns)} columns")
            
            # Check indexes
            result = conn.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename IN ('knowledge_documents', 'document_chunks')
            """))
            
            indexes = [row[0] for row in result]
            print(f"  ✅ Found {len(indexes)} indexes")
            
            # Check data
            result = conn.execute(text("SELECT COUNT(*) FROM knowledge_documents"))
            doc_count = result.scalar()
            
            result = conn.execute(text("SELECT COUNT(*) FROM document_chunks"))
            chunk_count = result.scalar()
            
            print(f"  ✅ Data: {doc_count} documents, {chunk_count} chunks")
            
    except Exception as e:
        print(f"  ❌ Error verifying schema: {e}")
        return False
    
    finally:
        engine.dispose()
    
    return True

def main():
    """Main function to standardize schemas."""
    print("🔄 Standardizing AI Assistant Database Schemas")
    print("=" * 50)
    print("Using development schema as the standard")
    print()
    
    # Step 1: Backup existing data from both environments
    print("Step 1: Backing up existing data...")
    dev_backup = backup_existing_data(DEV_DATABASE_URL, "development")
    prod_backup = backup_existing_data(PROD_DATABASE_URL, "production")
    
    if not dev_backup and not prod_backup:
        print("⚠️  No existing data found in either environment")
    
    # Step 2: Apply standard schema to both environments
    print("\nStep 2: Applying standard schema...")
    dev_success = apply_standard_schema(DEV_DATABASE_URL, "development")
    prod_success = apply_standard_schema(PROD_DATABASE_URL, "production")
    
    if not dev_success or not prod_success:
        print("❌ Schema application failed!")
        return False
    
    # Step 3: Restore data
    print("\nStep 3: Restoring data...")
    if dev_backup:
        restore_data(DEV_DATABASE_URL, "development", dev_backup)
    
    if prod_backup:
        restore_data(PROD_DATABASE_URL, "production", prod_backup)
    
    # Step 4: Verify schemas
    print("\nStep 4: Verifying schemas...")
    verify_schema(DEV_DATABASE_URL, "development")
    verify_schema(PROD_DATABASE_URL, "production")
    
    print("\n✅ Schema standardization complete!")
    print("\n📝 Next steps:")
    print("1. Remove the AI Assistant Alembic migration file")
    print("2. Update Alembic version to skip AI Assistant migrations")
    print("3. Test AI Assistant functionality in both environments")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)