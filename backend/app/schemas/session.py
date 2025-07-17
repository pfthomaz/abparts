# backend/app/schemas/session.py

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class UserSessionBase(BaseModel):
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class UserSessionCreate(UserSessionBase):
    user_id: uuid.UUID
    session_token: str
    expires_at: datetime

class UserSessionResponse(UserSessionBase):
    id: uuid.UUID
    session_token: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_current: bool = False

    class Config:
        orm_mode = True

class SecurityEventBase(BaseModel):
    event_type: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    details: Optional[str] = None
    risk_level: str = "low"

class SecurityEventCreate(SecurityEventBase):
    user_id: Optional[uuid.UUID] = None

class SecurityEventResponse(SecurityEventBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    timestamp: datetime

    class Config:
        orm_mode = True

class AdditionalVerification(BaseModel):
    verification_type: str = Field(..., description="Type of verification (email_code, sms_code, etc.)")
    verification_code: str = Field(..., description="Verification code provided by the user")

class SecurityDashboardResponse(BaseModel):
    total_events: int
    events_by_risk: dict
    events_by_type: dict
    failed_logins: int
    account_lockouts: int
    suspicious_activity: int
    active_sessions: int
    date_range: dict