# backend/app/crud/net_cleaning_records.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date

from ..models import NetCleaningRecord, Net, FarmSite, Machine, User
from ..schemas.net_cleaning import NetCleaningRecordCreate, NetCleaningRecordUpdate


def get_cleaning_record(db: Session, record_id: UUID) -> Optional[NetCleaningRecord]:
    """Get a single cleaning record by ID."""
    return db.query(NetCleaningRecord).filter(NetCleaningRecord.id == record_id).first()


def get_cleaning_records(
    db: Session,
    organization_id: UUID,
    net_id: Optional[UUID] = None,
    farm_site_id: Optional[UUID] = None,
    machine_id: Optional[UUID] = None,
    operator_name: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100
) -> List[NetCleaningRecord]:
    """Get cleaning records with various filters."""
    query = db.query(NetCleaningRecord).join(Net).join(FarmSite).filter(
        FarmSite.organization_id == organization_id
    )
    
    if net_id:
        query = query.filter(NetCleaningRecord.net_id == net_id)
    
    if farm_site_id:
        query = query.filter(Net.farm_site_id == farm_site_id)
    
    if machine_id:
        query = query.filter(NetCleaningRecord.machine_id == machine_id)
    
    if operator_name:
        query = query.filter(NetCleaningRecord.operator_name.ilike(f"%{operator_name}%"))
    
    if start_date:
        query = query.filter(NetCleaningRecord.start_time >= start_date)
    
    if end_date:
        # Add one day to include the entire end_date
        query = query.filter(NetCleaningRecord.start_time < end_date)
    
    return query.order_by(desc(NetCleaningRecord.start_time)).offset(skip).limit(limit).all()


def get_cleaning_records_count(
    db: Session,
    organization_id: UUID,
    net_id: Optional[UUID] = None,
    farm_site_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> int:
    """Get count of cleaning records."""
    query = db.query(NetCleaningRecord).join(Net).join(FarmSite).filter(
        FarmSite.organization_id == organization_id
    )
    
    if net_id:
        query = query.filter(NetCleaningRecord.net_id == net_id)
    
    if farm_site_id:
        query = query.filter(Net.farm_site_id == farm_site_id)
    
    if start_date:
        query = query.filter(NetCleaningRecord.start_time >= start_date)
    
    if end_date:
        query = query.filter(NetCleaningRecord.start_time < end_date)
    
    return query.count()


def create_cleaning_record(
    db: Session,
    record: NetCleaningRecordCreate,
    created_by_user_id: UUID
) -> NetCleaningRecord:
    """Create a new cleaning record."""
    db_record = NetCleaningRecord(
        **record.model_dump(),
        created_by=created_by_user_id
    )
    
    # Calculate duration
    db_record.calculate_duration()
    
    # Validate
    db_record.validate_cleaning_mode()
    db_record.validate_times()
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def update_cleaning_record(
    db: Session,
    record_id: UUID,
    record_update: NetCleaningRecordUpdate
) -> Optional[NetCleaningRecord]:
    """Update an existing cleaning record."""
    db_record = get_cleaning_record(db, record_id)
    if not db_record:
        return None
    
    update_data = record_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)
    
    # Auto-update status based on end_time
    if 'end_time' in update_data:
        if update_data['end_time'] is not None:
            # If end_time is provided, mark as completed
            db_record.status = 'completed'
        else:
            # If end_time is explicitly set to None, mark as in_progress
            db_record.status = 'in_progress'
    
    # Recalculate duration if times changed
    if 'start_time' in update_data or 'end_time' in update_data:
        db_record.calculate_duration()
        db_record.validate_times()
    
    # Validate mode if changed
    if 'cleaning_mode' in update_data:
        db_record.validate_cleaning_mode()
    
    db.commit()
    db.refresh(db_record)
    return db_record


def delete_cleaning_record(db: Session, record_id: UUID) -> bool:
    """Delete a cleaning record."""
    db_record = get_cleaning_record(db, record_id)
    if not db_record:
        return False
    
    db.delete(db_record)
    db.commit()
    return True


def get_cleaning_record_with_details(db: Session, record_id: UUID) -> Optional[dict]:
    """Get cleaning record with related entity details."""
    db_record = db.query(NetCleaningRecord).filter(
        NetCleaningRecord.id == record_id
    ).first()
    
    if not db_record:
        return None
    
    # Get related entities
    net = db.query(Net).filter(Net.id == db_record.net_id).first()
    farm_site = db.query(FarmSite).filter(FarmSite.id == net.farm_site_id).first() if net else None
    machine = db.query(Machine).filter(Machine.id == db_record.machine_id).first() if db_record.machine_id else None
    user = db.query(User).filter(User.id == db_record.created_by).first()
    
    return {
        "record": db_record,
        "net_name": net.name if net else None,
        "farm_site_name": farm_site.name if farm_site else None,
        "machine_name": machine.name if machine else None,
        "created_by_username": user.username if user else None
    }


def get_cleaning_statistics(
    db: Session,
    organization_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> dict:
    """Get cleaning statistics for an organization."""
    query = db.query(NetCleaningRecord).join(Net).join(FarmSite).filter(
        FarmSite.organization_id == organization_id
    )
    
    if start_date:
        query = query.filter(NetCleaningRecord.start_time >= start_date)
    
    if end_date:
        query = query.filter(NetCleaningRecord.start_time < end_date)
    
    records = query.all()
    
    if not records:
        return {
            "total_cleanings": 0,
            "total_duration_minutes": 0,
            "average_duration_minutes": 0,
            "cleanings_by_mode": {},
            "cleanings_by_operator": {},
            "most_cleaned_nets": []
        }
    
    # Calculate statistics
    total_cleanings = len(records)
    total_duration = sum(r.duration_minutes or 0 for r in records)
    average_duration = total_duration / total_cleanings if total_cleanings > 0 else 0
    
    # Group by mode
    cleanings_by_mode = {}
    for record in records:
        mode = f"Mode {record.cleaning_mode}"
        cleanings_by_mode[mode] = cleanings_by_mode.get(mode, 0) + 1
    
    # Group by operator
    cleanings_by_operator = {}
    for record in records:
        operator = record.operator_name
        cleanings_by_operator[operator] = cleanings_by_operator.get(operator, 0) + 1
    
    # Most cleaned nets
    net_counts = db.query(
        Net.id,
        Net.name,
        FarmSite.name.label('farm_site_name'),
        func.count(NetCleaningRecord.id).label('cleaning_count')
    ).join(NetCleaningRecord).join(FarmSite).filter(
        FarmSite.organization_id == organization_id
    )
    
    if start_date:
        net_counts = net_counts.filter(NetCleaningRecord.start_time >= start_date)
    if end_date:
        net_counts = net_counts.filter(NetCleaningRecord.start_time < end_date)
    
    net_counts = net_counts.group_by(Net.id, Net.name, FarmSite.name).order_by(
        desc('cleaning_count')
    ).limit(10).all()
    
    most_cleaned_nets = [
        {
            "net_id": str(net.id),
            "net_name": net.name,
            "farm_site_name": net.farm_site_name,
            "cleaning_count": net.cleaning_count
        }
        for net in net_counts
    ]
    
    return {
        "total_cleanings": total_cleanings,
        "total_duration_minutes": total_duration,
        "average_duration_minutes": round(average_duration, 2),
        "cleanings_by_mode": cleanings_by_mode,
        "cleanings_by_operator": cleanings_by_operator,
        "most_cleaned_nets": most_cleaned_nets
    }


def get_recent_cleaning_records(
    db: Session,
    organization_id: UUID,
    limit: int = 10
) -> List[NetCleaningRecord]:
    """Get most recent cleaning records for an organization."""
    return db.query(NetCleaningRecord).join(Net).join(FarmSite).filter(
        FarmSite.organization_id == organization_id
    ).order_by(desc(NetCleaningRecord.start_time)).limit(limit).all()
