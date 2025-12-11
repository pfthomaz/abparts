# backend/app/schemas/token.py

import uuid
from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[uuid.UUID] = None
    organization_id: Optional[uuid.UUID] = None
    role: Optional[str] = None