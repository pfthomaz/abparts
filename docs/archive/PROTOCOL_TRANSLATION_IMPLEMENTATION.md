# Protocol Translation Implementation Plan

## 🎯 **Objective**
Enable multi-language support for maintenance protocols and checklist items, allowing super admins to create content in English and provide translations for all supported languages.

## 🏗️ **Architecture Overview**

### Database Layer
- **Base Content**: Protocols/items stored in base language (English)
- **Translations**: Separate tables for translated content
- **Fallback Logic**: Display base language if translation missing

### API Layer
- **Language-aware endpoints**: Accept `Accept-Language` header
- **Translation management**: CRUD operations for translations
- **Bulk operations**: Efficient translation management

### Frontend Layer
- **Translation management UI**: For super admins
- **Language-aware display**: For end users
- **Translation status indicators**: Show completion status

## 📋 **Implementation Steps**

### Phase 1: Backend Foundation (Week 1)

#### 1.1 Database Schema
```bash
# Run the migration
alembic upgrade head
```

#### 1.2 Update Existing Models
```python
# Add to maintenance_protocols model
class MaintenanceProtocol(Base):
    # ... existing fields ...
    base_language = Column(String(5), nullable=False, default='en')
    translations = relationship("ProtocolTranslation", back_populates="protocol", cascade="all, delete-orphan")

# Add to checklist_items model  
class ChecklistItem(Base):
    # ... existing fields ...
    base_language = Column(String(5), nullable=False, default='en')
    translations = relationship("ChecklistItemTranslation", back_populates="checklist_item", cascade="all, delete-orphan")
```

#### 1.3 Translation Service
```python
# backend/app/services/translation_service.py
class TranslationService:
    @staticmethod
    def get_localized_protocol(protocol_id: UUID, language: str, db: Session):
        """Get protocol in specified language with fallback"""
        
    @staticmethod
    def get_translation_status(protocol_id: UUID, db: Session):
        """Get translation completion status for all languages"""
        
    @staticmethod
    def create_translation(protocol_id: UUID, translation_data: dict, db: Session):
        """Create or update translation"""
```

### Phase 2: API Endpoints (Week 1-2)

#### 2.1 Translation Management Endpoints
```python
# GET /protocols/{id}/translations - Get all translations for a protocol
# POST /protocols/{id}/translations - Create translation
# PUT /protocols/{id}/translations/{language} - Update translation
# DELETE /protocols/{id}/translations/{language} - Delete translation
# GET /protocols/{id}/translation-status - Get translation status

# Similar endpoints for checklist items
# GET /checklist-items/{id}/translations
# POST /checklist-items/{id}/translations
# etc.
```

#### 2.2 Language-aware Display Endpoints
```python
# GET /protocols?lang=el - Get protocols in Greek (with fallback)
# GET /protocols/{id}?lang=ar - Get specific protocol in Arabic
# GET /protocols/{id}/checklist-items?lang=es - Get items in Spanish
```

### Phase 3: Frontend Translation Management (Week 2)

#### 3.1 Translation Management Interface
```jsx
// TranslationManager.js - Main translation interface
// ProtocolTranslationForm.js - Form for editing protocol translations
// ChecklistTranslationForm.js - Form for editing item translations
// TranslationStatusIndicator.js - Shows completion status
```

#### 3.2 Enhanced Protocol Components
```jsx
// Update existing components to show translation status
// Add language switcher for protocols
// Add "Manage Translations" buttons for super admins
```

### Phase 4: User Experience (Week 3)

#### 4.1 Language-aware Display
```jsx
// Update protocol display to use user's preferred language
// Add fallback indicators when translation missing
// Show available languages for each protocol
```

#### 4.2 Translation Workflow
```jsx
// Translation progress tracking
// Bulk translation tools
// Translation validation
```

## 🎨 **User Interface Design**

### Translation Management Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│ Protocol Translations: "Daily Start of Day"                 │
├─────────────────────────────────────────────────────────────┤
│ Base Language: English ✓                                   │
│                                                             │
│ Translation Status:                                         │
│ 🇬🇷 Greek     ████████░░ 80% (4/5 items) [Manage]        │
│ 🇸🇦 Arabic    ██████░░░░ 60% (3/5 items) [Manage]        │
│ 🇪🇸 Spanish   ░░░░░░░░░░  0% (0/5 items) [Start]         │
│ 🇹🇷 Turkish   ░░░░░░░░░░  0% (0/5 items) [Start]         │
│ 🇳🇴 Norwegian ░░░░░░░░░░  0% (0/5 items) [Start]         │
│                                                             │
│ [Bulk Translate] [Export Translations] [Import]            │
└─────────────────────────────────────────────────────────────┘
```

### Protocol Translation Form
```
┌─────────────────────────────────────────────────────────────┐
│ Translate to Greek (🇬🇷)                                   │
├─────────────────────────────────────────────────────────────┤
│ Protocol Name:                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ English: Daily Start of Day                             │ │
│ │ Greek:   [Ημερήσια Έναρξη Ημέρας                    ] │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Description:                                                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ English: Complete these tasks at start of each day     │ │
│ │ Greek:   [Ολοκληρώστε αυτές τις εργασίες στην       ] │ │
│ │          [αρχή κάθε ημέρας                           ] │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Checklist Items (3/5 translated):                          │
│ ✓ Check oil level → Έλεγχος στάθμης λαδιού                │
│ ✓ Inspect filters → Επιθεώρηση φίλτρων                    │
│ ✗ Test emergency stop → [Not translated] [Add]             │
│                                                             │
│ [Save Draft] [Mark Complete] [Cancel]                      │
└─────────────────────────────────────────────────────────────┘
```

### User View with Language Indicator
```
┌─────────────────────────────────────────────────────────────┐
│ 🇬🇷 Ημερήσια Έναρξη Ημέρας                    [🌍 Languages] │
│ Translated from English                                     │
├─────────────────────────────────────────────────────────────┤
│ Checklist Items:                                            │
│ 1. ✓ Έλεγχος στάθμης λαδιού                               │
│ 2. ✓ Επιθεώρηση φίλτρων                                   │
│ 3. ⚠️ Test emergency stop (English - no translation)       │
│ 4. ✓ Καθαρισμός εξωτερικής επιφάνειας                     │
│ 5. ✓ Έλεγχος λειτουργίας συναγερμών                       │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 **Technical Implementation Details**

### Backend Service Layer
```python
class ProtocolTranslationService:
    def get_localized_protocol(self, protocol_id: UUID, user_language: str):
        """
        Returns protocol in user's preferred language with fallback logic:
        1. Try user's preferred language
        2. Fall back to base language (English)
        3. Mark which fields are translated vs fallback
        """
        
    def get_translation_completeness(self, protocol_id: UUID):
        """
        Returns translation status for all supported languages:
        - Total items count
        - Translated items per language
        - Completion percentage
        """
        
    def bulk_translate_protocol(self, protocol_id: UUID, target_language: str, translations: dict):
        """
        Efficiently update multiple translations at once
        """
```

### Frontend Translation Hook
```javascript
// hooks/useProtocolTranslations.js
export const useProtocolTranslations = (protocolId) => {
  const { currentLanguage } = useLocalization();
  
  const {
    protocol,
    isTranslated,
    availableLanguages,
    translationStatus
  } = useQuery(['protocol', protocolId, currentLanguage], 
    () => fetchLocalizedProtocol(protocolId, currentLanguage)
  );
  
  return {
    protocol,
    isTranslated,
    availableLanguages,
    translationStatus,
    switchLanguage: (lang) => setLanguage(lang)
  };
};
```

## 📊 **Benefits & Impact**

### Business Benefits
- **Safety Compliance**: Workers understand procedures in native language
- **Reduced Errors**: Clear instructions prevent maintenance mistakes  
- **Global Scalability**: Easy expansion to new markets/languages
- **Training Efficiency**: Faster onboarding for non-English speakers

### Technical Benefits
- **Maintainable**: Clean separation of content and translations
- **Performant**: Efficient queries with proper indexing
- **Scalable**: Easy to add new languages
- **Robust**: Fallback mechanisms prevent broken experiences

## 🚀 **Future Enhancements**

### Phase 2 Features
- **AI Translation Integration**: Auto-generate initial translations
- **Translation Workflow**: Review and approval process
- **Version Control**: Track translation changes over time
- **Community Translations**: Allow users to contribute translations

### Advanced Features
- **Context-aware Translations**: Different translations for different contexts
- **Media Translations**: Support for images, videos with text
- **Offline Support**: Download translations for offline use
- **Analytics**: Track which languages are most used

## 📋 **Implementation Checklist**

### Backend Tasks
- [ ] Create database migration
- [ ] Add translation models
- [ ] Create translation service
- [ ] Add translation endpoints
- [ ] Update existing protocol endpoints
- [ ] Add language detection middleware
- [ ] Create translation status endpoints

### Frontend Tasks  
- [ ] Create translation management components
- [ ] Update protocol display components
- [ ] Add language switcher
- [ ] Create translation forms
- [ ] Add translation status indicators
- [ ] Update navigation for translation management
- [ ] Add bulk translation tools

### Testing & Quality
- [ ] Unit tests for translation service
- [ ] API endpoint tests
- [ ] Frontend component tests
- [ ] End-to-end translation workflow tests
- [ ] Performance testing with large datasets
- [ ] Accessibility testing for RTL languages

This implementation provides a solid foundation for multi-language protocol support while maintaining performance and user experience quality.