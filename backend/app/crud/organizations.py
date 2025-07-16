# backend/app/crud/organizations.py
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from .. import models
from ..models import OrganizationType

def get_organization(db: Session, organization_id: uuid.UUID):
    """Retrieves a single organization by its ID with parent and children."""
    return db.query(models.Organization)\
        .options(
            joinedload(models.Organization.parent_organization),
            joinedload(models.Organization.child_organizations)
        )\
        .filter(models.Organization.id == organization_id)\
        .first()

def get_organizations(db: Session, include_inactive: bool = False):
    """Retrieves all organizations with hierarchy information."""
    query = db.query(models.Organization)\
        .options(
            joinedload(models.Organization.parent_organization),
            joinedload(models.Organization.child_organizations)
        )
    
    if not include_inactive:
        query = query.filter(models.Organization.is_active == True)
    
    return query.all()

def get_organizations_by_type(db: Session, organization_type: OrganizationType, include_inactive: bool = False):
    """Retrieves organizations filtered by type."""
    query = db.query(models.Organization)\
        .options(
            joinedload(models.Organization.parent_organization),
            joinedload(models.Organization.child_organizations)
        )\
        .filter(models.Organization.organization_type == organization_type)
    
    if not include_inactive:
        query = query.filter(models.Organization.is_active == True)
    
    return query.all()

def get_organization_hierarchy(db: Session, root_organization_id: uuid.UUID):
    """Retrieves the complete hierarchy starting from a root organization."""
    def build_hierarchy(org_id: uuid.UUID, visited: set = None):
        if visited is None:
            visited = set()
        
        if org_id in visited:
            return None  # Prevent infinite loops
        
        visited.add(org_id)
        
        org = get_organization(db, org_id)
        if not org:
            return None
        
        children = []
        for child in org.child_organizations:
            if child.is_active:
                child_hierarchy = build_hierarchy(child.id, visited.copy())
                if child_hierarchy:
                    children.append(child_hierarchy)
        
        return {
            "organization": org,
            "children": children,
            "depth": 0  # Will be calculated by caller if needed
        }
    
    return build_hierarchy(root_organization_id)

def get_child_organizations(db: Session, parent_id: uuid.UUID, include_inactive: bool = False):
    """Retrieves direct children of an organization."""
    query = db.query(models.Organization)\
        .filter(models.Organization.parent_organization_id == parent_id)
    
    if not include_inactive:
        query = query.filter(models.Organization.is_active == True)
    
    return query.all()

def get_root_organizations(db: Session, include_inactive: bool = False):
    """Retrieves organizations that have no parent (root level)."""
    query = db.query(models.Organization)\
        .filter(models.Organization.parent_organization_id.is_(None))
    
    if not include_inactive:
        query = query.filter(models.Organization.is_active == True)
    
    return query.all()

def create_organization(db: Session, org_data):
    """Creates a new organization with business rule validation."""
    org_dict = org_data.dict()
    
    # Validate business rules
    if org_dict.get('organization_type') == OrganizationType.SUPPLIER:
        if not org_dict.get('parent_organization_id'):
            raise ValueError("Supplier organizations must have a parent organization")
    
    # Check for singleton organizations (Oraseas EE, BossAqua)
    if org_dict.get('organization_type') in [OrganizationType.ORASEAS_EE, OrganizationType.BOSSAQUA]:
        existing = db.query(models.Organization)\
            .filter(models.Organization.organization_type == org_dict['organization_type'])\
            .first()
        if existing:
            raise ValueError(f"Only one {org_dict['organization_type'].value} organization is allowed")
    
    # Validate parent organization exists
    if org_dict.get('parent_organization_id'):
        parent = get_organization(db, org_dict['parent_organization_id'])
        if not parent:
            raise ValueError("Parent organization not found")
        if not parent.is_active:
            raise ValueError("Cannot assign inactive parent organization")
    
    org = models.Organization(**org_dict)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

def update_organization(db: Session, organization_id: uuid.UUID, org_data):
    """Updates an existing organization with business rule validation."""
    org = get_organization(db, organization_id)
    if not org:
        return None
    
    update_dict = org_data.dict(exclude_unset=True)
    
    # Validate business rules for updates
    new_type = update_dict.get('organization_type', org.organization_type)
    new_parent_id = update_dict.get('parent_organization_id', org.parent_organization_id)
    
    if new_type == OrganizationType.SUPPLIER and not new_parent_id:
        raise ValueError("Supplier organizations must have a parent organization")
    
    # Check for singleton constraint if type is changing
    if 'organization_type' in update_dict and update_dict['organization_type'] != org.organization_type:
        if update_dict['organization_type'] in [OrganizationType.ORASEAS_EE, OrganizationType.BOSSAQUA]:
            existing = db.query(models.Organization)\
                .filter(
                    and_(
                        models.Organization.organization_type == update_dict['organization_type'],
                        models.Organization.id != organization_id
                    )
                )\
                .first()
            if existing:
                raise ValueError(f"Only one {update_dict['organization_type'].value} organization is allowed")
    
    # Validate parent organization if changing
    if 'parent_organization_id' in update_dict and update_dict['parent_organization_id']:
        if update_dict['parent_organization_id'] == organization_id:
            raise ValueError("Organization cannot be its own parent")
        
        parent = get_organization(db, update_dict['parent_organization_id'])
        if not parent:
            raise ValueError("Parent organization not found")
        if not parent.is_active:
            raise ValueError("Cannot assign inactive parent organization")
        
        # Check for circular references
        if _would_create_cycle(db, organization_id, update_dict['parent_organization_id']):
            raise ValueError("Update would create a circular reference in organization hierarchy")
    
    for key, value in update_dict.items():
        setattr(org, key, value)
    
    db.commit()
    db.refresh(org)
    return org

def delete_organization(db: Session, organization_id: uuid.UUID):
    """Soft deletes an organization by setting is_active to False."""
    org = get_organization(db, organization_id)
    if not org:
        return None
    
    # Check if organization has active children
    active_children = get_child_organizations(db, organization_id, include_inactive=False)
    if active_children:
        raise ValueError("Cannot delete organization with active child organizations")
    
    # Check if organization has dependencies (users, machines, etc.)
    if org.users or org.machines or org.warehouses:
        # Soft delete instead of hard delete
        org.is_active = False
        db.commit()
        db.refresh(org)
        return org
    else:
        # Hard delete if no dependencies
        db.delete(org)
        db.commit()
        return org

def _would_create_cycle(db: Session, org_id: uuid.UUID, new_parent_id: uuid.UUID) -> bool:
    """Check if setting new_parent_id as parent of org_id would create a cycle."""
    visited = set()
    current_id = new_parent_id
    
    while current_id and current_id not in visited:
        if current_id == org_id:
            return True
        
        visited.add(current_id)
        parent_org = db.query(models.Organization)\
            .filter(models.Organization.id == current_id)\
            .first()
        
        if not parent_org:
            break
        
        current_id = parent_org.parent_organization_id
    
    return False

def search_organizations(db: Session, query: str, organization_type: Optional[OrganizationType] = None, include_inactive: bool = False):
    """Search organizations by name with optional type filtering."""
    search_query = db.query(models.Organization)\
        .options(
            joinedload(models.Organization.parent_organization),
            joinedload(models.Organization.child_organizations)
        )\
        .filter(models.Organization.name.ilike(f"%{query}%"))
    
    if organization_type:
        search_query = search_query.filter(models.Organization.organization_type == organization_type)
    
    if not include_inactive:
        search_query = search_query.filter(models.Organization.is_active == True)
    
    return search_query.all()