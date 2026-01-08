#!/usr/bin/env python3
"""
AutoBoss Manual Upload Utility

This script provides a simple command-line interface for uploading
AutoBoss manuals to the AI Assistant knowledge base.

Usage:
    python upload_manual.py --file path/to/manual.pdf --version V4.0 --title "AutoBoss V4.0 Operator Manual"
"""

import argparse
import asyncio
import sys
from pathlib import Path
import json

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from app.knowledge_base import knowledge_base


async def upload_manual(
    file_path: str,
    title: str,
    version: str,
    document_type: str = "manual",
    language: str = "en"
):
    """Upload a manual to the knowledge base."""
    
    try:
        print(f"Uploading manual: {title}")
        print(f"File: {file_path}")
        print(f"Version: {version}")
        print(f"Type: {document_type}")
        print(f"Language: {language}")
        print("-" * 50)
        
        # Check if file exists
        if not Path(file_path).exists():
            print(f"❌ Error: File not found: {file_path}")
            return False
        
        # Prepare metadata
        metadata = {
            "uploaded_via": "upload_manual.py",
            "machine_version": version,
            "document_category": "official_manual"
        }
        
        # Upload the document
        document_id = await knowledge_base.add_document(
            file_path=file_path,
            title=title,
            document_type=document_type,
            version=version,
            language=language,
            metadata=metadata
        )
        
        print(f"✅ Successfully uploaded manual!")
        print(f"Document ID: {document_id}")
        
        # Get document info to confirm
        doc_info = await knowledge_base.get_document_info(document_id)
        if doc_info:
            print(f"Chunks created: {doc_info['chunk_count']}")
            print(f"Created at: {doc_info['created_at']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error uploading manual: {e}")
        return False


async def list_manuals():
    """List all manuals in the knowledge base."""
    
    try:
        print("📚 Manuals in Knowledge Base:")
        print("-" * 50)
        
        documents = await knowledge_base.list_documents(document_type="manual")
        
        if not documents:
            print("No manuals found in the knowledge base.")
            return
        
        for doc in documents:
            print(f"Title: {doc['title']}")
            print(f"Version: {doc.get('version', 'N/A')}")
            print(f"Language: {doc['language']}")
            print(f"Chunks: {doc['chunk_count']}")
            print(f"Created: {doc['created_at']}")
            print(f"ID: {doc['id']}")
            print("-" * 30)
        
        print(f"Total manuals: {len(documents)}")
        
    except Exception as e:
        print(f"❌ Error listing manuals: {e}")


async def test_search(query: str, version: str = None):
    """Test search functionality."""
    
    try:
        print(f"🔍 Searching for: '{query}'")
        if version:
            print(f"Version filter: {version}")
        print("-" * 50)
        
        results = await knowledge_base.search_documents(
            query=query,
            version=version,
            document_type="manual",
            limit=5,
            similarity_threshold=0.5
        )
        
        if not results:
            print("No results found.")
            return
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['document_title']} (v{result['version']})")
            print(f"   Similarity: {result['similarity']:.3f}")
            print(f"   Content: {result['content'][:150]}...")
            print()
        
        print(f"Found {len(results)} results")
        
    except Exception as e:
        print(f"❌ Error searching: {e}")


def main():
    """Main function."""
    
    parser = argparse.ArgumentParser(
        description="Upload AutoBoss manuals to the AI Assistant knowledge base"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a manual")
    upload_parser.add_argument("--file", required=True, help="Path to the manual file (PDF)")
    upload_parser.add_argument("--title", required=True, help="Title of the manual")
    upload_parser.add_argument("--version", required=True, help="AutoBoss version (e.g., V4.0, V3.1B)")
    upload_parser.add_argument("--type", default="manual", help="Document type (default: manual)")
    upload_parser.add_argument("--language", default="en", help="Language code (default: en)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all manuals")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Test search functionality")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--version", help="Filter by version")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Run the appropriate command
    if args.command == "upload":
        success = asyncio.run(upload_manual(
            file_path=args.file,
            title=args.title,
            version=args.version,
            document_type=args.type,
            language=args.language
        ))
        sys.exit(0 if success else 1)
        
    elif args.command == "list":
        asyncio.run(list_manuals())
        
    elif args.command == "search":
        asyncio.run(test_search(args.query, args.version))


if __name__ == "__main__":
    main()