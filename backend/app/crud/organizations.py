# c:/abparts/backend/app/crud/organizations.py
import uuid
from sqlalchemy.orm import Session
from .. import models

def get_organization(db: Session, organization_id: uuid.UUID):
    """Retrieves a single organization by its ID."""
    return db.query(models.Organization).filter(models.Organization.id == organization_id).first()

def get_organizations(db: Session):
    """Retrieves all organizations."""
    return db.query(models.Organization).all()

def create_organization(db: Session, org_data):
    """Creates a new organization."""
    org = models.Organization(**org_data.dict())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

def update_organization(db: Session, organization_id: uuid.UUID, org_data):
    """Updates an existing organization."""
    org = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not org:
        return None
    for key, value in org_data.dict(exclude_unset=True).items():
        setattr(org, key, value)
    db.commit()
    db.refresh(org)
    return org

def delete_organization(db: Session, organization_id: uuid.UUID):
    """Deletes an organization by its ID."""
    org = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not org:
        return None
    db.delete(org)
    db.commit()
    return org