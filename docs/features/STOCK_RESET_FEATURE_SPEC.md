# Stock Reset Feature Specification

## Overview
Allow users to reset/initialize warehouse inventory with a simple, intuitive interface that includes smart part search.

## UI Location
**Warehouses Page → Select Warehouse → "Stock Reset" Tab**

## User Flow

### 1. Navigate to Stock Reset
```
Warehouses → Click "Sparfish" → Stock Reset Tab
```

### 2. Stock Reset Interface

```
┌─────────────────────────────────────────────────────────────┐
│ Stock Reset: Sparfish Warehouse                             │
│                                                              │
│ ⚠️  WARNING: This will adjust all listed parts to the       │
│    specified quantities. Use for:                           │
│    • Initial warehouse setup                                │
│    • Physical stocktake corrections                         │
│    • System reconciliation                                  │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ 🔍 Add Part: [Search parts...              ] [Add]  │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ Current Stock Adjustments:                                  │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ Part Number │ Part Name        │ Current │ New │ Δ  │   │
│ ├─────────────┼──────────────────┼─────────┼─────┼────┤   │
│ │ WHC-005     │ Rotary union     │  10.000 │ [15]│ +5 │   │
│ │ ESE-011     │ Alternator belt  │   5.000 │ [3] │ -2 │   │
│ │ WHC-007     │ Ceramic jets     │   0.000 │ [25]│+25 │   │
│ │             │                  │         │     │    │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ Reason: [Dropdown ▼]                                        │
│   • Initial Stock Entry                                     │
│   • Physical Stocktake Correction                           │
│   • System Reconciliation                                   │
│   • Damaged Goods Write-off                                 │
│   • Other                                                   │
│                                                              │
│ Notes: [_____________________________________________]       │
│                                                              │
│ Summary:                                                     │
│ • 3 parts will be adjusted                                  │
│ • Total increase: 28 units                                  │
│ • Total decrease: 2 units                                   │
│                                                              │
│ [Cancel]  [Preview Changes]  [Apply Stock Reset]            │
└─────────────────────────────────────────────────────────────┘
```

### 3. Part Search Component
Reuse the `PartSearchSelector` component from part usage:
- Search by part number, name, description (all languages)
- Shows part image thumbnail
- Displays current stock in selected warehouse
- Click to add to adjustment list

### 4. Preview Modal
Before applying, show confirmation:
```
┌─────────────────────────────────────────┐
│ Confirm Stock Reset                     │
│                                         │
│ You are about to adjust 3 parts in     │
│ Sparfish warehouse:                     │
│                                         │
│ WHC-005: 10 → 15 (+5)                  │
│ ESE-011: 5 → 3 (-2)                    │
│ WHC-007: 0 → 25 (+25)                  │
│                                         │
│ Reason: Initial Stock Entry            │
│                                         │
│ This action will:                       │
│ ✓ Create adjustment transactions       │
│ ✓ Update inventory quantities           │
│ ✓ Log in audit trail                   │
│                                         │
│ [Cancel]  [Confirm Reset]               │
└─────────────────────────────────────────┘
```

## Backend Implementation

### 1. New Endpoint

```python
# backend/app/routers/warehouses.py

@router.post("/{warehouse_id}/stock-reset")
def reset_warehouse_stock(
    warehouse_id: str,
    reset_data: StockResetRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.WRITE))
):
    """
    Reset stock levels for multiple parts in a warehouse.
    Creates adjustment transactions for audit trail.
    """
    # Verify warehouse belongs to user's organization
    warehouse = db.query(models.Warehouse).filter(
        models.Warehouse.id == warehouse_id
    ).first()
    
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    if not permission_checker.is_super_admin(current_user):
        if warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    results = []
    
    for adjustment in reset_data.adjustments:
        # Get current inventory
        inventory = db.query(models.Inventory).filter(
            models.Inventory.warehouse_id == warehouse_id,
            models.Inventory.part_id == adjustment.part_id
        ).first()
        
        current_stock = inventory.current_stock if inventory else Decimal('0')
        difference = adjustment.new_quantity - current_stock
        
        if difference != 0:
            # Create adjustment transaction
            transaction = models.Transaction(
                transaction_type="adjustment",
                part_id=adjustment.part_id,
                to_warehouse_id=warehouse_id if difference > 0 else None,
                from_warehouse_id=warehouse_id if difference < 0 else None,
                quantity=abs(difference),
                unit_of_measure=adjustment.unit_of_measure,
                performed_by_user_id=current_user.user_id,
                transaction_date=datetime.now(),
                notes=f"Stock reset: {reset_data.reason}. {reset_data.notes or ''}",
                reference_number=f"RESET-{warehouse_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            db.add(transaction)
            
            # Update or create inventory
            if inventory:
                inventory.current_stock = adjustment.new_quantity
                inventory.last_updated = datetime.now()
            else:
                inventory = models.Inventory(
                    warehouse_id=warehouse_id,
                    part_id=adjustment.part_id,
                    current_stock=adjustment.new_quantity,
                    minimum_stock_recommendation=0,
                    unit_of_measure=adjustment.unit_of_measure
                )
                db.add(inventory)
            
            results.append({
                "part_id": adjustment.part_id,
                "old_quantity": float(current_stock),
                "new_quantity": float(adjustment.new_quantity),
                "difference": float(difference)
            })
    
    db.commit()
    
    return {
        "warehouse_id": warehouse_id,
        "adjustments_made": len(results),
        "details": results
    }
```

### 2. Schema

```python
# backend/app/schemas.py

class StockAdjustmentItem(BaseModel):
    part_id: uuid.UUID
    new_quantity: Decimal
    unit_of_measure: str

class StockResetRequest(BaseModel):
    adjustments: List[StockAdjustmentItem]
    reason: str = Field(..., max_length=100)
    notes: Optional[str] = None
```

## Frontend Implementation

### 1. New Component: StockResetTab

```javascript
// frontend/src/components/StockResetTab.js

import React, { useState, useEffect } from 'react';
import PartSearchSelector from './PartSearchSelector';

const StockResetTab = ({ warehouse, onClose }) => {
  const [adjustments, setAdjustments] = useState([]);
  const [reason, setReason] = useState('Initial Stock Entry');
  const [notes, setNotes] = useState('');
  const [showPreview, setShowPreview] = useState(false);

  // Load current inventory for this warehouse
  useEffect(() => {
    fetchWarehouseInventory(warehouse.id).then(inventory => {
      setAdjustments(inventory.map(item => ({
        part_id: item.part_id,
        part_number: item.part_number,
        part_name: item.part_name,
        current_quantity: item.current_stock,
        new_quantity: item.current_stock,
        unit_of_measure: item.unit_of_measure
      })));
    });
  }, [warehouse.id]);

  const handleAddPart = (part) => {
    // Check if part already in list
    if (adjustments.find(a => a.part_id === part.id)) {
      alert('Part already in list');
      return;
    }
    
    setAdjustments([...adjustments, {
      part_id: part.id,
      part_number: part.part_number,
      part_name: part.name,
      current_quantity: 0, // Will be fetched from inventory
      new_quantity: 0,
      unit_of_measure: part.unit_of_measure
    }]);
  };

  const handleQuantityChange = (partId, newQty) => {
    setAdjustments(adjustments.map(adj =>
      adj.part_id === partId ? { ...adj, new_quantity: parseFloat(newQty) } : adj
    ));
  };

  const handleSubmit = async () => {
    // Filter only changed quantities
    const changes = adjustments.filter(
      adj => adj.new_quantity !== adj.current_quantity
    );
    
    if (changes.length === 0) {
      alert('No changes to apply');
      return;
    }

    try {
      await warehousesService.resetStock(warehouse.id, {
        adjustments: changes.map(adj => ({
          part_id: adj.part_id,
          new_quantity: adj.new_quantity,
          unit_of_measure: adj.unit_of_measure
        })),
        reason,
        notes
      });
      
      alert('Stock reset successful!');
      onClose();
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  return (
    <div className="p-6">
      {/* Warning banner */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-yellow-700">
              <strong>Warning:</strong> This will adjust inventory quantities. Use for initial setup, stocktake corrections, or system reconciliation.
            </p>
          </div>
        </div>
      </div>

      {/* Part search */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Add Part to Adjustment List
        </label>
        <PartSearchSelector
          onSelect={handleAddPart}
          placeholder="Search by part number, name, or description..."
        />
      </div>

      {/* Adjustments table */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-3">Stock Adjustments</h3>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Part Number</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Part Name</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Current</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">New</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Δ</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {adjustments.map(adj => {
              const diff = adj.new_quantity - adj.current_quantity;
              return (
                <tr key={adj.part_id}>
                  <td className="px-4 py-2 text-sm">{adj.part_number}</td>
                  <td className="px-4 py-2 text-sm">{adj.part_name}</td>
                  <td className="px-4 py-2 text-sm text-right">{adj.current_quantity.toFixed(3)}</td>
                  <td className="px-4 py-2">
                    <input
                      type="number"
                      step="0.001"
                      value={adj.new_quantity}
                      onChange={(e) => handleQuantityChange(adj.part_id, e.target.value)}
                      className="w-24 px-2 py-1 border rounded text-right"
                    />
                  </td>
                  <td className={`px-4 py-2 text-sm text-right font-medium ${
                    diff > 0 ? 'text-green-600' : diff < 0 ? 'text-red-600' : 'text-gray-500'
                  }`}>
                    {diff > 0 ? '+' : ''}{diff.toFixed(3)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Reason and notes */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Reason</label>
          <select
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full px-3 py-2 border rounded"
          >
            <option>Initial Stock Entry</option>
            <option>Physical Stocktake Correction</option>
            <option>System Reconciliation</option>
            <option>Damaged Goods Write-off</option>
            <option>Other</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full px-3 py-2 border rounded"
            placeholder="Optional notes..."
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-3">
        <button
          onClick={onClose}
          className="px-4 py-2 border rounded text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          onClick={() => setShowPreview(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Preview Changes
        </button>
        <button
          onClick={handleSubmit}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Apply Stock Reset
        </button>
      </div>
    </div>
  );
};

export default StockResetTab;
```

## Benefits

1. **Intuitive**: Users work within warehouse context
2. **Flexible**: Can add any part, not just existing inventory
3. **Safe**: Preview before applying, clear warnings
4. **Auditable**: All changes create transactions
5. **Reusable**: Leverages existing PartSearchSelector component

## Next Steps

1. Merge Inventory page into Warehouses
2. Implement Stock Reset tab
3. Add transaction history tab
4. Test with real data

Would you like me to start implementing this?
