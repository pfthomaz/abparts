# Stock Adjustments Implementation Plan

## Current State Analysis

### What Exists:
1. **`stock_adjustments` table** (in database, has model)
   - Links to `inventory` table (single part per adjustment)
   - Has 3 old records
   - Currently used but not properly

2. **`inventory_adjustments` table** (in database, NO model)
   - Referenced in code but model doesn't exist
   - Empty table
   - Should be removed

3. **Code references `InventoryAdjustment`** but model missing
   - CRUD functions exist
   - Router endpoints exist
   - Schemas exist
   - But no actual model!

### The Problem:
- Code is trying to use `InventoryAdjustment` model that doesn't exist
- This is why adjustments aren't working
- Two tables doing similar things (redundant)

## Implementation Plan

### Step 1: Create Migration
Create a migration that:
1. **Drops** `inventory_adjustments` table
2. **Updates** `stock_adjustments` table structure:
   - Remove `inventory_id` (too specific)
   - Add `warehouse_id` (more flexible)
   - Add `adjustment_type` enum
   - Keep `user_id`, `reason_code`, `notes`
3. **Creates** `stock_adjustment_items` table:
   - Links to `stock_adjustments`
   - Tracks individual part adjustments

### Step 2: Update Models
1. **Remove** all `InventoryAdjustment` references
2. **Update** `StockAdjustment` model
3. **Create** `StockAdjustmentItem` model

### Step 3: Update Schemas
1. Remove `InventoryAdjustment` schemas
2. Create new `StockAdjustment` schemas with items
3. Add adjustment type enum

### Step 4: Update CRUD
1. Remove `inventory_workflow.py` adjustment functions
2. Create new `stock_adjustments.py` CRUD file
3. Implement proper adjustment logic with items

### Step 5: Update Routers
1. Remove `/inventory-workflow/adjustments` endpoints
2. Create `/stock-adjustments` endpoints
3. Implement list, create, get detail

### Step 6: Update Frontend
1. Update `StockResetTab` to use new endpoints
2. Display adjustment history properly
3. Show item-level details

## Detailed Implementation

### Migration File

```python
"""redesign_stock_adjustments

Revision ID: xxxxx
Revises: previous_revision
Create Date: 2024-11-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# Drop inventory_adjustments table
op.drop_table('inventory_adjustments')

# Create adjustment_type enum
adjustment_type_enum = postgresql.ENUM(
    'manual', 'correction', 'damage', 'loss', 'found', 'other',
    name='adjustmenttype'
)
adjustment_type_enum.create(op.get_bind())

# Modify stock_adjustments table
op.drop_column('stock_adjustments', 'inventory_id')
op.add_column('stock_adjustments', sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False))
op.add_column('stock_adjustments', sa.Column('adjustment_type', adjustment_type_enum, nullable=False, server_default='manual'))
op.add_column('stock_adjustments', sa.Column('reason', sa.Text(), nullable=True))
op.alter_column('stock_adjustments', 'quantity_adjusted', new_column_name='total_items_adjusted')

# Create stock_adjustment_items table
op.create_table(
    'stock_adjustment_items',
    sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    sa.Column('stock_adjustment_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('part_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('quantity_before', sa.DECIMAL(precision=10, scale=3), nullable=False),
    sa.Column('quantity_after', sa.DECIMAL(precision=10, scale=3), nullable=False),
    sa.Column('quantity_change', sa.DECIMAL(precision=10, scale=3), nullable=False),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.ForeignKeyConstraint(['stock_adjustment_id'], ['stock_adjustments.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['part_id'], ['parts.id']),
)
```

### New Models

```python
class AdjustmentType(str, Enum):
    MANUAL = "manual"  # Manual stock count
    CORRECTION = "correction"  # Error correction
    DAMAGE = "damage"  # Damaged goods
    LOSS = "loss"  # Lost/stolen
    FOUND = "found"  # Found items
    OTHER = "other"  # Other reasons

class StockAdjustment(Base):
    __tablename__ = "stock_adjustments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    adjustment_type = Column(Enum(AdjustmentType), nullable=False)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    adjustment_date = Column(DateTime(timezone=True), server_default=func.now())
    total_items_adjusted = Column(Integer, nullable=False)  # Count of items
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    warehouse = relationship("Warehouse")
    user = relationship("User")
    items = relationship("StockAdjustmentItem", back_populates="adjustment", cascade="all, delete-orphan")

class StockAdjustmentItem(Base):
    __tablename__ = "stock_adjustment_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_adjustment_id = Column(UUID(as_uuid=True), ForeignKey("stock_adjustments.id", ondelete="CASCADE"))
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"))
    quantity_before = Column(DECIMAL(10, 3), nullable=False)
    quantity_after = Column(DECIMAL(10, 3), nullable=False)
    quantity_change = Column(DECIMAL(10, 3), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    adjustment = relationship("StockAdjustment", back_populates="items")
    part = relationship("Part")
```

### New Schemas

```python
class AdjustmentTypeEnum(str, Enum):
    MANUAL = "manual"
    CORRECTION = "correction"
    DAMAGE = "damage"
    LOSS = "loss"
    FOUND = "found"
    OTHER = "other"

class StockAdjustmentItemCreate(BaseModel):
    part_id: uuid.UUID
    quantity_after: Decimal
    reason: Optional[str] = None

class StockAdjustmentItemResponse(BaseModel):
    id: uuid.UUID
    part_id: uuid.UUID
    part_number: str
    part_name: str
    quantity_before: Decimal
    quantity_after: Decimal
    quantity_change: Decimal
    reason: Optional[str]
    
    class Config:
        from_attributes = True

class StockAdjustmentCreate(BaseModel):
    warehouse_id: uuid.UUID
    adjustment_type: AdjustmentTypeEnum
    reason: Optional[str] = None
    notes: Optional[str] = None
    items: List[StockAdjustmentItemCreate]

class StockAdjustmentResponse(BaseModel):
    id: uuid.UUID
    warehouse_id: uuid.UUID
    warehouse_name: str
    adjustment_type: AdjustmentTypeEnum
    reason: Optional[str]
    notes: Optional[str]
    user_id: uuid.UUID
    username: str
    adjustment_date: datetime
    total_items_adjusted: int
    items: List[StockAdjustmentItemResponse]
    
    class Config:
        from_attributes = True
```

## Files to Modify

### Backend:
1. `backend/alembic/versions/xxxxx_redesign_stock_adjustments.py` - NEW
2. `backend/app/models.py` - UPDATE StockAdjustment, ADD StockAdjustmentItem
3. `backend/app/schemas.py` - ADD new adjustment schemas
4. `backend/app/crud/stock_adjustments.py` - NEW file
5. `backend/app/routers/stock_adjustments.py` - NEW file
6. `backend/app/crud/inventory_workflow.py` - REMOVE adjustment functions
7. `backend/app/routers/inventory_workflow.py` - REMOVE adjustment endpoints

### Frontend:
1. `frontend/src/services/stockAdjustmentsService.js` - NEW
2. `frontend/src/components/StockResetTab.js` - UPDATE to use new API
3. `frontend/src/components/StockAdjustmentForm.js` - NEW (if needed)

## Testing Checklist

- [ ] Migration runs successfully
- [ ] Old data preserved (if any)
- [ ] Can create new adjustment with multiple items
- [ ] Inventory quantities update correctly
- [ ] Transactions created for audit trail
- [ ] Adjustment history displays correctly
- [ ] Can filter adjustments by warehouse/date
- [ ] Can view adjustment details with items
- [ ] Proper error handling
- [ ] Works in production

---

Ready to start implementation? Let's begin with the migration!
