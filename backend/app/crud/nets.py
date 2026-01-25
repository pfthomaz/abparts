# backend/app/crud/nets.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..models import Net, FarmSite, NetCleaningRecord
from ..schemas.net_cleaning import NetCreate, NetUpdate


def get_net(db: Session, net_id: UUID) -> Optional[Net]:
    """Get a single net by ID."""
    return db.query(Net).filter(Net.id == net_id).first()


def get_nets(
    db: Session,
    organization_id: UUID,
    farm_site_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
) -> List[Net]:
    """Get all nets with optional farm site filter."""
    query = db.query(Net).join(FarmSite).filter(
        FarmSite.organization_id == organization_id
    )
    
    if farm_site_id:
        query = query.filter(Net.farm_site_id == farm_site_id)
    
    if active_only:
        query = query.filter(Net.active == True)
    
    return query.order_by(FarmSite.name, Net.name).offset(skip).limit(limit).all()


def get_nets_count(
    db: Session,
    organization_id: UUID,
    farm_site_id: Optional[UUID] = None,
    active_only: bool = True
) -> int:
    """Get count of nets."""
    query = db.query(Net).join(FarmSite).filter(
        FarmSite.organization_id == organization_id
    )
    
    if farm_site_id:
        query = query.filter(Net.farm_site_id == farm_site_id)
    
    if active_only:
        query = query.filter(Net.active == True)
    
    return query.count()


def create_net(db: Session, net: NetCreate) -> Net:
    """Create a new net."""
    db_net = Net(**net.model_dump())
    db.add(db_net)
    db.commit()
    db.refresh(db_net)
    return db_net


def update_net(
    db: Session,
    net_id: UUID,
    net_update: NetUpdate
) -> Optional[Net]:
    """Update an existing net."""
    db_net = get_net(db, net_id)
    if not db_net:
        return None
    
    update_data = net_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_net, field, value)
    
    db.commit()
    db.refresh(db_net)
    return db_net


def delete_net(db: Session, net_id: UUID) -> bool:
    """Soft delete a net by setting active=False."""
    db_net = get_net(db, net_id)
    if not db_net:
        return False
    
    db_net.active = False
    db.commit()
    return True


def get_net_with_cleaning_stats(db: Session, net_id: UUID) -> Optional[dict]:
    """Get net with cleaning statistics."""
    db_net = get_net(db, net_id)
    if not db_net:
        return None
    
    # Get cleaning records count
    cleaning_count = db.query(NetCleaningRecord).filter(
        NetCleaningRecord.net_id == net_id
    ).count()
    
    # Get last cleaning date
    last_cleaning = db.query(NetCleaningRecord).filter(
        NetCleaningRecord.net_id == net_id
    ).order_by(NetCleaningRecord.start_time.desc()).first()
    
    return {
        "net": db_net,
        "cleaning_records_count": cleaning_count,
        "last_cleaning_date": last_cleaning.start_time if last_cleaning else None
    }


def search_nets(
    db: Session,
    organization_id: UUID,
    search_term: str,
    skip: int = 0,
    limit: int = 100
) -> List[Net]:
    """Search nets by name."""
    query = db.query(Net).join(FarmSite).filter(
        and_(
            FarmSite.organization_id == organization_id,
            Net.active == True
        )
    )
    
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(Net.name.ilike(search_pattern))
    
    return query.order_by(Net.name).offset(skip).limit(limit).all()


def get_nets_by_farm_site(
    db: Session,
    farm_site_id: UUID,
    active_only: bool = True
) -> List[Net]:
    """Get all nets for a specific farm site."""
    query = db.query(Net).filter(Net.farm_site_id == farm_site_id)
    
    if active_only:
        query = query.filter(Net.active == True)
    
    return query.order_by(Net.name).all()
