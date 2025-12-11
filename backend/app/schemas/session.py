# backend/app/schemas/session.py

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class UserSessionBase(BaseModel):
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime

class UserSessionResponse(UserSessionBase):
    id: uuid.UUID
    session_token: str
    is_current: bool = False

class SecurityEventResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    event_type: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    details: Optional[str] = None
    risk_level: str = "medium"
    success: bool = False

    class Config:
        from_attributes = True

class AdditionalVerification(BaseModel):
    verification_type: str = "email_code"  # Default to email code verification
    verification_code: str