# backend/app/schemas/transaction.py

import uuid
from typing import Optional, List
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
        orm_mode = True

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
        orm_mode = True

class WarehouseTransactionSummary(BaseModel):
    warehouse_id: uuid.UUID
    warehouse_name: str
    incoming_transactions: int
    outgoing_transactions: int
    net_quantity: Decimal
    
    class Config:
        orm_mode = True

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
        orm_mode = True