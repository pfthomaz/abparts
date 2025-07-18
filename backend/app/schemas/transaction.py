# backend/app/schemas/transaction.py

import uuid
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class TransactionTypeEnum(str, Enum):
    CREATION = "creation"
    TRANSFER = "transfer"
    CONSUMPTION = "consumption"
    ADJUSTMENT = "adjustment"

class TransactionBase(BaseModel):
    transaction_type: TransactionTypeEnum
    part_id: uuid.UUID
    from_warehouse_id: Optional[uuid.UUID] = None
    to_warehouse_id: Optional[uuid.UUID] = None
    machine_id: Optional[uuid.UUID] = None
    quantity: Decimal
    unit_of_measure: str
    performed_by_user_id: uuid.UUID
    transaction_date: datetime
    notes: Optional[str] = None
    reference_number: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    transaction_type: Optional[TransactionTypeEnum] = None
    part_id: Optional[uuid.UUID] = None
    from_warehouse_id: Optional[uuid.UUID] = None
    to_warehouse_id: Optional[uuid.UUID] = None
    machine_id: Optional[uuid.UUID] = None
    quantity: Optional[Decimal] = None
    unit_of_measure: Optional[str] = None
    performed_by_user_id: Optional[uuid.UUID] = None
    transaction_date: Optional[datetime] = None
    notes: Optional[str] = None
    reference_number: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: uuid.UUID
    created_at: datetime
    
    # Include related data
    part_name: Optional[str] = None
    part_number: Optional[str] = None
    from_warehouse_name: Optional[str] = None
    to_warehouse_name: Optional[str] = None
    machine_serial: Optional[str] = None
    performed_by_username: Optional[str] = None

    class Config:
        from_attributes = True

class TransactionFilter(BaseModel):
    transaction_type: Optional[TransactionTypeEnum] = None
    part_id: Optional[uuid.UUID] = None
    from_warehouse_id: Optional[uuid.UUID] = None
    to_warehouse_id: Optional[uuid.UUID] = None
    machine_id: Optional[uuid.UUID] = None
    performed_by_user_id: Optional[uuid.UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    reference_number: Optional[str] = None

class TransactionReversal(BaseModel):
    transaction_id: uuid.UUID
    reason: str
    performed_by_user_id: uuid.UUID

class TransactionSummary(BaseModel):
    transaction_type: TransactionTypeEnum
    total_quantity: Decimal
    transaction_count: int
    
    class Config:
        from_attributes = True

class WarehouseTransactionSummary(BaseModel):
    warehouse_id: uuid.UUID
    warehouse_name: str
    incoming_transactions: int
    outgoing_transactions: int
    net_quantity: Decimal
    
    class Config:
        from_attributes = True

class PartTransactionHistory(BaseModel):
    part_id: uuid.UUID
    part_name: str
    part_number: str
    transactions: List[TransactionResponse]
    total_created: Decimal
    total_transferred: Decimal
    total_consumed: Decimal
    total_adjusted: Decimal
    net_quantity: Decimal
    
    class Config:
        from_attributes = True

class TransactionApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class TransactionApprovalRequest(BaseModel):
    transaction_id: uuid.UUID
    approver_id: uuid.UUID
    status: TransactionApprovalStatus
    notes: Optional[str] = None

class TransactionApprovalResponse(BaseModel):
    transaction_id: uuid.UUID
    approver_id: uuid.UUID
    status: TransactionApprovalStatus
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TransactionBatchRequest(BaseModel):
    transactions: List[TransactionCreate]
    reference: Optional[str] = None

class TransactionBatchResponse(BaseModel):
    transactions: List[TransactionResponse]
    reference: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class InventoryReconciliationItem(BaseModel):
    warehouse_id: uuid.UUID
    part_id: uuid.UUID
    current_stock: Decimal
    calculated_balance: Decimal
    discrepancy: Decimal
    reconciled: bool
    
    class Config:
        from_attributes = True

class InventoryReconciliationRequest(BaseModel):
    warehouse_id: uuid.UUID
    part_id: Optional[uuid.UUID] = None

class TransactionAnalytics(BaseModel):
    period_days: int
    total_transactions: int
    daily_average: float
    transactions_by_type: Dict[str, int]
    quantities_by_type: Dict[str, float]
    top_parts: List[Dict[str, Any]]
    top_warehouses: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True