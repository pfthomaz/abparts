#!/usr/bin/env python3
"""
Sync production database schema to development environment.

This script helps maintain consistency between production and development
by creating the necessary AI Assistant tables in the development database.
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Database connection strings
DEV_DATABASE_URL = "postgresql://abparts_user:abparts_pass@localhost:5432/abparts_dev"
PROD_DATABASE_URL = "postgresql://abparts_user:abparts_pass@localhost:5432/abparts_prod"

def create_ai_assistant_tables(database_url: str, environment: str):
    """Create AI Assistant knowledge base tables."""
    print(f"Creating AI Assistant tables in {environment} database...")
    
    engine = create_engine(database_url)
    
    # SQL to create the tables
    create_tables_sql = """
    -- Create knowledge_documents table
    CREATE TABLE IF NOT EXISTS knowledge_documents (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        title VARCHAR(255) NOT NULL,
        document_type VARCHAR(50) NOT NULL,
        language VARCHAR(10) NOT NULL DEFAULT 'en',
        version VARCHAR(20) NOT NULL DEFAULT '1.0',
        file_path VARCHAR(500),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        machine_models TEXT[] DEFAULT '{}',
        tags TEXT[] DEFAULT '{}',
        document_metadata JSONB DEFAULT '{}',
        chunk_count INTEGER DEFAULT 0
    );

    -- Create document_chunks table
    CREATE TABLE IF NOT EXISTS document_chunks (
        id VARCHAR(255) PRIMARY KEY,
        document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
        chunk_index INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_knowledge_documents_type ON knowledge_documents(document_type);
    CREATE INDEX IF NOT EXISTS idx_knowledge_documents_language ON knowledge_documents(language);
    CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
    """
    
    try:
        with engine.connect() as conn:
            # Execute each statement
            for statement in create_tables_sql.split(';'):
                statement = statement.strip()
                if statement:
                    conn.execute(text(statement))
                    conn.commit()
        
        print(f"✅ AI Assistant tables created successfully in {environment}")
        
    except Exception as e:
        print(f"❌ Error creating tables in {environment}: {e}")
        return False
    
    finally:
        engine.dispose()
    
    return True

def main():
    """Main function to sync schema."""
    print("🔄 Syncing AI Assistant schema from production to development...")
    
    # Check if we're in development mode
    if len(sys.argv) > 1 and sys.argv[1] == "--dev":
        print("Creating tables in development database...")
        success = create_ai_assistant_tables(DEV_DATABASE_URL, "development")
    else:
        print("Usage: python sync_production_schema.py --dev")
        print("This will create AI Assistant tables in your development database.")
        return
    
    if success:
        print("\n✅ Schema sync completed successfully!")
        print("📝 Next steps:")
        print("1. Run: docker-compose up -d db")
        print("2. Run: docker-compose exec api alembic upgrade head")
        print("3. Test AI Assistant locally: docker-compose up ai_assistant")
    else:
        print("\n❌ Schema sync failed!")

if __name__ == "__main__":
    main()