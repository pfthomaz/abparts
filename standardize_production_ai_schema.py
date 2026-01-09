#!/usr/bin/env python3
"""
Standardize AI Assistant Schema - Production Server

This script should be run ON THE PRODUCTION SERVER to update the production
AI Assistant schema to match the development standard.
"""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Production database connection (run this ON production server)
PROD_DATABASE_URL = "postgresql://abparts_user:abparts_pass@localhost:5432/abparts_prod"

def get_standard_schema_sql():
    """Get the standard AI Assistant schema SQL."""
    return """
    -- Drop existing tables if they exist (in correct order due to foreign keys)
    DROP TABLE IF EXISTS document_chunks CASCADE;
    DROP TABLE IF EXISTS knowledge_documents CASCADE;
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
    """

def get_trigger_sql():
    """Get the trigger SQL."""
    return """
    -- Create trigger function for updated_at
    CREATE OR REPLACE FUNCTION update_knowledge_document_updated_at()
    RETURNS trigger AS $function$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $function$ LANGUAGE plpgsql;
    
    -- Create trigger
    CREATE TRIGGER trigger_update_knowledge_document_updated_at
        BEFORE UPDATE ON knowledge_documents
        FOR EACH ROW
        EXECUTE FUNCTION update_knowledge_document_updated_at();
    """

def backup_production_data():
    """Backup existing production AI Assistant data."""
    print("📦 Backing up existing production AI Assistant data...")
    
    engine = create_engine(PROD_DATABASE_URL)
    backup_data = {
        'knowledge_documents': [],
        'document_chunks': [],
        'knowledge_chunks': []  # Old production table name
    }
    
    try:
        with engine.connect() as conn:
            # Backup knowledge_documents (if exists)
            try:
                result = conn.execute(text("SELECT * FROM knowledge_documents"))
                backup_data['knowledge_documents'] = [dict(row._mapping) for row in result]
                print(f"  ✅ Backed up {len(backup_data['knowledge_documents'])} knowledge documents")
            except Exception as e:
                print(f"  ⚠️  No knowledge_documents table: {e}")
            
            # Backup document_chunks (if exists)
            try:
                result = conn.execute(text("SELECT * FROM document_chunks"))
                backup_data['document_chunks'] = [dict(row._mapping) for row in result]
                print(f"  ✅ Backed up {len(backup_data['document_chunks'])} document chunks")
            except Exception as e:
                print(f"  ⚠️  No document_chunks table: {e}")
            
            # Backup knowledge_chunks (old production table)
            try:
                result = conn.execute(text("SELECT * FROM knowledge_chunks"))
                backup_data['knowledge_chunks'] = [dict(row._mapping) for row in result]
                print(f"  ✅ Backed up {len(backup_data['knowledge_chunks'])} knowledge chunks (old format)")
            except Exception as e:
                print(f"  ⚠️  No knowledge_chunks table: {e}")
                
    except Exception as e:
        print(f"  ❌ Error during backup: {e}")
        return None
    
    finally:
        engine.dispose()
    
    return backup_data

def restore_production_data(backup_data):
    """Restore backed up data to the new schema."""
    if not backup_data:
        print("  ⚠️  No data to restore")
        return True
    
    print("📥 Restoring data to new schema...")
    
    engine = create_engine(PROD_DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Restore knowledge_documents
            docs_to_restore = backup_data.get('knowledge_documents', [])
            for doc in docs_to_restore:
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
                    'id': str(doc['id']),
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
            
            if docs_to_restore:
                print(f"  ✅ Restored {len(docs_to_restore)} knowledge documents")
            
            # Restore document_chunks (from document_chunks backup)
            chunks_to_restore = backup_data.get('document_chunks', [])
            for chunk in chunks_to_restore:
                insert_sql = """
                INSERT INTO document_chunks (
                    id, document_id, chunk_index, content, embedding, created_at
                ) VALUES (
                    :id, :document_id, :chunk_index, :content, :embedding, :created_at
                )
                """
                
                conn.execute(text(insert_sql), {
                    'id': str(chunk['id']),
                    'document_id': str(chunk['document_id']),
                    'chunk_index': chunk.get('chunk_index'),
                    'content': chunk.get('content'),
                    'embedding': chunk.get('embedding'),
                    'created_at': chunk.get('created_at')
                })
            
            # Also restore from knowledge_chunks (old production format)
            old_chunks = backup_data.get('knowledge_chunks', [])
            for chunk in old_chunks:
                # Convert old format to new format
                chunk_id = f"{chunk['document_id']}_chunk_{chunk['chunk_index']}"
                
                insert_sql = """
                INSERT INTO document_chunks (
                    id, document_id, chunk_index, content, embedding, created_at
                ) VALUES (
                    :id, :document_id, :chunk_index, :content, :embedding, :created_at
                )
                """
                
                conn.execute(text(insert_sql), {
                    'id': chunk_id,
                    'document_id': str(chunk['document_id']),
                    'chunk_index': chunk.get('chunk_index'),
                    'content': chunk.get('content'),
                    'embedding': None,  # Will need to be regenerated
                    'created_at': chunk.get('created_at')
                })
            
            total_chunks = len(chunks_to_restore) + len(old_chunks)
            if total_chunks > 0:
                print(f"  ✅ Restored {total_chunks} document chunks")
            
            conn.commit()
            
    except Exception as e:
        print(f"  ❌ Error during restore: {e}")
        return False
    
    finally:
        engine.dispose()
    
    return True

def apply_schema():
    """Apply the standard schema to production."""
    print("🔧 Applying standard AI Assistant schema to production...")
    
    engine = create_engine(PROD_DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Execute the main schema SQL
            schema_sql = get_standard_schema_sql()
            
            # Split and execute each statement
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                try:
                    conn.execute(text(statement))
                    conn.commit()
                except Exception as e:
                    print(f"  ⚠️  Statement warning: {e}")
            
            # Execute trigger SQL separately
            trigger_sql = get_trigger_sql()
            try:
                conn.execute(text(trigger_sql))
                conn.commit()
                print(f"  ✅ Trigger created successfully")
            except Exception as e:
                print(f"  ⚠️  Trigger creation warning: {e}")
                
        print(f"  ✅ Standard schema applied to production")
        return True
        
    except Exception as e:
        print(f"  ❌ Error applying schema: {e}")
        return False
    
    finally:
        engine.dispose()

def verify_schema():
    """Verify the schema is correct."""
    print("🔍 Verifying production schema...")
    
    engine = create_engine(PROD_DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check data
            result = conn.execute(text("SELECT COUNT(*) FROM knowledge_documents"))
            doc_count = result.scalar()
            
            result = conn.execute(text("SELECT COUNT(*) FROM document_chunks"))
            chunk_count = result.scalar()
            
            print(f"  ✅ Data: {doc_count} documents, {chunk_count} chunks")
            
            # Check key fields exist
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'document_chunks' AND column_name = 'embedding'
            """))
            
            if result.fetchone():
                print(f"  ✅ Embedding field exists in document_chunks")
            else:
                print(f"  ❌ Embedding field missing!")
            
    except Exception as e:
        print(f"  ❌ Error verifying schema: {e}")
        return False
    
    finally:
        engine.dispose()
    
    return True

def main():
    """Main function."""
    print("🔄 Standardizing AI Assistant Schema - Production Server")
    print("=" * 55)
    print("⚠️  This script should be run ON THE PRODUCTION SERVER")
    print()
    
    # Step 1: Backup existing data
    print("Step 1: Backing up existing data...")
    backup_data = backup_production_data()
    
    # Step 2: Apply standard schema
    print("\nStep 2: Applying standard schema...")
    if not apply_schema():
        print("❌ Schema application failed!")
        return False
    
    # Step 3: Restore data
    print("\nStep 3: Restoring data...")
    if not restore_production_data(backup_data):
        print("❌ Data restore failed!")
        return False
    
    # Step 4: Verify schema
    print("\nStep 4: Verifying schema...")
    verify_schema()
    
    print("\n✅ Production schema standardization complete!")
    print("\n📝 Next steps:")
    print("1. Restart AI Assistant service: docker compose -f docker-compose.prod.yml restart ai_assistant")
    print("2. Test AI Assistant functionality")
    print("3. Regenerate embeddings if needed")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)