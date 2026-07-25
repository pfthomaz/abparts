#!/usr/bin/env python3
"""
Compare development and production database schemas to ensure 100% match.

This script compares the core ABParts tables between dev and production
to verify they are identical after our schema standardization work.
"""

import sys
from sqlalchemy import create_engine, text
import subprocess

# Database connection strings
DEV_DATABASE_URL = "postgresql://abparts_user:abparts_pass@localhost:5433/abparts_dev"  # Docker port mapping

def get_table_schema(database_url, db_name):
    """Get table schema information using SQL queries."""
    print(f"📊 Getting schema info for {db_name}...")
    
    engine = create_engine(database_url)
    
    schema_info = {}
    
    try:
        with engine.connect() as conn:
            # Get all tables (excluding AI Assistant tables)
            tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name NOT IN ('knowledge_documents', 'document_chunks', 'knowledge_chunks')
            ORDER BY table_name;
            """
            
            result = conn.execute(text(tables_query))
            tables = [row[0] for row in result]
            
            print(f"  📋 Found {len(tables)} core tables")
            
            for table in tables:
                # Get column information
                columns_query = f"""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position;
                """
                
                result = conn.execute(text(columns_query))
                columns = []
                for row in result:
                    columns.append({
                        'name': row[0],
                        'type': row[1],
                        'nullable': row[2],
                        'default': row[3],
                        'max_length': row[4]
                    })
                
                schema_info[table] = {
                    'columns': columns,
                    'column_count': len(columns)
                }
            
    except Exception as e:
        print(f"  ❌ Error getting schema for {db_name}: {e}")
        return None
    
    finally:
        engine.dispose()
    
    return schema_info

def compare_schemas_detailed(dev_schema, prod_schema):
    """Compare schemas in detail and report differences."""
    print("\n🔍 Detailed Schema Comparison")
    print("-" * 40)
    
    differences = []
    
    # Compare table lists
    dev_tables = set(dev_schema.keys())
    prod_tables = set(prod_schema.keys())
    
    if dev_tables != prod_tables:
        differences.append("TABLE LIST MISMATCH:")
        if dev_tables - prod_tables:
            differences.append(f"  Tables only in DEV: {dev_tables - prod_tables}")
        if prod_tables - dev_tables:
            differences.append(f"  Tables only in PROD: {prod_tables - dev_tables}")
    
    # Compare common tables
    common_tables = dev_tables & prod_tables
    
    for table in sorted(common_tables):
        dev_table = dev_schema[table]
        prod_table = prod_schema[table]
        
        # Compare column count
        if dev_table['column_count'] != prod_table['column_count']:
            differences.append(f"Table {table}: Column count mismatch")
            differences.append(f"  DEV: {dev_table['column_count']} columns")
            differences.append(f"  PROD: {prod_table['column_count']} columns")
        
        # Compare columns
        dev_cols = {col['name']: col for col in dev_table['columns']}
        prod_cols = {col['name']: col for col in prod_table['columns']}
        
        dev_col_names = set(dev_cols.keys())
        prod_col_names = set(prod_cols.keys())
        
        if dev_col_names != prod_col_names:
            differences.append(f"Table {table}: Column name mismatch")
            if dev_col_names - prod_col_names:
                differences.append(f"  Columns only in DEV: {dev_col_names - prod_col_names}")
            if prod_col_names - dev_col_names:
                differences.append(f"  Columns only in PROD: {prod_col_names - dev_col_names}")
        
        # Compare column details for common columns
        common_cols = dev_col_names & prod_col_names
        for col_name in common_cols:
            dev_col = dev_cols[col_name]
            prod_col = prod_cols[col_name]
            
            if dev_col['type'] != prod_col['type']:
                differences.append(f"Table {table}.{col_name}: Type mismatch")
                differences.append(f"  DEV: {dev_col['type']}")
                differences.append(f"  PROD: {prod_col['type']}")
            
            if dev_col['nullable'] != prod_col['nullable']:
                differences.append(f"Table {table}.{col_name}: Nullable mismatch")
                differences.append(f"  DEV: {dev_col['nullable']}")
                differences.append(f"  PROD: {prod_col['nullable']}")
    
    return differences

def main():
    """Main comparison function."""
    print("🔍 Development vs Production Schema Comparison")
    print("=" * 55)
    print()
    
    # Get development schema
    dev_schema = get_table_schema(DEV_DATABASE_URL, "development")
    if not dev_schema:
        print("❌ Failed to get development schema")
        return False
    
    print(f"✅ Development schema loaded: {len(dev_schema)} tables")
    
    # For production comparison, we need to run this on production server
    print("\n📋 To compare with production, run this on production server:")
    print("=" * 55)
    print("# On production server:")
    print("python3 compare_dev_prod_schemas.py --production-only")
    print()
    print("# Or manually check key tables:")
    print("docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c \"\\dt\"")
    print()
    
    # Show development schema summary
    print("📊 Development Schema Summary:")
    print("-" * 30)
    
    total_columns = 0
    for table_name, table_info in sorted(dev_schema.items()):
        column_count = table_info['column_count']
        total_columns += column_count
        print(f"  {table_name:<25} {column_count:>3} columns")
    
    print(f"\n📈 Total: {len(dev_schema)} tables, {total_columns} columns")
    
    # Create a schema snapshot for comparison
    print("\n💾 Creating schema snapshot for production comparison...")
    
    snapshot = {
        'timestamp': '2025-01-09',
        'environment': 'development',
        'tables': dev_schema
    }
    
    with open('dev_schema_snapshot.json', 'w') as f:
        import json
        json.dump(snapshot, f, indent=2, default=str)
    
    print("  ✅ Schema snapshot saved to dev_schema_snapshot.json")
    
    print("\n✅ Development schema analysis complete!")
    print("\n📋 Next steps:")
    print("1. Copy this script to production server")
    print("2. Run schema comparison on production")
    print("3. If schemas match, proceed with migration reset")
    print("4. If schemas differ, apply standardization first")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--production-only":
        # This would be run on production server
        PROD_DATABASE_URL = "postgresql://abparts_user:abparts_pass@db:5432/abparts_prod"
        prod_schema = get_table_schema(PROD_DATABASE_URL, "production")
        if prod_schema:
            print(f"✅ Production schema loaded: {len(prod_schema)} tables")
            # Save production snapshot
            snapshot = {
                'timestamp': '2025-01-09',
                'environment': 'production',
                'tables': prod_schema
            }
            with open('prod_schema_snapshot.json', 'w') as f:
                import json
                json.dump(snapshot, f, indent=2, default=str)
            print("  ✅ Production schema snapshot saved")
    else:
        main()