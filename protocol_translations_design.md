# Protocol Multi-Language Implementation Design

## Database Schema Changes

### New Tables

#### `protocol_translations`
```sql
CREATE TABLE protocol_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    protocol_id UUID NOT NULL REFERENCES maintenance_protocols(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL, -- 'en', 'el', 'ar', 'es', 'tr', 'no'
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(protocol_id, language_code)
);
```

#### `checklist_item_translations`
```sql
CREATE TABLE checklist_item_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checklist_item_id UUID NOT NULL REFERENCES checklist_items(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL,
    item_description TEXT NOT NULL,
    notes TEXT,
    item_category TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(checklist_item_id, language_code)
);
```

### Modified Existing Tables

#### `maintenance_protocols` - Add base language
```sql
ALTER TABLE maintenance_protocols 
ADD COLUMN base_language VARCHAR(5) DEFAULT 'en' NOT NULL;
```

#### `checklist_items` - Add base language
```sql
ALTER TABLE checklist_items 
ADD COLUMN base_language VARCHAR(5) DEFAULT 'en' NOT NULL;
```

## Implementation Approaches

### Option 1: Manual Translation (Recommended for Start)
- Super admins create protocols in English (base language)
- Translation interface allows adding translations for each supported language
- Fallback to base language if translation missing

### Option 2: AI-Assisted Translation (Future Enhancement)
- Integrate with translation services (Google Translate, Azure Translator)
- Auto-generate initial translations that can be manually refined
- Quality control workflow for translation approval

### Option 3: Hybrid Approach (Best Long-term)
- Start with manual translations for critical protocols
- Use AI for initial drafts of new protocols
- Community/expert review system for translation quality

## User Experience Flow

### For Super Admins (Protocol Creation)
1. Create protocol in base language (English)
2. Access "Manage Translations" for each protocol
3. Add/edit translations for each supported language
4. Mark translations as "Complete" or "Draft"

### For End Users (Protocol Viewing)
1. System detects user's preferred language
2. Shows translated version if available and complete
3. Falls back to base language with indicator
4. Option to switch languages manually

## Technical Implementation

### Backend Changes
- New translation models and CRUD operations
- Modified protocol/checklist APIs to include translations
- Language-aware endpoints with fallback logic

### Frontend Changes
- Translation management interface for super admins
- Language-aware protocol display components
- Translation status indicators
- Language switcher for protocols

## Translation Management UI

### Protocol Translation Interface
```
┌─────────────────────────────────────────┐
│ Protocol: "Daily Start of Day"          │
│ Base Language: English                  │
├─────────────────────────────────────────┤
│ Translations:                           │
│ 🇬🇷 Greek     [Complete] [Edit]        │
│ 🇸🇦 Arabic    [Draft]    [Edit]        │
│ 🇪🇸 Spanish   [Missing]  [Add]         │
│ 🇹🇷 Turkish   [Missing]  [Add]         │
│ 🇳🇴 Norwegian [Missing]  [Add]         │
└─────────────────────────────────────────┘
```

### Checklist Item Translation
```
┌─────────────────────────────────────────┐
│ Item: "Check oil level and top up"      │
│ ┌─────────────────────────────────────┐ │
│ │ 🇬🇷 Greek Translation              │ │
│ │ ┌─────────────────────────────────┐ │ │
│ │ │ Έλεγχος στάθμης λαδιού και     │ │ │
│ │ │ συμπλήρωση εάν χρειάζεται      │ │ │
│ │ └─────────────────────────────────┘ │ │
│ │ Notes: [Optional translation]       │ │
│ │ Category: Μηχανικά                 │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Benefits

### Business Benefits
- Improved safety compliance across regions
- Reduced training time for non-English speakers
- Better adoption rates in international markets
- Consistent maintenance procedures globally

### Technical Benefits
- Scalable to new languages
- Maintains data integrity with fallbacks
- SEO benefits for different regions
- Audit trail for translation changes

## Implementation Phases

### Phase 1: Foundation (2-3 weeks)
- Database schema changes
- Basic translation CRUD APIs
- Simple translation management UI

### Phase 2: Enhanced UX (2-3 weeks)
- Advanced translation interface
- Bulk translation tools
- Translation status tracking

### Phase 3: Automation (Future)
- AI translation integration
- Translation workflow management
- Quality assurance tools

## Considerations

### Data Migration
- Existing protocols become "English" base language
- Create migration script to populate base translations

### Performance
- Eager loading of translations
- Caching strategies for frequently accessed protocols
- Database indexing on language_code

### Quality Control
- Translation review workflow
- Version control for translations
- Translation completeness metrics

### Fallback Strategy
- Always show base language if translation missing
- Clear indicators when viewing non-native language
- Option to contribute missing translations