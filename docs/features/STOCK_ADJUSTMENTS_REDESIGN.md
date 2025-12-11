# Stock Adjustments System Redesign

## Current Problems

1. **Two redundant tables:**
   - `inventory_adjustments` - Empty, not used
   - `stock_adjustments` - Has 3 old records (>2 months), not actively used

2. **No item-level tracking:**
   - Can't see which parts were adjusted
   - Can't see adjustment quantities per part

3. **Adjustment history not showing:**
   - Frontend shows empty list
   - No connection between adjustments and display

## Proposed Solution

### Database Structure

#### Keep: `stock_adjustments` (Header table)
```sql
stock_adjustments:
  - id (UUID, PK)
  - warehouse_id (UUID, FK to warehouses)
  - adjustment_type (ENUM: 'manual', 'correction', 'damage', 'loss', 'found', 'other')
  - reason (TEXT) - Why the adjustment was made
  - notes (TEXT) - Additional details
  - adjusted_by_user_id (UUID, FK to users) - Who made the adjustment
  - adjustment_date (TIMESTAMP) - When it was made
  - created_at (TIMESTAMP)
  - updated_at (TIMESTAMP)
```

#### Create: `stock_adjustment_items` (Line items table)
```sql
stock_adjustment_items:
  - id (UUID, PK)
  - stock_adjustment_id (UUID, FK to stock_adjustments)
  - part_id (UUID, FK to parts)
  - quantity_before (DECIMAL) - Quantity before adjustment
  - quantity_after (DECIMAL) - Quantity after adjustment
  - quantity_change (DECIMAL) - The adjustment amount (+/-)
  - reason (TEXT) - Specific reason for this part
  - created_at (TIMESTAMP)
```

#### Remove: `inventory_adjustments`
- Drop table completely
- Remove all related code

### Adjustment Types

1. **manual** - Manual stock count correction
2. **correction** - Error correction
3. **damage** - Damaged goods write-off
4. **loss** - Lost/stolen items
5. **found** - Found items (increase)
6. **other** - Other reasons

### Workflow

1. **User initiates adjustment** in Warehouse → Stock Adjustments tab
2. **Selects parts** and enters new quantities
3. **System calculates** quantity_change for each part
4. **Records adjustment** in both tables:
   - Header in `stock_adjustments`
   - Line items in `stock_adjustment_items`
5. **Updates inventory** in `inventory` table
6. **Creates transaction** in `transactions` table for audit trail
7. **Displays history** in Adjustment History list

## Implementation Steps

### Phase 1: Database Changes

1. Create migration to:
   - Add `stock_adjustment_items` table
   - Update `stock_adjustments` table structure
   - Drop `inventory_adjustments` table

### Phase 2: Backend Changes

1. Update models:
   - Remove `InventoryAdjustment` model
   - Update `StockAdjustment` model
   - Create `StockAdjustmentItem` model

2. Update schemas:
   - Create adjustment request/response schemas
   - Include item-level details

3. Update routers:
   - Remove inventory_adjustments endpoints
   - Update stock_adjustments endpoints
   - Add item-level operations

4. Update CRUD operations:
   - Create adjustment with items
   - Update inventory quantities
   - Create transaction records

### Phase 3: Frontend Changes

1. Update StockResetTab component:
   - Show adjustment history
   - Display item-level details
   - Add adjustment type selection

2. Create adjustment form:
   - Select multiple parts
   - Enter new quantities
   - Add reason/notes

3. Display adjustment history:
   - List all adjustments
   - Show details per adjustment
   - Filter by date/type

## Data Flow

```
User Action → Frontend Form
    ↓
POST /api/stock-adjustments
    ↓
Backend validates & processes:
  1. Create stock_adjustments record
  2. Create stock_adjustment_items records
  3. Update inventory quantities
  4. Create transaction records
    ↓
Return adjustment details
    ↓
Frontend refreshes & shows in history
```

## Example Adjustment

**Scenario:** Physical count found discrepancies

```json
{
  "warehouse_id": "uuid",
  "adjustment_type": "manual",
  "reason": "Physical inventory count - Q4 2024",
  "notes": "Annual stocktake",
  "items": [
    {
      "part_id": "part-uuid-1",
      "quantity_before": 100,
      "quantity_after": 95,
      "quantity_change": -5,
      "reason": "5 units missing"
    },
    {
      "part_id": "part-uuid-2",
      "quantity_before": 50,
      "quantity_after": 52,
      "quantity_change": +2,
      "reason": "2 units found in back room"
    }
  ]
}
```

## Benefits

1. ✅ Single source of truth (`stock_adjustments`)
2. ✅ Item-level tracking (what changed)
3. ✅ Full audit trail (who, when, why)
4. ✅ Proper history display
5. ✅ Clean codebase (no redundant tables)

## Migration Strategy

1. **Backup** existing `stock_adjustments` data (3 records)
2. **Create** new tables and structure
3. **Migrate** old records if needed (or archive)
4. **Drop** `inventory_adjustments` table
5. **Deploy** new code
6. **Test** adjustment workflow

---

Ready to implement? Let's start with the database migration.
