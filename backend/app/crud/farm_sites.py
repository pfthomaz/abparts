# backend/app/crud/farm_sites.py

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID

from ..models import FarmSite, Net
from ..schemas.net_cleaning import FarmSiteCreate, FarmSiteUpdate


def get_farm_site(db: Session, farm_site_id: UUID) -> Optional[FarmSite]:
    """Get a single farm site by ID."""
    return db.query(FarmSite).filter(FarmSite.id == farm_site_id).first()


def get_farm_sites(
    db: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
) -> List[FarmSite]:
    """Get all farm sites for an organization with pagination."""
    query = db.query(FarmSite).filter(FarmSite.organization_id == organization_id)
    
    if active_only:
        query = query.filter(FarmSite.active == True)
    
    return query.order_by(FarmSite.name).offset(skip).limit(limit).all()


def get_farm_sites_count(
    db: Session,
    organization_id: UUID,
    active_only: bool = True
) -> int:
    """Get count of farm sites for an organization."""
    query = db.query(FarmSite).filter(FarmSite.organization_id == organization_id)
    
    if active_only:
        query = query.filter(FarmSite.active == True)
    
    return query.count()


def create_farm_site(
    db: Session,
    farm_site: FarmSiteCreate,
    organization_id: UUID
) -> FarmSite:
    """Create a new farm site."""
    db_farm_site = FarmSite(
        organization_id=organization_id,
        **farm_site.model_dump()
    )
    db.add(db_farm_site)
    db.commit()
    db.refresh(db_farm_site)
    return db_farm_site


def update_farm_site(
    db: Session,
    farm_site_id: UUID,
    farm_site_update: FarmSiteUpdate
) -> Optional[FarmSite]:
    """Update an existing farm site."""
    db_farm_site = get_farm_site(db, farm_site_id)
    if not db_farm_site:
        return None
    
    update_data = farm_site_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_farm_site, field, value)
    
    db.commit()
    db.refresh(db_farm_site)
    return db_farm_site


def delete_farm_site(db: Session, farm_site_id: UUID) -> bool:
    """Soft delete a farm site by setting active=False."""
    db_farm_site = get_farm_site(db, farm_site_id)
    if not db_farm_site:
        return False
    
    db_farm_site.active = False
    db.commit()
    return True


def get_farm_site_with_nets_count(db: Session, farm_site_id: UUID) -> Optional[dict]:
    """Get farm site with count of nets."""
    db_farm_site = get_farm_site(db, farm_site_id)
    if not db_farm_site:
        return None
    
    nets_count = db.query(Net).filter(
        and_(
            Net.farm_site_id == farm_site_id,
            Net.active == True
        )
    ).count()
    
    return {
        "farm_site": db_farm_site,
        "nets_count": nets_count
    }


def search_farm_sites(
    db: Session,
    organization_id: UUID,
    search_term: str,
    skip: int = 0,
    limit: int = 100
) -> List[FarmSite]:
    """Search farm sites by name or location."""
    query = db.query(FarmSite).filter(
        and_(
            FarmSite.organization_id == organization_id,
            FarmSite.active == True
        )
    )
    
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            (FarmSite.name.ilike(search_pattern)) |
            (FarmSite.location.ilike(search_pattern))
        )
    
    return query.order_by(FarmSite.name).offset(skip).limit(limit).all()
