# backend/app/crud/organizations.py
import uuid
from typing import List, Optional, Set
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from .. import models
from ..models import OrganizationType
from ..schemas import OrganizationHierarchyNode

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
    
    # Convert string organization_type to model enum if needed
    org_type = org_dict.get('organization_type')
    if isinstance(org_type, str):
        try:
            org_type = OrganizationType(org_type)
            org_dict['organization_type'] = org_type
        except ValueError:
            raise ValueError(f"Invalid organization type: {org_type}")
    
    # Validate business rules
    if org_type == OrganizationType.supplier:
        if not org_dict.get('parent_organization_id'):
            raise ValueError("Supplier organizations must have a parent organization")
    
    # Check for singleton organizations (Oraseas EE, BossAqua)
    if org_type in [OrganizationType.oraseas_ee, OrganizationType.bossaqua]:
        existing = db.query(models.Organization)\
            .filter(models.Organization.organization_type == org_type)\
            .first()
        if existing:
            raise ValueError(f"Only one {org_type.value} organization is allowed")
    
    # Validate parent organization exists
    if org_dict.get('parent_organization_id'):
        parent = get_organization(db, org_dict['parent_organization_id'])
        if not parent:
            raise ValueError("Parent organization not found")
        if not parent.is_active:
            raise ValueError("Cannot assign inactive parent organization")
    
    # Temporarily remove country field until DB migration is complete
    org_dict_filtered = {k: v for k, v in org_dict.items() if k != 'country'}
    
    org = models.Organization(**org_dict_filtered)
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Auto-create default warehouse for customer organizations
    if org.organization_type == OrganizationType.customer:
        _create_default_warehouse_for_organization(db, org)
    
    return org

def update_organization(db: Session, organization_id: uuid.UUID, org_data):
    """Updates an existing organization with business rule validation."""
    org = get_organization(db, organization_id)
    if not org:
        return None
    
    update_dict = org_data.dict(exclude_unset=True)
    
    # Convert string organization_type to model enum if needed
    if 'organization_type' in update_dict:
        org_type = update_dict['organization_type']
        if isinstance(org_type, str):
            try:
                org_type = OrganizationType(org_type)
                update_dict['organization_type'] = org_type
            except ValueError:
                raise ValueError(f"Invalid organization type: {org_type}")
    
    # Validate business rules for updates
    new_type = update_dict.get('organization_type', org.organization_type)
    new_parent_id = update_dict.get('parent_organization_id', org.parent_organization_id)
    
    if new_type == OrganizationType.supplier and not new_parent_id:
        raise ValueError("Supplier organizations must have a parent organization")
    
    # Check for singleton constraint if type is changing
    if 'organization_type' in update_dict and update_dict['organization_type'] != org.organization_type:
        if update_dict['organization_type'] in [OrganizationType.oraseas_ee, OrganizationType.bossaqua]:
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
    # Use try-catch to handle potential database schema issues gracefully
    has_dependencies = False
    try:
        # Check for users
        if org.users:
            has_dependencies = True
    except Exception as e:
        # If there's an error accessing users, rollback and assume there are dependencies
        db.rollback()
        has_dependencies = True
    
    try:
        # Check for machines
        if not has_dependencies and org.machines:
            has_dependencies = True
    except Exception as e:
        # If there's an error accessing machines, rollback and assume there are dependencies
        db.rollback()
        has_dependencies = True
    
    try:
        # Check for warehouses
        if not has_dependencies and org.warehouses:
            has_dependencies = True
    except Exception as e:
        # If there's an error accessing warehouses, rollback and assume there are dependencies
        db.rollback()
        has_dependencies = True
    
    # Always do soft delete to avoid further database issues
    # This is safer and preserves data integrity
    try:
        org.is_active = False
        db.commit()
        db.refresh(org)
        return org
    except Exception as e:
        db.rollback()
        raise e

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

def get_potential_parent_organizations(db: Session, organization_type: OrganizationType):
    """
    Returns organizations that can serve as parents for the given organization type.
    
    Business rules:
    - For suppliers: Return active Customer and Oraseas EE organizations
    - For other types: Return empty list (no parent allowed)
    """
    if organization_type == OrganizationType.supplier:
        # Suppliers can have Customer or Oraseas EE organizations as parents
        return db.query(models.Organization)\
            .filter(
                and_(
                    models.Organization.is_active == True,
                    or_(
                        models.Organization.organization_type == OrganizationType.customer,
                        models.Organization.organization_type == OrganizationType.oraseas_ee
                    )
                )
            )\
            .order_by(models.Organization.name)\
            .all()
    else:
        # Other organization types don't have parents
        return []

def validate_organization_data(db: Session, org_data, org_id: Optional[uuid.UUID] = None):
    """
    Validates organization data without creating/updating the organization.
    Returns structured validation results.
    
    Args:
        db: Database session
        org_data: Organization data to validate (dict or Pydantic model)
        org_id: Optional organization ID for update validation
    
    Returns:
        dict: {"valid": bool, "errors": [{"field": str, "message": str}]}
    """
    errors = []
    
    # Convert Pydantic model to dict if needed
    if hasattr(org_data, 'dict'):
        org_dict = org_data.dict()
    else:
        org_dict = org_data
    
    # Get current organization if this is an update
    current_org = None
    if org_id:
        current_org = get_organization(db, org_id)
        if not current_org:
            errors.append({"field": "id", "message": "Organization not found"})
            return {"valid": False, "errors": errors}
    
    # Determine effective values (new values or current values for updates)
    org_type = org_dict.get('organization_type')
    if org_type is None and current_org:
        org_type = current_org.organization_type
    
    # Convert string to enum if needed
    if isinstance(org_type, str):
        try:
            org_type = OrganizationType(org_type)
        except ValueError:
            errors.append({
                "field": "organization_type",
                "message": f"Invalid organization type: {org_type}"
            })
            return {"valid": False, "errors": errors}
    
    parent_id = org_dict.get('parent_organization_id')
    if parent_id is None and current_org:
        parent_id = current_org.parent_organization_id
    
    # Validate supplier parent requirement
    if org_type == OrganizationType.supplier:
        if not parent_id:
            errors.append({
                "field": "parent_organization_id", 
                "message": "Supplier organizations must have a parent organization"
            })
    
    # Check for singleton organizations (Oraseas EE, BossAqua)
    if org_type in [OrganizationType.oraseas_ee, OrganizationType.bossaqua]:
        query = db.query(models.Organization)\
            .filter(models.Organization.organization_type == org_type)
        
        # Exclude current organization if this is an update
        if org_id:
            query = query.filter(models.Organization.id != org_id)
        
        existing = query.first()
        if existing:
            errors.append({
                "field": "organization_type",
                "message": f"Only one {org_type.value} organization is allowed"
            })
    
    # Validate parent organization if specified
    if parent_id:
        # Check if organization would be its own parent
        if org_id and str(parent_id) == str(org_id):
            errors.append({
                "field": "parent_organization_id",
                "message": "Organization cannot be its own parent"
            })
        else:
            # Check if parent exists and is active
            try:
                parent_uuid = parent_id if isinstance(parent_id, uuid.UUID) else uuid.UUID(str(parent_id))
                parent = get_organization(db, parent_uuid)
            except ValueError:
                # Invalid UUID format
                errors.append({
                    "field": "parent_organization_id",
                    "message": "Invalid parent organization ID format"
                })
                parent = None
            if not parent:
                errors.append({
                    "field": "parent_organization_id",
                    "message": "Parent organization not found"
                })
            elif not parent.is_active:
                errors.append({
                    "field": "parent_organization_id",
                    "message": "Cannot assign inactive parent organization"
                })
            else:
                # Check for circular references (only for updates)
                if org_id:
                    # Convert to UUID objects for the cycle check
                    try:
                        org_uuid = org_id if isinstance(org_id, uuid.UUID) else uuid.UUID(str(org_id))
                        parent_uuid = parent_id if isinstance(parent_id, uuid.UUID) else uuid.UUID(str(parent_id))
                        if _would_create_cycle(db, org_uuid, parent_uuid):
                            errors.append({
                                "field": "parent_organization_id",
                                "message": "Update would create a circular reference in organization hierarchy"
                            })
                    except ValueError:
                        # Invalid UUID format
                        errors.append({
                            "field": "parent_organization_id",
                            "message": "Invalid parent organization ID format"
                        })
    
    # Validate name is provided and not empty
    name = org_dict.get('name')
    if name is None and current_org:
        name = current_org.name
    
    if not name or not name.strip():
        errors.append({
            "field": "name",
            "message": "Organization name is required"
        })
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def get_organization_suppliers(db: Session, organization_id: uuid.UUID, include_inactive: bool = False):
    """Get all suppliers belonging to a specific organization."""
    query = db.query(models.Organization)\
        .options(
            joinedload(models.Organization.parent_organization),
            joinedload(models.Organization.child_organizations)
        )\
        .filter(
            and_(
                models.Organization.organization_type == OrganizationType.supplier,
                models.Organization.parent_organization_id == organization_id
            )
        )
    
    if not include_inactive:
        query = query.filter(models.Organization.is_active == True)
    
    return query.all()

def get_active_suppliers_for_organization(db: Session, organization_id: uuid.UUID):
    """Get only active suppliers for a specific organization (for dropdowns)."""
    return db.query(models.Organization)\
        .filter(
            and_(
                models.Organization.organization_type == OrganizationType.supplier,
                models.Organization.parent_organization_id == organization_id,
                models.Organization.is_active == True
            )
        )\
        .order_by(models.Organization.name)\
        .all()

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

def get_organization_hierarchy_tree(
    db: Session, 
    include_inactive: bool = False,
    accessible_org_ids: Optional[Set[uuid.UUID]] = None
) -> List[OrganizationHierarchyNode]:
    """
    Build complete organization hierarchy tree with nested children.
    
    Args:
        db: Database session
        include_inactive: Include inactive organizations
        accessible_org_ids: Set of organization IDs user can access (for scoping)
    
    Returns:
        List of root organization nodes with nested children
    """
    # Build base query for all organizations
    query = db.query(models.Organization)
    
    # Apply active status filter
    if not include_inactive:
        query = query.filter(models.Organization.is_active == True)
    
    # Apply organization scoping if provided
    if accessible_org_ids is not None:
        query = query.filter(models.Organization.id.in_(accessible_org_ids))
    
    # Fetch all organizations in a single query
    all_orgs = query.order_by(models.Organization.name).all()
    
    # Build parent-child mapping
    org_dict = {org.id: org for org in all_orgs}
    children_map = {}
    
    # Initialize children map
    for org in all_orgs:
        children_map[org.id] = []
    
    # Populate children map and identify roots
    root_orgs = []
    for org in all_orgs:
        if org.parent_organization_id is None:
            # This is a root organization
            root_orgs.append(org)
        elif org.parent_organization_id in org_dict:
            # Add to parent's children list
            children_map[org.parent_organization_id].append(org)
    
    def build_hierarchy_node(org: models.Organization) -> OrganizationHierarchyNode:
        """Recursively build hierarchy node with children."""
        # Get children for this organization
        children = []
        for child_org in children_map.get(org.id, []):
            child_node = build_hierarchy_node(child_org)
            children.append(child_node)
        
        # Sort children by name for consistent ordering
        children.sort(key=lambda x: x.name)
        
        # Create hierarchy node
        return OrganizationHierarchyNode(
            id=org.id,
            name=org.name,
            organization_type=org.organization_type,
            is_active=org.is_active,
            parent_organization_id=org.parent_organization_id,
            created_at=org.created_at,
            updated_at=org.updated_at,
            children=children
        )
    
    # Build hierarchy tree starting from root organizations
    hierarchy_tree = []
    for root_org in root_orgs:
        root_node = build_hierarchy_node(root_org)
        hierarchy_tree.append(root_node)
    
    # Sort root organizations by name for consistent ordering
    hierarchy_tree.sort(key=lambda x: x.name)
    
    return hierarchy_tree

def seed_default_organizations(db: Session):
    """
    Create default organizations (Oraseas EE and BossAqua) if they don't exist.
    Returns a dict with the created/existing organizations.
    """
    result = {
        "oraseas_ee": None,
        "bossaqua": None,
        "created": [],
        "existing": []
    }
    
    # Check if Oraseas EE exists
    oraseas_ee = db.query(models.Organization)\
        .filter(models.Organization.organization_type == OrganizationType.oraseas_ee)\
        .first()
    
    if not oraseas_ee:
        # Create Oraseas EE
        oraseas_ee = models.Organization(
            name="Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            country="GR",  # Default to Greece
            address="Greece",
            contact_info="Default Oraseas EE contact",
            is_active=True
        )
        db.add(oraseas_ee)
        db.flush()  # Flush to get the ID
        result["created"].append("Oraseas EE")
    else:
        result["existing"].append("Oraseas EE")
    
    result["oraseas_ee"] = oraseas_ee
    
    # Check if BossAqua exists
    bossaqua = db.query(models.Organization)\
        .filter(models.Organization.organization_type == OrganizationType.bossaqua)\
        .first()
    
    if not bossaqua:
        # Create BossAqua
        bossaqua = models.Organization(
            name="BossAqua",
            organization_type=OrganizationType.bossaqua,
            country="GR",  # Default to Greece
            address="Greece",
            contact_info="Default BossAqua contact",
            is_active=True
        )
        db.add(bossaqua)
        db.flush()  # Flush to get the ID
        result["created"].append("BossAqua")
    else:
        result["existing"].append("BossAqua")
    
    result["bossaqua"] = bossaqua
    
    # Commit all changes
    db.commit()
    
    # Refresh objects to get updated data
    db.refresh(oraseas_ee)
    db.refresh(bossaqua)
    
    return result

def _create_default_warehouse_for_organization(db: Session, organization: models.Organization):
    """
    Create a default warehouse for an organization with the same name.
    This is called automatically when customer organizations are created.
    """
    try:
        # Check if a warehouse with the organization name already exists
        existing_warehouse = db.query(models.Warehouse).filter(
            and_(
                models.Warehouse.organization_id == organization.id,
                models.Warehouse.name == organization.name
            )
        ).first()
        
        if not existing_warehouse:
            # Create default warehouse
            default_warehouse = models.Warehouse(
                organization_id=organization.id,
                name=organization.name,  # Use organization name as warehouse name
                location=organization.address or "Default Location",
                description=f"Default warehouse for {organization.name}",
                is_active=True
            )
            
            db.add(default_warehouse)
            db.commit()
            db.refresh(default_warehouse)
            
            return default_warehouse
        
        return existing_warehouse
        
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to create default warehouse for organization {organization.name}: {str(e)}")

def initialize_default_organizations(db: Session):
    """
    Initialize default organizations and return status.
    This is the main function to be called from API endpoints.
    """
    try:
        result = seed_default_organizations(db)
        
        return {
            "success": True,
            "message": f"Default organizations initialized. Created: {result['created']}, Existing: {result['existing']}",
            "organizations": {
                "oraseas_ee": {
                    "id": str(result["oraseas_ee"].id),
                    "name": result["oraseas_ee"].name,
                    "created": "Oraseas EE" in result["created"]
                },
                "bossaqua": {
                    "id": str(result["bossaqua"].id),
                    "name": result["bossaqua"].name,
                    "created": "BossAqua" in result["created"]
                }
            }
        }
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to initialize default organizations: {str(e)}")