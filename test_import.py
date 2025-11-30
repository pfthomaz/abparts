#!/usr/bin/env python3
"""Test if StockAdjustmentListResponse can be imported"""

import sys
sys.path.insert(0, 'backend')

try:
    from app.schemas import StockAdjustmentListResponse
    print("✅ SUCCESS: StockAdjustmentListResponse imported successfully")
    print(f"   Class: {StockAdjustmentListResponse}")
    print(f"   Fields: {StockAdjustmentListResponse.__fields__.keys()}")
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
except AttributeError as e:
    print(f"❌ ATTRIBUTE ERROR: {e}")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
