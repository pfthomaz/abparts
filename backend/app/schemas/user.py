# backend/app/schemas/user.py

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, EmailStr, Field

class UserRoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_INVITATION = "pending_invitation"
    LOCKED = "locked"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: Optional[str] = None
    role: UserRoleEnum
    organization_id: uuid.UUID

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    organization_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: uuid.UUID
    user_status: UserStatusEnum
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserAccountStatusUpdate(BaseModel):
    user_status: UserStatusEnum

class UserInvitationCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    role: UserRoleEnum
    organization_id: uuid.UUID

class UserInvitationResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: Optional[str] = None
    role: UserRoleEnum
    organization_id: uuid.UUID
    user_status: UserStatusEnum
    invitation_token: Optional[str] = None
    invitation_expires_at: Optional[datetime] = None
    invited_by_user_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        orm_mode = True

class UserInvitationAcceptance(BaseModel):
    invitation_token: str
    username: str
    password: str
    name: Optional[str] = None

class UserInvitationResend(BaseModel):
    user_id: uuid.UUID

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserProfileResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    name: Optional[str] = None
    role: UserRoleEnum
    organization_id: uuid.UUID
    organization_name: str
    organization_type: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str

class EmailVerificationRequest(BaseModel):
    new_email: EmailStr

class EmailVerificationConfirm(BaseModel):
    verification_token: str