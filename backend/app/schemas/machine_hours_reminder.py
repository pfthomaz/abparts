# backend/app/schemas/machine_hours_reminder.py

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

class MachineHoursReminderCheck(BaseModel):
    """Schema for individual machine reminder check"""
    machine_id: uuid.UUID
    machine_name: str
    serial_number: str
    last_recorded_date: Optional[datetime] = None
    days_since_last_record: Optional[int] = None
    never_recorded: bool = False

    class Config:
        from_attributes = True

class MachineHoursReminderResponse(BaseModel):
    """Schema for reminder check response"""
    should_show_reminder: bool
    reminder_machines: List[MachineHoursReminderCheck] = []
    reminder_reason: str  # "monthly_check", "overdue_machines", or "no_reminder"
    total_overdue_machines: int = 0

class BulkMachineHoursCreate(BaseModel):
    """Schema for bulk machine hours creation from reminder modal"""
    machine_id: uuid.UUID
    hours_value: Decimal = Field(..., decimal_places=2, gt=0, description="Machine hours value (must be positive)")
    notes: Optional[str] = None

class BulkMachineHoursRequest(BaseModel):
    """Schema for bulk machine hours request"""
    machine_hours: List[BulkMachineHoursCreate]

class ReminderDismissalCreate(BaseModel):
    """Schema for tracking reminder dismissals"""
    user_id: uuid.UUID
    dismissed_date: datetime = Field(default_factory=datetime.now)

class ReminderDismissalResponse(BaseModel):
    """Schema for reminder dismissal response"""
    id: uuid.UUID
    user_id: uuid.UUID
    dismissed_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True