# backend/app/services/ai_translation_service.py

import os
import logging
from typing import Dict, List, Optional
from googletrans import Translator
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class AITranslationService:
    """Service for AI-powered automatic translations using Google Translate"""
    
    def __init__(self):
        self.translator = Translator()
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Language mapping: our codes -> Google Translate codes
        self.language_mapping = {
            'en': 'en',  # English
            'el': 'el',  # Greek
            'ar': 'ar',  # Arabic
            'es': 'es',  # Spanish
            'tr': 'tr',  # Turkish
            'no': 'no'   # Norwegian
        }
        
        # Supported target languages (excluding base language 'en')
        self.target_languages = ['el', 'ar', 'es', 'tr', 'no']
    
    async def translate_text(self, text: str, target_language: str, source_language: str = 'en') -> Optional[str]:
        """
        Translate a single text string to target language
        
        Args:
            text: Text to translate
            target_language: Target language code ('el', 'ar', etc.)
            source_language: Source language code (default: 'en')
            
        Returns:
            Translated text or None if translation fails
        """
        if not text or not text.strip():
            return text
            
        if target_language == source_language:
            return text
            
        try:
            # Get Google Translate language codes
            src_lang = self.language_mapping.get(source_language, source_language)
            dest_lang = self.language_mapping.get(target_language, target_language)
            
            # Run translation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._translate_sync,
                text,
                src_lang,
                dest_lang
            )
            
            return result.text if result else None
            
        except Exception as e:
            logger.error(f"Translation failed for '{text[:50]}...' to {target_language}: {str(e)}")
            return None
    
    def _translate_sync(self, text: str, src_lang: str, dest_lang: str):
        """Synchronous translation method for thread pool execution"""
        return self.translator.translate(text, src=src_lang, dest=dest_lang)
    
    async def translate_protocol(
        self, 
        protocol_name: str, 
        protocol_description: Optional[str] = None,
        target_languages: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Translate protocol name and description to multiple languages
        
        Args:
            protocol_name: Protocol name to translate
            protocol_description: Protocol description to translate (optional)
            target_languages: List of target language codes (default: all supported)
            
        Returns:
            Dictionary with translations:
            {
                'el': {'name': 'Translated name', 'description': 'Translated desc'},
                'ar': {'name': 'Translated name', 'description': 'Translated desc'},
                ...
            }
        """
        if target_languages is None:
            target_languages = self.target_languages
            
        translations = {}
        
        for lang in target_languages:
            try:
                # Translate name (required)
                translated_name = await self.translate_text(protocol_name, lang)
                
                # Translate description (optional)
                translated_description = None
                if protocol_description:
                    translated_description = await self.translate_text(protocol_description, lang)
                
                if translated_name:  # Only add if name translation succeeded
                    translations[lang] = {
                        'name': translated_name,
                        'description': translated_description
                    }
                    
            except Exception as e:
                logger.error(f"Failed to translate protocol to {lang}: {str(e)}")
                continue
        
        return translations
    
    async def translate_checklist_item(
        self,
        item_description: str,
        item_notes: Optional[str] = None,
        item_category: Optional[str] = None,
        target_languages: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Translate checklist item content to multiple languages
        
        Args:
            item_description: Item description to translate
            item_notes: Item notes to translate (optional)
            item_category: Item category to translate (optional)
            target_languages: List of target language codes (default: all supported)
            
        Returns:
            Dictionary with translations:
            {
                'el': {'item_description': '...', 'notes': '...', 'item_category': '...'},
                'ar': {'item_description': '...', 'notes': '...', 'item_category': '...'},
                ...
            }
        """
        if target_languages is None:
            target_languages = self.target_languages
            
        translations = {}
        
        for lang in target_languages:
            try:
                # Translate description (required)
                translated_description = await self.translate_text(item_description, lang)
                
                # Translate notes (optional)
                translated_notes = None
                if item_notes:
                    translated_notes = await self.translate_text(item_notes, lang)
                
                # Translate category (optional)
                translated_category = None
                if item_category:
                    translated_category = await self.translate_text(item_category, lang)
                
                if translated_description:  # Only add if description translation succeeded
                    translations[lang] = {
                        'item_description': translated_description,
                        'notes': translated_notes,
                        'item_category': translated_category
                    }
                    
            except Exception as e:
                logger.error(f"Failed to translate checklist item to {lang}: {str(e)}")
                continue
        
        return translations
    
    async def translate_multiple_checklist_items(
        self,
        items: List[Dict[str, str]],
        target_languages: Optional[List[str]] = None
    ) -> Dict[int, Dict[str, Dict[str, str]]]:
        """
        Translate multiple checklist items efficiently
        
        Args:
            items: List of items with keys: 'item_description', 'notes', 'item_category'
            target_languages: List of target language codes
            
        Returns:
            Dictionary indexed by item index:
            {
                0: {'el': {'item_description': '...', 'notes': '...'}, 'ar': {...}},
                1: {'el': {'item_description': '...', 'notes': '...'}, 'ar': {...}},
                ...
            }
        """
        if target_languages is None:
            target_languages = self.target_languages
            
        results = {}
        
        # Create translation tasks for all items
        tasks = []
        for i, item in enumerate(items):
            task = self.translate_checklist_item(
                item_description=item.get('item_description', ''),
                item_notes=item.get('notes'),
                item_category=item.get('item_category'),
                target_languages=target_languages
            )
            tasks.append((i, task))
        
        # Execute all translations concurrently
        for i, task in tasks:
            try:
                translations = await task
                results[i] = translations
            except Exception as e:
                logger.error(f"Failed to translate checklist item {i}: {str(e)}")
                results[i] = {}
        
        return results
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported target languages"""
        return self.target_languages.copy()
    
    def is_translation_available(self) -> bool:
        """Check if translation service is available"""
        try:
            # Test with a simple translation
            result = self.translator.translate("test", src='en', dest='es')
            return result is not None
        except Exception as e:
            logger.error(f"Translation service not available: {str(e)}")
            return False

# Global instance
ai_translation_service = AITranslationService()