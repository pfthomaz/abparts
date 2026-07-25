# Maintenance Delete Feature - Implementation Plan

## Overview

Add the ability for admins and super-admins to delete maintenance execution records (e.g., started by mistake) and for super-admins to delete maintenance protocol templates.

## Requirements

### 1. Delete Execution Records
- **Who**: Admin and Super-admin users
- **What**: Delete ongoing or completed maintenance execution records
- **Why**: Remove records started by mistake or incorrect data
- **Where**: Execution History view

### 2. Delete Protocol Templates
- **Who**: Super-admin only
- **What**: Delete maintenance protocol templates
- **Why**: Remove obsolete or incorrect protocol templates
- **Where**: Maintenance Protocols management page

## Permissions

| Action | User | Admin | Super-admin |
|--------|------|-------|-------------|
| Delete own execution | ❌ | ✅ | ✅ |
| Delete any execution in org | ❌ | ✅ | ✅ |
| Delete protocol template | ❌ | ❌ | ✅ |

## Backend Implementation

### 1. CRUD Functions (backend/app/crud/maintenance_protocols.py)

#### Already Added:
```python
def delete_execution(db: Session, execution_id: uuid.UUID) -> bool:
    """Delete a maintenance execution and its related checklist completions."""
    execution = get_execution(db, execution_id)
    if not execution:
        return False
    
    # Delete related checklist completions first
    db.query(models.MaintenanceChecklistCompletion).filter(
        models.MaintenanceChecklistCompletion.execution_id == execution_id
    ).delete()
    
    # Delete the execution
    db.delete(execution)
    db.commit()
    return True
```

#### Already Exists:
```python
def delete_protocol(db: Session, protocol_id: uuid.UUID) -> bool:
    """Delete a protocol."""
    # Already implemented - checks for executions before deleting
```

### 2. Router Endpoints (backend/app/routers/maintenance_protocols.py)

#### Add Delete Execution Endpoint:
```python
@router.delete("/executions/{execution_id}", status_code=204)
def delete_execution(
    execution_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a maintenance execution. Admin and super-admin only."""
    # Check if user is admin or super-admin
    if not permission_checker.is_admin(current_user) and not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only admins can delete maintenance executions")
    
    # Verify execution exists and belongs to user's organization
    execution = db.query(models.MaintenanceExecution).filter(
        models.MaintenanceExecution.id == execution_id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Verify execution belongs to user's organization
    machine = db.query(models.Machine).filter(
        models.Machine.id == execution.machine_id
    ).first()
    
    if machine.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Cannot delete execution from another organization")
    
    # Delete the execution
    success = crud_maintenance.delete_execution(db=db, execution_id=execution_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete execution")
```

#### Protocol Delete Already Exists:
```python
@router.delete("/{protocol_id}", status_code=204)
def delete_protocol(
    protocol_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MAINTENANCE, PermissionType.DELETE))
):
    """Delete a maintenance protocol. Super admin only."""
    # Already checks for super-admin and existing executions
```

## Frontend Implementation

### 1. Service Functions (frontend/src/services/maintenanceProtocolsService.js)

```javascript
export const deleteExecution = async (executionId) => {
  return api.delete(`/maintenance-protocols/executions/${executionId}`);
};

export const deleteProtocol = async (protocolId) => {
  return api.delete(`/maintenance-protocols/${protocolId}`);
};
```

### 2. ExecutionHistory Component (frontend/src/components/ExecutionHistory.js)

Add delete button in detail view:

```javascript
// In the detail view header, add delete button for admins
{(user.role === 'admin' || user.role === 'super_admin') && (
  <button
    onClick={() => handleDeleteExecution(selectedExecution.id)}
    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
  >
    {t('common.delete')}
  </button>
)}

const handleDeleteExecution = async (executionId) => {
  if (!window.confirm(t('maintenance.confirmDeleteExecution'))) {
    return;
  }
  
  try {
    await deleteExecution(executionId);
    setSelectedExecution(null);
    onRefresh();
    // Show success message
  } catch (err) {
    alert(t('maintenance.failedToDeleteExecution', { error: err.message }));
  }
};
```

### 3. MaintenanceProtocols Page (frontend/src/pages/MaintenanceProtocols.js)

Add delete button for super-admins:

```javascript
// In protocol list/detail view
{user.role === 'super_admin' && (
  <button
    onClick={() => handleDeleteProtocol(protocol.id)}
    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
  >
    {t('common.delete')}
  </button>
)}

const handleDeleteProtocol = async (protocolId) => {
  if (!window.confirm(t('maintenance.confirmDeleteProtocol'))) {
    return;
  }
  
  try {
    await deleteProtocol(protocolId);
    loadProtocols(); // Refresh list
    // Show success message
  } catch (err) {
    if (err.message.includes('execution records')) {
      alert(t('maintenance.cannotDeleteProtocolWithExecutions'));
    } else {
      alert(t('maintenance.failedToDeleteProtocol', { error: err.message }));
    }
  }
};
```

## Translation Keys

Add to all 6 language files:

### English (en.json)
```json
"maintenance": {
  "confirmDeleteExecution": "Are you sure you want to delete this maintenance execution? This action cannot be undone.",
  "failedToDeleteExecution": "Failed to delete execution: {{error}}",
  "executionDeletedSuccessfully": "Maintenance execution deleted successfully",
  "confirmDeleteProtocol": "Are you sure you want to delete this protocol template? This action cannot be undone.",
  "failedToDeleteProtocol": "Failed to delete protocol: {{error}}",
  "protocolDeletedSuccessfully": "Protocol template deleted successfully",
  "cannotDeleteProtocolWithExecutions": "Cannot delete protocol. It has execution records. Consider deactivating instead."
}
```

### Greek (el.json)
```json
"maintenance": {
  "confirmDeleteExecution": "Είστε σίγουροι ότι θέλετε να διαγράψετε αυτή την εκτέλεση συντήρησης; Αυτή η ενέργεια δεν μπορεί να αναιρεθεί.",
  "failedToDeleteExecution": "Αποτυχία διαγραφής εκτέλεσης: {{error}}",
  "executionDeletedSuccessfully": "Η εκτέλεση συντήρησης διαγράφηκε με επιτυχία",
  "confirmDeleteProtocol": "Είστε σίγουροι ότι θέλετε να διαγράψετε αυτό το πρότυπο πρωτοκόλλου; Αυτή η ενέργεια δεν μπορεί να αναιρεθεί.",
  "failedToDeleteProtocol": "Αποτυχία διαγραφής πρωτοκόλλου: {{error}}",
  "protocolDeletedSuccessfully": "Το πρότυπο πρωτοκόλλου διαγράφηκε με επιτυχία",
  "cannotDeleteProtocolWithExecutions": "Δεν είναι δυνατή η διαγραφή του πρωτοκόλλου. Έχει εγγραφές εκτέλεσης. Εξετάστε το ενδεχόμενο απενεργοποίησης."
}
```

Similar translations needed for: Spanish, Norwegian, Turkish, Arabic

## UI/UX Considerations

### Delete Button Placement

**Execution History:**
- Show delete button in detail view header (next to "Back to History")
- Only visible to admin and super-admin users
- Red color to indicate destructive action
- Confirmation dialog before deletion

**Protocol Management:**
- Show delete button in protocol detail/edit view
- Only visible to super-admin users
- Red color with warning styling
- Confirmation dialog with warning about permanence
- Error message if protocol has executions

### Visual Design

```
┌─────────────────────────────────────────┐
│ ← Back to History    [Resume] [Delete]  │ <- Admin/Super-admin only
├─────────────────────────────────────────┤
│ Execution Details                        │
│ ...                                      │
└─────────────────────────────────────────┘
```

### Confirmation Dialogs

**Delete Execution:**
```
⚠️ Delete Maintenance Execution?

Are you sure you want to delete this maintenance execution?
This action cannot be undone.

[Cancel]  [Delete]
```

**Delete Protocol:**
```
⚠️ Delete Protocol Template?

Are you sure you want to delete this protocol template?
This will permanently remove the template and cannot be undone.

Note: Protocols with execution records cannot be deleted.

[Cancel]  [Delete]
```

## Security Considerations

1. **Permission Checks**: Verify user role on both frontend and backend
2. **Organization Scope**: Users can only delete executions from their organization
3. **Audit Trail**: Consider logging deletions for audit purposes
4. **Cascade Deletes**: Ensure checklist completions are deleted with executions
5. **Protocol Protection**: Prevent deletion of protocols with execution history

## Testing Checklist

### Backend Tests
- [ ] Delete execution as admin - success
- [ ] Delete execution as regular user - forbidden
- [ ] Delete execution from another org - forbidden
- [ ] Delete non-existent execution - 404
- [ ] Delete protocol as super-admin - success
- [ ] Delete protocol with executions - error
- [ ] Delete protocol as admin - forbidden

### Frontend Tests
- [ ] Delete button visible for admins
- [ ] Delete button hidden for regular users
- [ ] Confirmation dialog appears
- [ ] Successful deletion refreshes list
- [ ] Error messages display correctly
- [ ] Deleted execution removed from history
- [ ] Protocol delete shows appropriate errors

### Integration Tests
- [ ] Delete ongoing execution
- [ ] Delete completed execution
- [ ] Delete execution with checklist completions
- [ ] Attempt to delete protocol with executions
- [ ] Delete unused protocol successfully

## Implementation Steps

1. ✅ **Backend CRUD** - Add delete_execution function
2. **Backend Router** - Add DELETE /executions/{id} endpoint
3. **Frontend Service** - Add deleteExecution and deleteProtocol functions
4. **Frontend UI** - Add delete buttons to ExecutionHistory
5. **Frontend UI** - Add delete button to MaintenanceProtocols
6. **Translations** - Add all translation keys to 6 languages
7. **Permissions** - Add permission checks in frontend
8. **Testing** - Test all scenarios
9. **Documentation** - Update user manual

## Files to Modify

### Backend
- ✅ `backend/app/crud/maintenance_protocols.py` - Add delete_execution
- `backend/app/routers/maintenance_protocols.py` - Add DELETE endpoint

### Frontend
- `frontend/src/services/maintenanceProtocolsService.js` - Add delete functions
- `frontend/src/components/ExecutionHistory.js` - Add delete button
- `frontend/src/pages/MaintenanceProtocols.js` - Add delete button
- `frontend/src/locales/en.json` - Add translations
- `frontend/src/locales/el.json` - Add translations
- `frontend/src/locales/es.json` - Add translations
- `frontend/src/locales/no.json` - Add translations
- `frontend/src/locales/tr.json` - Add translations
- `frontend/src/locales/ar.json` - Add translations

## Status

**Current**: Planning complete, CRUD function added
**Next**: Implement router endpoint and frontend UI
**Estimated Time**: 1-2 hours for full implementation and testing
