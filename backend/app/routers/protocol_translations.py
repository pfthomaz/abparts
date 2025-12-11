# backend/app/routers/protocol_translations.py

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..services.translation_service import TranslationService
from ..schemas_translations import (
    ProtocolTranslationCreate, ProtocolTranslationUpdate, ProtocolTranslationResponse,
    ChecklistItemTranslationCreate, ChecklistItemTranslationUpdate, ChecklistItemTranslationResponse,
    TranslationStatusResponse, LocalizedProtocolResponse, LocalizedChecklistItemResponse
)

router = APIRouter()


def check_translation_permissions(current_user: User):
    """Check if user has permission to manage translations"""
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can manage translations"
        )


def get_user_language(accept_language: Optional[str] = Header(None)) -> str:
    """Extract user's preferred language from Accept-Language header or default to English"""
    if accept_language:
        # Parse Accept-Language header (simplified)
        # Format: "en-US,en;q=0.9,el;q=0.8"
        languages = accept_language.split(',')
        for lang in languages:
            lang_code = lang.split(';')[0].split('-')[0].strip().lower()
            if lang_code in ['en', 'el', 'ar', 'es', 'tr', 'no']:
                return lang_code
    return 'en'  # Default to English


# Protocol Translation Endpoints

@router.get("/protocols/{protocol_id}/translations", response_model=List[ProtocolTranslationResponse])
async def get_protocol_translations(
    protocol_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all translations for a protocol"""
    check_translation_permissions(current_user)
    
    translations = TranslationService.get_protocol_translations(protocol_id, db)
    return translations


@router.post("/protocols/{protocol_id}/translations", response_model=ProtocolTranslationResponse)
async def create_protocol_translation(
    protocol_id: UUID,
    translation_data: ProtocolTranslationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update a protocol translation"""
    check_translation_permissions(current_user)
    
    translation = TranslationService.create_protocol_translation(
        protocol_id, translation_data, db
    )
    return translation


@router.put("/protocols/{protocol_id}/translations/{language_code}", response_model=ProtocolTranslationResponse)
async def update_protocol_translation(
    protocol_id: UUID,
    language_code: str,
    translation_data: ProtocolTranslationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a specific protocol translation"""
    check_translation_permissions(current_user)
    
    # Convert update data to create data for the service
    create_data = ProtocolTranslationCreate(
        language_code=language_code,
        name=translation_data.name,
        description=translation_data.description
    )
    
    translation = TranslationService.create_protocol_translation(
        protocol_id, create_data, db
    )
    return translation


@router.delete("/protocols/{protocol_id}/translations/{language_code}")
async def delete_protocol_translation(
    protocol_id: UUID,
    language_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a protocol translation"""
    check_translation_permissions(current_user)
    
    success = TranslationService.delete_protocol_translation(
        protocol_id, language_code, db
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    return {"message": "Translation deleted successfully"}


@router.get("/protocols/{protocol_id}/translation-status", response_model=dict)
async def get_protocol_translation_status(
    protocol_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get translation completion status for a protocol"""
    check_translation_permissions(current_user)
    
    status = TranslationService.get_translation_status(protocol_id, db)
    
    if not status:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    return status


# Checklist Item Translation Endpoints

@router.get("/checklist-items/{item_id}/translations", response_model=List[ChecklistItemTranslationResponse])
async def get_checklist_item_translations(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all translations for a checklist item"""
    check_translation_permissions(current_user)
    
    translations = TranslationService.get_checklist_item_translations(item_id, db)
    return translations


@router.post("/checklist-items/{item_id}/translations", response_model=ChecklistItemTranslationResponse)
async def create_checklist_item_translation(
    item_id: UUID,
    translation_data: ChecklistItemTranslationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update a checklist item translation"""
    check_translation_permissions(current_user)
    
    translation = TranslationService.create_checklist_item_translation(
        item_id, translation_data, db
    )
    return translation


@router.put("/checklist-items/{item_id}/translations/{language_code}", response_model=ChecklistItemTranslationResponse)
async def update_checklist_item_translation(
    item_id: UUID,
    language_code: str,
    translation_data: ChecklistItemTranslationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a specific checklist item translation"""
    check_translation_permissions(current_user)
    
    # Convert update data to create data for the service
    create_data = ChecklistItemTranslationCreate(
        language_code=language_code,
        item_description=translation_data.item_description,
        notes=translation_data.notes,
        item_category=translation_data.item_category
    )
    
    translation = TranslationService.create_checklist_item_translation(
        item_id, create_data, db
    )
    return translation


@router.delete("/checklist-items/{item_id}/translations/{language_code}")
async def delete_checklist_item_translation(
    item_id: UUID,
    language_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a checklist item translation"""
    check_translation_permissions(current_user)
    
    success = TranslationService.delete_checklist_item_translation(
        item_id, language_code, db
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    return {"message": "Translation deleted successfully"}


# Language-aware Display Endpoints

@router.get("/protocols/{protocol_id}/localized", response_model=dict)
async def get_localized_protocol(
    protocol_id: UUID,
    language: Optional[str] = None,
    accept_language: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get protocol in user's preferred language with fallback"""
    
    # Determine preferred language
    preferred_language = language or get_user_language(accept_language)
    
    protocol = TranslationService.get_localized_protocol(
        protocol_id, preferred_language, db
    )
    
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    return protocol


@router.get("/protocols/{protocol_id}/checklist-items/localized", response_model=List[dict])
async def get_localized_checklist_items(
    protocol_id: UUID,
    language: Optional[str] = None,
    accept_language: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get checklist items in user's preferred language with fallback"""
    
    # Determine preferred language
    preferred_language = language or get_user_language(accept_language)
    
    items = TranslationService.get_localized_checklist_items(
        protocol_id, preferred_language, db
    )
    
    return items


# Bulk Translation Operations

@router.post("/protocols/{protocol_id}/translations/bulk")
async def bulk_create_protocol_translations(
    protocol_id: UUID,
    translations: List[ProtocolTranslationCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create multiple protocol translations at once"""
    check_translation_permissions(current_user)
    
    created_translations = []
    
    for translation_data in translations:
        translation = TranslationService.create_protocol_translation(
            protocol_id, translation_data, db
        )
        created_translations.append(translation)
    
    return {
        "message": f"Created {len(created_translations)} translations",
        "translations": created_translations
    }


@router.post("/checklist-items/translations/bulk")
async def bulk_create_checklist_item_translations(
    translations: List[dict],  # Format: [{"item_id": UUID, "language_code": str, "item_description": str, ...}]
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create multiple checklist item translations at once"""
    check_translation_permissions(current_user)
    
    created_translations = []
    
    for translation_data in translations:
        item_id = UUID(translation_data["item_id"])
        create_data = ChecklistItemTranslationCreate(
            language_code=translation_data["language_code"],
            item_description=translation_data["item_description"],
            notes=translation_data.get("notes"),
            item_category=translation_data.get("item_category")
        )
        
        translation = TranslationService.create_checklist_item_translation(
            item_id, create_data, db
        )
        created_translations.append(translation)
    
    return {
        "message": f"Created {len(created_translations)} translations",
        "translations": created_translations
    }