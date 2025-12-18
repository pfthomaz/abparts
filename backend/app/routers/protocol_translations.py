# backend/app/routers/protocol_translations.py

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..services.translation_service import TranslationService
from ..services.ai_translation_service import ai_translation_service
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

# AI-Powered Auto-Translation Endpoints

@router.post("/protocols/{protocol_id}/auto-translate")
async def auto_translate_protocol(
    protocol_id: UUID,
    target_languages: Optional[List[str]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Automatically translate a protocol to specified languages using AI
    
    Args:
        protocol_id: UUID of the protocol to translate
        target_languages: List of language codes to translate to (default: all supported)
    
    Returns:
        Dictionary with translation results and status
    """
    check_translation_permissions(current_user)
    
    # Check if AI translation service is available
    if not ai_translation_service.is_translation_available():
        raise HTTPException(
            status_code=503, 
            detail="AI translation service is currently unavailable"
        )
    
    # Get the protocol
    from ..models import MaintenanceProtocol
    protocol = db.query(MaintenanceProtocol).filter(
        MaintenanceProtocol.id == protocol_id
    ).first()
    
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    # Use default target languages if not specified
    if target_languages is None:
        target_languages = ai_translation_service.get_supported_languages()
    
    try:
        # Generate AI translations
        ai_translations = await ai_translation_service.translate_protocol(
            protocol_name=protocol.name,
            protocol_description=protocol.description,
            target_languages=target_languages
        )
        
        # Save translations to database
        created_translations = []
        failed_translations = []
        
        for lang_code, translation_data in ai_translations.items():
            try:
                # Create translation data
                translation_create = ProtocolTranslationCreate(
                    language_code=lang_code,
                    name=translation_data['name'],
                    description=translation_data.get('description')
                )
                
                # Save to database
                translation = TranslationService.create_protocol_translation(
                    protocol_id, translation_create, db
                )
                
                created_translations.append({
                    'language_code': lang_code,
                    'name': translation_data['name'],
                    'description': translation_data.get('description'),
                    'status': 'success'
                })
                
            except Exception as e:
                failed_translations.append({
                    'language_code': lang_code,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return {
            'protocol_id': protocol_id,
            'total_requested': len(target_languages),
            'successful_translations': len(created_translations),
            'failed_translations': len(failed_translations),
            'translations': created_translations,
            'failures': failed_translations,
            'message': f"Auto-translated protocol to {len(created_translations)} languages"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Auto-translation failed: {str(e)}"
        )


@router.post("/protocols/{protocol_id}/auto-translate-checklist")
async def auto_translate_protocol_checklist(
    protocol_id: UUID,
    target_languages: Optional[List[str]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Automatically translate all checklist items for a protocol using AI
    
    Args:
        protocol_id: UUID of the protocol whose checklist items to translate
        target_languages: List of language codes to translate to (default: all supported)
    
    Returns:
        Dictionary with translation results and status
    """
    check_translation_permissions(current_user)
    
    # Check if AI translation service is available
    if not ai_translation_service.is_translation_available():
        raise HTTPException(
            status_code=503, 
            detail="AI translation service is currently unavailable"
        )
    
    # Get checklist items for the protocol
    from ..models import ProtocolChecklistItem
    checklist_items = db.query(ProtocolChecklistItem).filter(
        ProtocolChecklistItem.protocol_id == protocol_id
    ).order_by(ProtocolChecklistItem.item_order).all()
    
    if not checklist_items:
        return {
            'protocol_id': protocol_id,
            'message': 'No checklist items found for this protocol',
            'total_items': 0,
            'successful_translations': 0,
            'failed_translations': 0
        }
    
    # Use default target languages if not specified
    if target_languages is None:
        target_languages = ai_translation_service.get_supported_languages()
    
    try:
        # Prepare items for translation
        items_data = []
        for item in checklist_items:
            items_data.append({
                'item_description': item.item_description,
                'notes': item.notes,
                'item_category': item.item_category
            })
        
        # Generate AI translations for all items
        ai_translations = await ai_translation_service.translate_multiple_checklist_items(
            items=items_data,
            target_languages=target_languages
        )
        
        # Save translations to database
        total_successful = 0
        total_failed = 0
        translation_results = []
        
        for item_index, item in enumerate(checklist_items):
            item_translations = ai_translations.get(item_index, {})
            item_results = {
                'item_id': item.id,
                'item_order': item.item_order,
                'original_description': item.item_description,
                'translations': [],
                'failures': []
            }
            
            for lang_code in target_languages:
                if lang_code in item_translations:
                    translation_data = item_translations[lang_code]
                    
                    try:
                        # Create translation data
                        translation_create = ChecklistItemTranslationCreate(
                            language_code=lang_code,
                            item_description=translation_data['item_description'],
                            notes=translation_data.get('notes'),
                            item_category=translation_data.get('item_category')
                        )
                        
                        # Save to database
                        translation = TranslationService.create_checklist_item_translation(
                            item.id, translation_create, db
                        )
                        
                        item_results['translations'].append({
                            'language_code': lang_code,
                            'item_description': translation_data['item_description'],
                            'notes': translation_data.get('notes'),
                            'item_category': translation_data.get('item_category'),
                            'status': 'success'
                        })
                        
                        total_successful += 1
                        
                    except Exception as e:
                        item_results['failures'].append({
                            'language_code': lang_code,
                            'error': str(e),
                            'status': 'failed'
                        })
                        total_failed += 1
                else:
                    item_results['failures'].append({
                        'language_code': lang_code,
                        'error': 'AI translation not generated',
                        'status': 'failed'
                    })
                    total_failed += 1
            
            translation_results.append(item_results)
        
        return {
            'protocol_id': protocol_id,
            'total_items': len(checklist_items),
            'total_requested_translations': len(checklist_items) * len(target_languages),
            'successful_translations': total_successful,
            'failed_translations': total_failed,
            'target_languages': target_languages,
            'results': translation_results,
            'message': f"Auto-translated {total_successful} checklist item translations"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Auto-translation failed: {str(e)}"
        )


@router.post("/protocols/{protocol_id}/auto-translate-complete")
async def auto_translate_complete_protocol(
    protocol_id: UUID,
    target_languages: Optional[List[str]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Automatically translate both protocol and all its checklist items using AI
    
    Args:
        protocol_id: UUID of the protocol to translate completely
        target_languages: List of language codes to translate to (default: all supported)
    
    Returns:
        Dictionary with complete translation results and status
    """
    check_translation_permissions(current_user)
    
    # Check if AI translation service is available
    if not ai_translation_service.is_translation_available():
        raise HTTPException(
            status_code=503, 
            detail="AI translation service is currently unavailable"
        )
    
    try:
        # Translate protocol first
        protocol_result = await auto_translate_protocol(
            protocol_id, target_languages, db, current_user
        )
        
        # Then translate checklist items
        checklist_result = await auto_translate_protocol_checklist(
            protocol_id, target_languages, db, current_user
        )
        
        return {
            'protocol_id': protocol_id,
            'protocol_translation': protocol_result,
            'checklist_translation': checklist_result,
            'total_successful_translations': (
                protocol_result['successful_translations'] + 
                checklist_result['successful_translations']
            ),
            'total_failed_translations': (
                protocol_result['failed_translations'] + 
                checklist_result['failed_translations']
            ),
            'message': 'Complete protocol auto-translation completed'
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Complete auto-translation failed: {str(e)}"
        )


@router.get("/auto-translate/status")
async def get_auto_translate_status(
    current_user: User = Depends(get_current_user)
):
    """Check if auto-translation service is available"""
    
    is_available = ai_translation_service.is_translation_available()
    supported_languages = ai_translation_service.get_supported_languages()
    
    return {
        'service_available': is_available,
        'supported_languages': supported_languages,
        'total_supported_languages': len(supported_languages)
    }