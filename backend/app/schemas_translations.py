# backend/app/schemas_translations.py

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


# Protocol Translation Schemas
class ProtocolTranslationBase(BaseModel):
    language_code: str = Field(..., min_length=2, max_length=5, description="Language code (e.g., 'en', 'el', 'ar')")
    name: str = Field(..., min_length=1, max_length=500, description="Translated protocol name")
    description: Optional[str] = Field(None, max_length=2000, description="Translated protocol description")


class ProtocolTranslationCreate(ProtocolTranslationBase):
    pass


class ProtocolTranslationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)


class ProtocolTranslationResponse(ProtocolTranslationBase):
    id: UUID
    protocol_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Checklist Item Translation Schemas
class ChecklistItemTranslationBase(BaseModel):
    language_code: str = Field(..., min_length=2, max_length=5)
    item_description: str = Field(..., min_length=1, max_length=1000, description="Translated item description")
    notes: Optional[str] = Field(None, max_length=1000, description="Translated notes")
    item_category: Optional[str] = Field(None, max_length=100, description="Translated category")


class ChecklistItemTranslationCreate(ChecklistItemTranslationBase):
    pass


class ChecklistItemTranslationUpdate(BaseModel):
    item_description: Optional[str] = Field(None, min_length=1, max_length=1000)
    notes: Optional[str] = Field(None, max_length=1000)
    item_category: Optional[str] = Field(None, max_length=100)


class ChecklistItemTranslationResponse(ChecklistItemTranslationBase):
    id: UUID
    checklist_item_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Enhanced Protocol Response with Translations
class ProtocolWithTranslationsResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    protocol_type: str
    base_language: str
    translations: List[ProtocolTranslationResponse] = []
    translation_status: Dict[str, str] = {}  # language_code -> "complete"|"draft"|"missing"

    class Config:
        from_attributes = True


# Enhanced Checklist Item Response with Translations
class ChecklistItemWithTranslationsResponse(BaseModel):
    id: UUID
    item_description: str
    notes: Optional[str]
    item_category: Optional[str]
    base_language: str
    translations: List[ChecklistItemTranslationResponse] = []
    translation_status: Dict[str, str] = {}

    class Config:
        from_attributes = True


# Bulk Translation Operations
class BulkTranslationRequest(BaseModel):
    target_language: str = Field(..., min_length=2, max_length=5)
    translations: List[Dict[str, str]] = Field(..., description="List of {id: translated_text} pairs")


class TranslationStatusResponse(BaseModel):
    protocol_id: UUID
    total_items: int
    translated_items: Dict[str, int]  # language_code -> count
    completion_percentage: Dict[str, float]  # language_code -> percentage
    missing_languages: List[str]


# Language-aware Protocol Display
class LocalizedProtocolResponse(BaseModel):
    """Protocol response in user's preferred language with fallback indicators"""
    id: UUID
    name: str
    description: Optional[str]
    protocol_type: str
    display_language: str  # Language actually being displayed
    is_translated: bool  # True if in user's preferred language
    available_languages: List[str]  # Languages with translations
    
    class Config:
        from_attributes = True


class LocalizedChecklistItemResponse(BaseModel):
    """Checklist item response in user's preferred language"""
    id: UUID
    item_description: str
    notes: Optional[str]
    item_category: Optional[str]
    display_language: str
    is_translated: bool
    available_languages: List[str]
    
    class Config:
        from_attributes = True