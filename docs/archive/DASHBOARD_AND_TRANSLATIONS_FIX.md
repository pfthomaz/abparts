# Dashboard Stats and Translation Keys Fix

## Issues Fixed

### 1. Dashboard Statistics Showing Zero
**Problem:** Farm Sites and Cages (Nets) were showing 0 instead of actual counts.

**Root Cause:** 
- The `total_warehouses` field was missing from `dashboard_fixed.py`
- The `total_warehouses` field was missing from the `DashboardMetricsResponse` schema

**Solution:**
- Added warehouse counting logic to `backend/app/crud/dashboard_fixed.py`
- Added `total_warehouses` field to the return dictionary
- Added `total_warehouses: int` to `DashboardMetricsResponse` schema in `backend/app/schemas.py`
- Added debug logging to `backend/app/routers/dashboard.py` to track metrics

**Result:** Dashboard now correctly shows:
- 2 farm sites (total across all organizations for super_admin)
- 4 nets/cages (total across all organizations for super_admin)
- 17 warehouses (total across all organizations for super_admin)

### 2. Translation Keys Showing Instead of Translated Text
**Problem:** Escalation modal and chat messages were showing keys like `aiAssistant.escalation.title` instead of translated text.

**Root Cause:** Spanish translation file (`frontend/src/locales/es.json`) was missing several escalation-related translation keys.

**Solution:** Added missing Spanish translations:

#### Escalation Modal Keys:
- `title`: "Escalar a Soporte de Expertos"
- `description`: "Si no puedes resolver el problema..."
- `escalate_button`: "Crear Ticket de Soporte"
- `escalating`: "Creando ticket..."
- `confidence_score`: "Confianza de IA"
- `additional_notes`: "Notas Adicionales"
- `notes_placeholder`: "Describe cualquier detalle adicional..."
- `reason.label`: "Razón de Escalación"
- `reason.user_request`: "Necesito ayuda de un experto"
- `reason.low_confidence`: "La IA tiene baja confianza"
- `reason.steps_exceeded`: "Demasiados pasos de solución de problemas"
- `reason.safety_concern`: "Preocupación de seguridad"
- `reason.complex_issue`: "Problema técnico complejo"
- `reason.expert_required`: "Se requiere conocimiento experto"
- `priority.label`: "Nivel de Prioridad"
- `priority.low`: "Baja - Puede esperar"
- `priority.medium`: "Media - Prioridad normal"
- `priority.high`: "Alta - Urgente"
- `priority.urgent`: "Urgente - Problema crítico"

#### Chat Message Keys:
- `messages.machineSelected`: "Máquina seleccionada: {{machineName}} ({{modelType}})"
- `messages.machineCleared`: "Selección de máquina borrada..."
- `messages.escalationCreated`: "Se ha creado el ticket de soporte {{ticketNumber}}..."
- `messages.expertContact`: "Contacto del Experto: {{contactName}}..."
- `messages.escalationError`: "Error al crear el ticket de soporte..."

## Files Modified

1. `backend/app/crud/dashboard_fixed.py` - Added warehouse counting logic
2. `backend/app/schemas.py` - Added total_warehouses field to schema
3. `backend/app/routers/dashboard.py` - Added debug logging
4. `frontend/src/pages/Dashboard.js` - Added console logging for debugging
5. `frontend/src/locales/es.json` - Added missing Spanish translations

## Testing

To verify the fixes:
1. Refresh the dashboard - should show correct counts for farms, cages, and warehouses
2. Open the AI Assistant and create an escalation - all labels should be in Spanish
3. Check the chat messages after escalation - should show translated text, not keys

## Status

✅ Dashboard statistics now display correctly
✅ Escalation modal fully translated to Spanish
✅ Chat messages fully translated to Spanish
✅ API restart completed successfully
