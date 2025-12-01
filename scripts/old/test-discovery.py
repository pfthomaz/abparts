#!/usr/bin/env python3
"""
Test discovery script for Kiro IDE
This script provides test discovery without requiring full Docker setup
"""

import sys
import os
import re
from pathlib import Path

def setup_minimal_env():
    """Set up minimal environment for test discovery"""
    os.environ.update({
        'DATABASE_URL': 'sqlite:///./test_discovery.db',
        'REDIS_URL': 'redis://localhost:6379/0',
        'ENVIRONMENT': 'test_discovery',
        'TESTING': 'true',
        'SECRET_KEY': 'test-secret-key-for-discovery-only',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '30',
        'SMTP_SERVER': 'smtp.example.com',
        'SMTP_PORT': '587',
        'SMTP_USERNAME': 'test@example.com',
        'SMTP_PASSWORD': 'test_password',
        'FROM_EMAIL': 'test@abparts.com',
        'BASE_URL': 'http://localhost:8000',
        'SKIP_DB_INIT': 'true'
    })

def parse_test_file(file_path):
    """Parse a test file to extract test names"""
    tests = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find class definitions
        class_pattern = r'class (Test\w+):'
        classes = re.findall(class_pattern, content)
        
        # Find test method definitions
        method_pattern = r'def (test_\w+)\('
        methods = re.findall(method_pattern, content)
        
        # Simple approach: combine classes and methods
        current_class = None
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('class Test') and line.endswith(':'):
                current_class = line.split()[1].rstrip(':')
            elif line.startswith('def test_') and current_class:
                method_name = line.split('(')[0].replace('def ', '')
                test_name = f"{file_path}::{current_class}::{method_name}"
                tests.append(test_name)
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
    
    return tests

def main():
    """Main test discovery function"""
    setup_minimal_env()
    
    # Check if we're in collect-only mode
    if '--collect-only' in sys.argv and '-q' in sys.argv:
        # Find test files to process
        test_files = []
        for arg in sys.argv:
            if arg.endswith('.py') and 'test_' in arg:
                test_files.append(arg)
        
        if not test_files:
            # Default to all test files in backend/tests
            test_dir = Path('backend/tests')
            if test_dir.exists():
                test_files = list(test_dir.glob('test_*.py'))
        
        # Parse and output test names
        all_tests = []
        for test_file in test_files:
            tests = parse_test_file(test_file)
            all_tests.extend(tests)
        
        for test in all_tests:
            print(test)
        
        return 0
    
    else:
        print("Usage: python test-discovery.py --collect-only -q [test_file.py]")
        return 1

if __name__ == "__main__":
    sys.exit(main())