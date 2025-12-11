# backend/app/services/translation_service.py

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from ..models import MaintenanceProtocol, ProtocolChecklistItem, ProtocolTranslation, ChecklistItemTranslation
from ..schemas_translations import (
    ProtocolTranslationCreate, ProtocolTranslationUpdate,
    ChecklistItemTranslationCreate, ChecklistItemTranslationUpdate,
    LocalizedProtocolResponse, LocalizedChecklistItemResponse,
    TranslationStatusResponse
)

# Supported languages
SUPPORTED_LANGUAGES = ['en', 'el', 'ar', 'es', 'tr', 'no']


class TranslationService:
    """Service for managing protocol and checklist item translations"""

    @staticmethod
    def get_localized_protocol(
        protocol_id: UUID, 
        preferred_language: str, 
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        Get protocol in specified language with fallback to base language.
        Returns protocol data with translation metadata.
        """
        # Get protocol with all translations
        protocol = db.query(MaintenanceProtocol).options(
            joinedload(MaintenanceProtocol.translations)
        ).filter(MaintenanceProtocol.id == protocol_id).first()
        
        if not protocol:
            return None
        
        # Find translation for preferred language
        translation = None
        for trans in protocol.translations:
            if trans.language_code == preferred_language:
                translation = trans
                break
        
        # Determine display language and content
        if translation:
            display_name = translation.name
            display_description = translation.description
            display_language = preferred_language
            is_translated = True
        else:
            # Fallback to base language
            display_name = protocol.name
            display_description = protocol.description
            display_language = protocol.base_language
            is_translated = (preferred_language == protocol.base_language)
        
        # Get available languages
        available_languages = [protocol.base_language]
        available_languages.extend([t.language_code for t in protocol.translations])
        available_languages = list(set(available_languages))  # Remove duplicates
        
        return {
            'id': protocol.id,
            'name': display_name,
            'description': display_description,
            'protocol_type': protocol.protocol_type.value,
            'service_interval_hours': protocol.service_interval_hours,
            'is_recurring': protocol.is_recurring,
            'machine_model': protocol.machine_model,
            'is_active': protocol.is_active,
            'display_order': protocol.display_order,
            'base_language': protocol.base_language,
            'display_language': display_language,
            'is_translated': is_translated,
            'available_languages': available_languages,
            'created_at': protocol.created_at,
            'updated_at': protocol.updated_at
        }

    @staticmethod
    def get_localized_checklist_items(
        protocol_id: UUID,
        preferred_language: str,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get checklist items in specified language with fallback"""
        
        # Get checklist items with translations
        items = db.query(ProtocolChecklistItem).options(
            joinedload(ProtocolChecklistItem.translations),
            joinedload(ProtocolChecklistItem.part)
        ).filter(
            ProtocolChecklistItem.protocol_id == protocol_id
        ).order_by(ProtocolChecklistItem.item_order).all()
        
        localized_items = []
        
        for item in items:
            # Find translation for preferred language
            translation = None
            for trans in item.translations:
                if trans.language_code == preferred_language:
                    translation = trans
                    break
            
            # Determine display content
            if translation:
                display_description = translation.item_description
                display_notes = translation.notes
                display_category = translation.item_category
                display_language = preferred_language
                is_translated = True
            else:
                # Fallback to base language
                display_description = item.item_description
                display_notes = item.notes
                display_category = item.item_category
                display_language = item.base_language
                is_translated = (preferred_language == item.base_language)
            
            # Get available languages for this item
            available_languages = [item.base_language]
            available_languages.extend([t.language_code for t in item.translations])
            available_languages = list(set(available_languages))
            
            localized_items.append({
                'id': item.id,
                'protocol_id': item.protocol_id,
                'item_order': item.item_order,
                'item_description': display_description,
                'item_type': item.item_type.value,
                'item_category': display_category,
                'part_id': item.part_id,
                'part': {
                    'id': item.part.id,
                    'name': item.part.name,
                    'part_number': item.part.part_number
                } if item.part else None,
                'estimated_quantity': item.estimated_quantity,
                'is_critical': item.is_critical,
                'estimated_duration_minutes': item.estimated_duration_minutes,
                'notes': display_notes,
                'base_language': item.base_language,
                'display_language': display_language,
                'is_translated': is_translated,
                'available_languages': available_languages,
                'created_at': item.created_at
            })
        
        return localized_items

    @staticmethod
    def get_translation_status(protocol_id: UUID, db: Session) -> Optional[Dict[str, Any]]:
        """Get translation completion status for a protocol"""
        
        protocol = db.query(MaintenanceProtocol).filter(
            MaintenanceProtocol.id == protocol_id
        ).first()
        
        if not protocol:
            return None
        
        # Get checklist items count
        total_items = db.query(ProtocolChecklistItem).filter(
            ProtocolChecklistItem.protocol_id == protocol_id
        ).count()
        
        # Get protocol translations
        protocol_translations = db.query(ProtocolTranslation).filter(
            ProtocolTranslation.protocol_id == protocol_id
        ).all()
        
        # Get checklist item translations by language
        item_translations = db.query(ChecklistItemTranslation).join(
            ProtocolChecklistItem
        ).filter(
            ProtocolChecklistItem.protocol_id == protocol_id
        ).all()
        
        # Calculate status for each language
        translated_items = {}
        completion_percentage = {}
        
        for lang in SUPPORTED_LANGUAGES:
            if lang == protocol.base_language:
                # Base language is always 100% complete
                translated_items[lang] = total_items + 1  # +1 for protocol itself
                completion_percentage[lang] = 100.0
            else:
                # Count translations for this language
                protocol_translated = any(t.language_code == lang for t in protocol_translations)
                items_translated = len([t for t in item_translations if t.language_code == lang])
                
                total_translatable = total_items + 1  # +1 for protocol
                total_translated = (1 if protocol_translated else 0) + items_translated
                
                translated_items[lang] = total_translated
                completion_percentage[lang] = (total_translated / total_translatable * 100) if total_translatable > 0 else 0
        
        # Find missing languages (less than 100% complete)
        missing_languages = [
            lang for lang, percentage in completion_percentage.items() 
            if percentage < 100.0 and lang != protocol.base_language
        ]
        
        return {
            'protocol_id': protocol_id,
            'total_items': total_items + 1,  # +1 for protocol itself
            'translated_items': translated_items,
            'completion_percentage': completion_percentage,
            'missing_languages': missing_languages,
            'base_language': protocol.base_language
        }

    @staticmethod
    def create_protocol_translation(
        protocol_id: UUID,
        translation_data: ProtocolTranslationCreate,
        db: Session
    ) -> ProtocolTranslation:
        """Create or update a protocol translation"""
        
        # Check if translation already exists
        existing = db.query(ProtocolTranslation).filter(
            and_(
                ProtocolTranslation.protocol_id == protocol_id,
                ProtocolTranslation.language_code == translation_data.language_code
            )
        ).first()
        
        if existing:
            # Update existing translation
            existing.name = translation_data.name
            existing.description = translation_data.description
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new translation
            translation = ProtocolTranslation(
                protocol_id=protocol_id,
                language_code=translation_data.language_code,
                name=translation_data.name,
                description=translation_data.description
            )
            db.add(translation)
            db.commit()
            db.refresh(translation)
            return translation

    @staticmethod
    def create_checklist_item_translation(
        item_id: UUID,
        translation_data: ChecklistItemTranslationCreate,
        db: Session
    ) -> ChecklistItemTranslation:
        """Create or update a checklist item translation"""
        
        # Check if translation already exists
        existing = db.query(ChecklistItemTranslation).filter(
            and_(
                ChecklistItemTranslation.checklist_item_id == item_id,
                ChecklistItemTranslation.language_code == translation_data.language_code
            )
        ).first()
        
        if existing:
            # Update existing translation
            existing.item_description = translation_data.item_description
            existing.notes = translation_data.notes
            existing.item_category = translation_data.item_category
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new translation
            translation = ChecklistItemTranslation(
                checklist_item_id=item_id,
                language_code=translation_data.language_code,
                item_description=translation_data.item_description,
                notes=translation_data.notes,
                item_category=translation_data.item_category
            )
            db.add(translation)
            db.commit()
            db.refresh(translation)
            return translation

    @staticmethod
    def delete_protocol_translation(
        protocol_id: UUID,
        language_code: str,
        db: Session
    ) -> bool:
        """Delete a protocol translation"""
        
        translation = db.query(ProtocolTranslation).filter(
            and_(
                ProtocolTranslation.protocol_id == protocol_id,
                ProtocolTranslation.language_code == language_code
            )
        ).first()
        
        if translation:
            db.delete(translation)
            db.commit()
            return True
        return False

    @staticmethod
    def delete_checklist_item_translation(
        item_id: UUID,
        language_code: str,
        db: Session
    ) -> bool:
        """Delete a checklist item translation"""
        
        translation = db.query(ChecklistItemTranslation).filter(
            and_(
                ChecklistItemTranslation.checklist_item_id == item_id,
                ChecklistItemTranslation.language_code == language_code
            )
        ).first()
        
        if translation:
            db.delete(translation)
            db.commit()
            return True
        return False

    @staticmethod
    def get_protocol_translations(protocol_id: UUID, db: Session) -> List[ProtocolTranslation]:
        """Get all translations for a protocol"""
        return db.query(ProtocolTranslation).filter(
            ProtocolTranslation.protocol_id == protocol_id
        ).all()

    @staticmethod
    def get_checklist_item_translations(item_id: UUID, db: Session) -> List[ChecklistItemTranslation]:
        """Get all translations for a checklist item"""
        return db.query(ChecklistItemTranslation).filter(
            ChecklistItemTranslation.checklist_item_id == item_id
        ).all()