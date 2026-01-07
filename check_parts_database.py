#!/usr/bin/env python3
"""
Check what's actually in the parts database table
"""

import psycopg2
import json
from datetime import datetime

def connect_to_db():
    """Connect to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="abparts_dev",
            user="abparts_user",
            password="abparts_pass"
        )
        return conn
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return None

def check_parts_table():
    """Check the parts table directly"""
    conn = connect_to_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check table structure
        print("=== Parts Table Structure ===")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'parts' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        for col_name, data_type, nullable in columns:
            print(f"  {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")
        
        print()
        
        # Check recent parts
        print("=== Recent Parts (Last 10) ===")
        cursor.execute("""
            SELECT id, part_number, name, image_urls, 
                   CASE WHEN image_data IS NOT NULL THEN array_length(image_data, 1) ELSE 0 END as image_data_count,
                   created_at
            FROM parts 
            ORDER BY created_at DESC 
            LIMIT 10;
        """)
        
        parts = cursor.fetchall()
        
        if not parts:
            print("❌ No parts found in database!")
        else:
            for part_id, part_number, name, image_urls, image_data_count, created_at in parts:
                print(f"\n📦 Part: {part_number}")
                print(f"   ID: {part_id}")
                print(f"   Name: {name}")
                print(f"   Image URLs: {len(image_urls) if image_urls else 0} URLs")
                print(f"   Image Data: {image_data_count or 0} binary images")
                print(f"   Created: {created_at}")
                
                if image_urls:
                    print(f"   First URL: {image_urls[0][:50]}..." if image_urls[0] else "   Empty URL")
        
        print()
        
        # Check parts with images specifically
        print("=== Parts with Images ===")
        cursor.execute("""
            SELECT part_number, name, 
                   array_length(image_urls, 1) as url_count,
                   array_length(image_data, 1) as data_count
            FROM parts 
            WHERE image_urls IS NOT NULL AND array_length(image_urls, 1) > 0
               OR image_data IS NOT NULL AND array_length(image_data, 1) > 0
            ORDER BY created_at DESC;
        """)
        
        parts_with_images = cursor.fetchall()
        
        if not parts_with_images:
            print("❌ No parts with images found!")
        else:
            print(f"✅ Found {len(parts_with_images)} parts with images:")
            for part_number, name, url_count, data_count in parts_with_images:
                print(f"  📷 {part_number}: {name}")
                print(f"     URLs: {url_count or 0}, Data: {data_count or 0}")
        
        cursor.close()
        
    except Exception as e:
        print(f"✗ Database query failed: {e}")
    finally:
        conn.close()

def check_recent_api_activity():
    """Check if there are any recent parts created via API"""
    conn = connect_to_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        print("\n=== Recent API Activity (Last Hour) ===")
        cursor.execute("""
            SELECT part_number, name, created_at
            FROM parts 
            WHERE created_at > NOW() - INTERVAL '1 hour'
            ORDER BY created_at DESC;
        """)
        
        recent_parts = cursor.fetchall()
        
        if not recent_parts:
            print("❌ No parts created in the last hour")
        else:
            print(f"✅ Found {len(recent_parts)} parts created in the last hour:")
            for part_number, name, created_at in recent_parts:
                print(f"  🆕 {part_number}: {name} (created: {created_at})")
        
        cursor.close()
        
    except Exception as e:
        print(f"✗ Recent activity query failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== Checking Parts Database ===")
    print()
    
    check_parts_table()
    check_recent_api_activity()
    
    print("\n=== Database Check Complete ===")