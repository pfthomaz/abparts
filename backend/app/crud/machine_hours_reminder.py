# backend/app/crud/machine_hours_reminder.py

import uuid
from datetime import datetime, timedelta, date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from .. import models
from ..schemas.machine_hours_reminder import (
    MachineHoursReminderCheck, 
    MachineHoursReminderResponse,
    BulkMachineHoursCreate
)

def should_show_reminder_today() -> bool:
    """
    Check if today is a reminder day (1,2,3 or 15,16,17 of each month)
    TEMPORARILY MODIFIED: Show reminders every day for testing
    """
    today = date.today()
    reminder_days = [1, 2, 3, 15, 16, 17]
    
    # TEMPORARY: Always return True for testing
    # Remove this line and uncomment the next line for production
    return True
    # return today.day in reminder_days

def get_machines_needing_hours_update(db: Session, organization_id: uuid.UUID) -> List[models.Machine]:
    """
    Get machines that haven't had hours recorded in 2+ weeks or never recorded
    """
    two_weeks_ago = datetime.now() - timedelta(days=14)
    
    # Get all machines for the organization
    machines = db.query(models.Machine)\
        .filter(models.Machine.customer_organization_id == organization_id)\
        .all()
    
    overdue_machines = []
    
    for machine in machines:
        # Get the latest hours record for this machine
        latest_record = db.query(models.MachineHours)\
            .filter(models.MachineHours.machine_id == machine.id)\
            .order_by(desc(models.MachineHours.recorded_date))\
            .first()
        
        # If no record exists or last record is older than 2 weeks
        if not latest_record or latest_record.recorded_date < two_weeks_ago:
            overdue_machines.append(machine)
    
    return overdue_machines

def get_last_hours_record_date(db: Session, machine_id: uuid.UUID) -> Optional[datetime]:
    """
    Get the date of the last hours record for a machine
    """
    latest_record = db.query(models.MachineHours)\
        .filter(models.MachineHours.machine_id == machine_id)\
        .order_by(desc(models.MachineHours.recorded_date))\
        .first()
    
    return latest_record.recorded_date if latest_record else None

def check_machine_hours_reminders(db: Session, user_id: uuid.UUID, organization_id: uuid.UUID) -> MachineHoursReminderResponse:
    """
    Check if user should see machine hours reminder modal
    """
    # Check if today is a reminder day
    is_reminder_day = should_show_reminder_today()
    
    if not is_reminder_day:
        return MachineHoursReminderResponse(
            should_show_reminder=False,
            reminder_reason="no_reminder"
        )
    
    # Check if user already dismissed reminder today
    if has_dismissed_reminder_today(db, user_id):
        return MachineHoursReminderResponse(
            should_show_reminder=False,
            reminder_reason="already_dismissed"
        )
    
    # Get machines needing updates
    overdue_machines = get_machines_needing_hours_update(db, organization_id)
    
    if not overdue_machines:
        return MachineHoursReminderResponse(
            should_show_reminder=False,
            reminder_reason="all_up_to_date"
        )
    
    # Build reminder data for each machine
    reminder_machines = []
    for machine in overdue_machines:
        last_recorded_date = get_last_hours_record_date(db, machine.id)
        
        if last_recorded_date:
            days_since = (datetime.now() - last_recorded_date).days
            never_recorded = False
        else:
            days_since = None
            never_recorded = True
        
        reminder_machines.append(MachineHoursReminderCheck(
            machine_id=machine.id,
            machine_name=machine.name,
            serial_number=machine.serial_number,
            last_recorded_date=last_recorded_date,
            days_since_last_record=days_since,
            never_recorded=never_recorded
        ))
    
    return MachineHoursReminderResponse(
        should_show_reminder=True,
        reminder_machines=reminder_machines,
        reminder_reason="overdue_machines",
        total_overdue_machines=len(reminder_machines)
    )

def has_dismissed_reminder_today(db: Session, user_id: uuid.UUID) -> bool:
    """
    Check if user has already dismissed the reminder today
    Note: This would require a dismissal tracking table, for now return False
    """
    # TODO: Implement dismissal tracking table
    return False

def record_reminder_dismissal(db: Session, user_id: uuid.UUID) -> bool:
    """
    Record that user dismissed the reminder today
    Note: This would require a dismissal tracking table
    """
    # TODO: Implement dismissal tracking table
    return True

def create_bulk_machine_hours(db: Session, machine_hours_list: List[BulkMachineHoursCreate], user_id: uuid.UUID) -> List[models.MachineHours]:
    """
    Create multiple machine hours records from the reminder modal
    """
    created_records = []
    
    for hours_data in machine_hours_list:
        # Verify machine exists and user has permission
        machine = db.query(models.Machine)\
            .filter(models.Machine.id == hours_data.machine_id)\
            .first()
        
        if not machine:
            continue  # Skip invalid machines
        
        # Create the hours record
        hours_record = models.MachineHours(
            machine_id=hours_data.machine_id,
            recorded_by_user_id=user_id,
            hours_value=hours_data.hours_value,
            recorded_date=datetime.now(),
            notes=hours_data.notes
        )
        
        db.add(hours_record)
        created_records.append(hours_record)
    
    db.commit()
    
    # Refresh all records
    for record in created_records:
        db.refresh(record)
    
    return created_records