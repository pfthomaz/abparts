#!/usr/bin/env python3
"""
Knowledge Base Setup Script

This script sets up the knowledge base tables and prepares the system
for document uploads.
"""

import asyncio
import sys
from pathlib import Path
import subprocess
import os

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from app.database import get_db_session
from app.config import settings


async def setup_database():
    """Set up the knowledge base database tables."""
    
    try:
        print("🔧 Setting up Knowledge Base database...")
        print("-" * 50)
        
        # Read the SQL script
        sql_file = Path(__file__).parent / "create_knowledge_base_tables.sql"
        
        if not sql_file.exists():
            print(f"❌ SQL script not found: {sql_file}")
            return False
        
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        # Execute the SQL script
        with get_db_session() as db:
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    try:
                        db.execute(statement)
                        print(f"✅ Executed: {statement[:50]}...")
                    except Exception as e:
                        print(f"⚠️  Warning: {e}")
                        # Continue with other statements
        
        print("✅ Database setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    
    print("📦 Checking dependencies...")
    print("-" * 50)
    
    required_packages = [
        "fastapi",
        "sqlalchemy",
        "psycopg2",
        "openai",
        "numpy",
        "PyPDF2"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True


def check_configuration():
    """Check if the configuration is correct."""
    
    print("⚙️  Checking configuration...")
    print("-" * 50)
    
    # Check OpenAI API key
    if settings.OPENAI_API_KEY:
        print("✅ OpenAI API key configured")
    else:
        print("⚠️  OpenAI API key not configured")
        print("   Set OPENAI_API_KEY environment variable")
    
    # Check database URL
    if settings.DATABASE_URL:
        print("✅ Database URL configured")
    else:
        print("⚠️  Database URL not configured")
        print("   Set DATABASE_URL environment variable")
    
    return True


async def test_knowledge_base():
    """Test the knowledge base functionality."""
    
    print("🧪 Testing Knowledge Base...")
    print("-" * 50)
    
    try:
        from app.knowledge_base import knowledge_base
        
        # Test listing documents
        documents = await knowledge_base.list_documents()
        print(f"✅ Found {len(documents)} documents in knowledge base")
        
        # Test search (should work even with no documents)
        results = await knowledge_base.search_documents(
            query="test query",
            limit=1,
            similarity_threshold=0.5
        )
        print(f"✅ Search functionality working (found {len(results)} results)")
        
        return True
        
    except Exception as e:
        print(f"❌ Knowledge base test failed: {e}")
        return False


def print_usage_instructions():
    """Print usage instructions."""
    
    print("\n" + "=" * 60)
    print("📖 KNOWLEDGE BASE SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print("1. Upload your AutoBoss manuals:")
    print("   python upload_manual.py upload \\")
    print("     --file /path/to/AutoBoss_V4.0_Manual.pdf \\")
    print("     --title 'AutoBoss V4.0 Operator Manual' \\")
    print("     --version V4.0")
    print()
    print("   python upload_manual.py upload \\")
    print("     --file /path/to/AutoBoss_V3.1B_Manual.pdf \\")
    print("     --title 'AutoBoss V3.1B Operator Manual' \\")
    print("     --version V3.1B")
    print()
    print("2. List uploaded manuals:")
    print("   python upload_manual.py list")
    print()
    print("3. Test search functionality:")
    print("   python upload_manual.py search --query 'troubleshooting' --version V4.0")
    print()
    print("4. Start the AI Assistant service:")
    print("   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
    print()
    print("5. Access the API documentation:")
    print("   http://localhost:8001/docs")
    print()


async def main():
    """Main setup function."""
    
    print("🚀 AutoBoss AI Assistant - Knowledge Base Setup")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup failed: Missing dependencies")
        sys.exit(1)
    
    print()
    
    # Check configuration
    check_configuration()
    print()
    
    # Setup database
    if not await setup_database():
        print("\n❌ Setup failed: Database setup error")
        sys.exit(1)
    
    print()
    
    # Test knowledge base
    if not await test_knowledge_base():
        print("\n❌ Setup failed: Knowledge base test error")
        sys.exit(1)
    
    # Print usage instructions
    print_usage_instructions()


if __name__ == "__main__":
    asyncio.run(main())