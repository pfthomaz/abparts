# backend/app/routers/security.py

import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ..database import get_db
from ..models import User, AuditLog, SecurityEventLog
from ..auth import get_current_user_object as get_current_user
from ..enhanced_organizational_isolation import (
    EnhancedOrganizationalDataFilter,
    EnhancedSupplierVisibilityControl,
    EnhancedBossAquaAccessControl
)
from ..enhanced_audit_system import EnhancedAuditSystem, AuditContext
from ..security_decorators import (
    validate_organizational_isolation,
    audit_data_access,
    extract_id_from_path
)

def get_user_role_value(user: User) -> str:
    """Helper function to get role value from User object"""
    if hasattr(user.role, 'value'):
        return user.role.value
    elif isinstance(user.role, str):
        return user.role
    else:
        return str(user.role)

router = APIRouter(prefix="/security", tags=["security"])

# Pydantic schemas for security endpoints
from pydantic import BaseModel, UUID4
from typing import Dict, Any

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    user_id: uuid.UUID
    organization_id: Optional[uuid.UUID]
    resource_type: str
    resource_id: uuid.UUID
    action: str
    old_values: Optional[str]
    new_values: Optional[str]
    details: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    endpoint: Optional[str]
    http_method: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class SecurityEventResponse(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    event_type: str
    severity: str
    user_id: Optional[uuid.UUID]
    organization_id: Optional[uuid.UUID]
    description: str
    details: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    endpoint: Optional[str]
    resolved: str
    resolved_at: Optional[datetime]
    resolved_by: Optional[uuid.UUID]
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrganizationAccessValidation(BaseModel):
    user_id: uuid.UUID
    target_organization_id: uuid.UUID
    access_granted: bool
    reason: str

class SecurityEventUpdate(BaseModel):
    resolved: str
    resolution_notes: Optional[str] = None

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resource_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs with organizational filtering"""
    
    # Only superadmin can view all audit logs
    if get_user_role_value(current_user) != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can access audit logs"
        )
    
    query = db.query(AuditLog)
    
    # Apply filters
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    # Create audit context for this request
    audit_context = AuditContext(current_user)
    
    # If not superadmin, filter by accessible organizations
    if get_user_role_value(current_user) != "super_admin":
        accessible_org_ids = EnhancedOrganizationalDataFilter.get_accessible_organization_ids(
            current_user, db, audit_context
        )
        query = query.filter(AuditLog.organization_id.in_(accessible_org_ids))
    
    audit_logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    return audit_logs

@router.get("/security-events", response_model=List[SecurityEventResponse])
async def get_security_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = Query(None),
    resolved: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security events with organizational filtering"""
    
    # Only superadmin and admin can view security events
    user_role = get_user_role_value(current_user)
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access security events"
        )
    
    query = db.query(SecurityEventLog)
    
    # Apply filters
    if severity:
        query = query.filter(SecurityEventLog.severity == severity)
    
    if resolved:
        query = query.filter(SecurityEventLog.resolved == resolved)
    
    if start_date:
        query = query.filter(SecurityEventLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(SecurityEventLog.timestamp <= end_date)
    
    # If not superadmin, filter by organization
    if user_role != "super_admin":
        query = query.filter(SecurityEventLog.organization_id == current_user.organization_id)
    
    security_events = query.order_by(desc(SecurityEventLog.timestamp)).offset(skip).limit(limit).all()
    return security_events

@router.put("/security-events/{event_id}", response_model=SecurityEventResponse)
async def update_security_event(
    event_id: uuid.UUID,
    event_update: SecurityEventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update security event resolution status"""
    
    # Only superadmin and admin can update security events
    user_role = get_user_role_value(current_user)
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update security events"
        )
    
    security_event = db.query(SecurityEventLog).filter(SecurityEventLog.id == event_id).first()
    if not security_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security event not found"
        )
    
    # Non-superadmin can only update events from their organization
    if user_role != "super_admin" and security_event.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update security events from other organizations"
        )
    
    # Update the event
    security_event.resolved = event_update.resolved
    security_event.resolution_notes = event_update.resolution_notes
    security_event.resolved_by = current_user.id
    security_event.resolved_at = datetime.utcnow()
    security_event.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(security_event)
    
    return security_event

@router.get("/validate-organization-access", response_model=OrganizationAccessValidation)
async def validate_organization_access(
    target_organization_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate if current user can access target organization data"""
    
    audit_context = AuditContext(current_user)
    validation_result = EnhancedOrganizationalDataFilter.validate_organization_access(
        current_user, target_organization_id, db, audit_context
    )
    access_granted = validation_result["allowed"]
    
    reason = validation_result["reason"]
    
    return OrganizationAccessValidation(
        user_id=current_user.id,
        target_organization_id=target_organization_id,
        access_granted=access_granted,
        reason=reason
    )

@router.get("/accessible-organizations")
async def get_accessible_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of organizations accessible to current user"""
    
    audit_context = AuditContext(current_user)
    accessible_org_ids = EnhancedOrganizationalDataFilter.get_accessible_organization_ids(
        current_user, db, audit_context
    )
    
    from ..models import Organization
    organizations = db.query(Organization).filter(Organization.id.in_(accessible_org_ids)).all()
    
    return {
        "user_id": current_user.id,
        "user_role": get_user_role_value(current_user),
        "accessible_organization_count": len(accessible_org_ids),
        "organizations": [
            {
                "id": org.id,
                "name": org.name,
                "organization_type": org.organization_type.value if hasattr(org.organization_type, 'value') else str(org.organization_type),
                "country": org.country
            }
            for org in organizations
        ]
    }

@router.get("/visible-suppliers")
async def get_visible_suppliers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get suppliers visible to current user based on organizational relationships"""
    
    audit_context = AuditContext(current_user)
    visible_suppliers = EnhancedSupplierVisibilityControl.get_visible_suppliers(
        current_user, db, audit_context
    )
    
    return {
        "user_id": current_user.id,
        "user_organization_id": current_user.organization_id,
        "visible_supplier_count": len(visible_suppliers),
        "suppliers": [
            {
                "id": supplier.id,
                "name": supplier.name,
                "parent_organization_id": supplier.parent_organization_id,
                "country": supplier.country,
                "is_active": supplier.is_active
            }
            for supplier in visible_suppliers
        ]
    }

@router.get("/validate-bossaqua-access")
async def validate_bossaqua_access(
    action: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate if current user can access BossAqua organization data"""
    
    audit_context = AuditContext(current_user)
    access_granted = EnhancedBossAquaAccessControl.validate_bossaqua_access(
        current_user, action, audit_context, db
    )
    
    return {
        "user_id": current_user.id,
        "user_role": get_user_role_value(current_user),
        "action": action,
        "access_granted": access_granted,
        "reason": "Only superadmin can access BossAqua data initially" if not access_granted else "Access granted"
    }