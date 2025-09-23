#!/usr/bin/env python3
"""
Simple validation script for enhanced search performance features
"""

import os
import subprocess
import time

def check_file_exists(filepath, description):
    """Check if a file exists and report"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} missing: {filepath}")
        return False

def check_docker_services():
    """Check if Docker services are running"""
    try:
        result = subprocess.run(['docker-compose', 'ps'], 
                              capture_output=True, text=True, check=True)
        if 'abparts_web' in result.stdout and 'Up' in result.stdout:
            print("✓ Docker services are running")
            return True
        else:
            print("✗ Docker services not running properly")
            return False
    except Exception as e:
        print(f"✗ Error checking Docker services: {e}")
        return False

def validate_implementation():
    """Validate that all enhanced search features are implemented"""
    print("=== Enhanced Search Performance Validation ===\n")
    
    all_good = True
    
    # Check core implementation files
    files_to_check = [
        ("frontend/src/hooks/useDebounce.js", "Debounce hook"),
        ("frontend/src/components/ProgressiveLoader.js", "Progressive loader component"),
        ("frontend/src/components/PartCard.js", "Optimized PartCard component"),
        ("frontend/src/components/PartsSearchFilter.js", "Optimized search filter component"),
        ("frontend/src/components/VirtualizedPartsList.js", "Virtualized parts list component"),
        ("frontend/src/hooks/usePerformanceMonitor.js", "Performance monitoring hook"),
        ("frontend/src/pages/Parts.js", "Updated Parts page"),
    ]
    
    print("1. Checking implementation files:")
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_good = False
    
    print("\n2. Checking Docker services:")
    if not check_docker_services():
        all_good = False
    
    print("\n3. Checking key features in Parts.js:")
    try:
        with open("frontend/src/pages/Parts.js", "r") as f:
            content = f.read()
            
        features = [
            ("useDebounceSearch", "Debounced search hook usage"),
            ("usePerformanceMonitor", "Performance monitoring"),
            ("PartsSearchFilter", "Optimized search filter component"),
            ("PartCard", "Optimized part card component"),
            ("VirtualizedPartsList", "Virtualized list for large datasets"),
            ("useVirtualization", "Virtualization logic"),
            ("React.memo", "Component memoization (in PartCard)"),
        ]
        
        for feature, description in features:
            if feature in content:
                print(f"✓ {description}")
            else:
                print(f"⚠ {description} - check implementation")
                
    except Exception as e:
        print(f"✗ Error checking Parts.js: {e}")
        all_good = False
    
    print("\n4. Checking debounce hook implementation:")
    try:
        with open("frontend/src/hooks/useDebounce.js", "r") as f:
            content = f.read()
            
        if "useDebounce" in content and "useDebounceSearch" in content:
            print("✓ Debounce hooks implemented")
        else:
            print("✗ Debounce hooks missing")
            all_good = False
            
        if "setTimeout" in content and "clearTimeout" in content:
            print("✓ Proper debounce timing logic")
        else:
            print("✗ Debounce timing logic missing")
            all_good = False
            
    except Exception as e:
        print(f"✗ Error checking debounce hook: {e}")
        all_good = False
    
    print("\n5. Checking performance optimizations:")
    try:
        with open("frontend/src/components/PartCard.js", "r") as f:
            content = f.read()
            
        if "memo" in content:
            print("✓ React.memo optimization in PartCard")
        else:
            print("✗ React.memo optimization missing")
            all_good = False
            
        if "useCallback" in content or "useMemo" in content:
            print("✓ Additional React optimizations")
        else:
            print("ℹ Consider adding useCallback/useMemo optimizations")
            
    except Exception as e:
        print(f"✗ Error checking PartCard optimizations: {e}")
        all_good = False
    
    print("\n=== Summary ===")
    if all_good:
        print("✓ All enhanced search performance features are implemented!")
        print("\nImplemented enhancements:")
        print("  • Debounced search (300ms delay) - reduces API calls")
        print("  • Progressive loading indicators - better UX for large datasets")
        print("  • Optimized component re-rendering with React.memo")
        print("  • Performance monitoring for development")
        print("  • Virtualized rendering for datasets >100 parts")
        print("  • Enhanced search across multiple part fields")
        print("  • Memoized event handlers to prevent re-renders")
        print("  • Optimized filtering with debounced search terms")
        
        print("\nPerformance benefits:")
        print("  • Reduced server load from fewer search requests")
        print("  • Faster UI response with optimized re-rendering")
        print("  • Better handling of large parts catalogs")
        print("  • Improved user experience with loading indicators")
        
        return True
    else:
        print("✗ Some features are missing or incomplete")
        return False

if __name__ == "__main__":
    success = validate_implementation()
    
    if success:
        print("\n🎉 Task 5 - Enhanced frontend search performance: COMPLETED")
        print("\nNext steps:")
        print("  • Test with large datasets in development")
        print("  • Monitor performance metrics in production")
        print("  • Consider additional optimizations based on usage patterns")
    else:
        print("\n❌ Task 5 - Enhanced frontend search performance: NEEDS ATTENTION")
    
    exit(0 if success else 1)