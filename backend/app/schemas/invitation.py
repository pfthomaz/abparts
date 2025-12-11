# backend/app/schemas/invitation.py

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class InvitationAuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    action: str
    performed_by_user_id: Optional[uuid.UUID] = None
    timestamp: datetime
    details: Optional[str] = None

    class Config:
        from_attributes = True

class UserManagementAuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    action: str
    performed_by_user_id: uuid.UUID
    timestamp: datetime
    details: Optional[str] = None
    
    # Include related data for easier display
    user_username: Optional[str] = None
    performed_by_username: Optional[str] = None

    class Config:
        from_attributes = True