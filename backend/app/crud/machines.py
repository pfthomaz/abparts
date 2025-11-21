# backend/app/crud/machines.py

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError, InvalidRequestError, OperationalError, TimeoutError
from fastapi import HTTPException, status
from psycopg2.errors import UniqueViolation, ForeignKeyViolation, CheckViolation, OperationalError as PsycopgOperationalError

from .. import models, schemas

logger = logging.getLogger(__name__)

def safe_database_query(query_func, error_message="Database query failed", log_context=""):
    """
    Safely execute a database query with comprehensive error handling.
    
    Args:
        query_func: Function that executes the database query
        error_message: Custom error message for HTTP exceptions
        log_context: Additional context for logging
    
    Returns:
        Query result
        
    Raises:
        HTTPException: If the query fails
    """
    try:
        return query_func()
    except (OperationalError, TimeoutError) as e:
        logger.error(f"Database connection/timeout error {log_context}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable. Please try again later."
        )
    except IntegrityError as e:
        logger.error(f"Database integrity error {log_context}: {str(e)}")
        # Let the calling function handle specific integrity errors
        raise
    except DataError as e:
        logger.error(f"Database data error {log_context}: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data format provided")
    except SQLAlchemyError as e:
        logger.error(f"Database error {log_context}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )

def safe_enum_conversion(enum_class, value, field_name="field"):
    """
    Safely convert a value to an enum, handling various input types and providing detailed error messages.
    
    Args:
        enum_class: The enum class to convert to
        value: The value to convert
        field_name: Name of the field for error messages
    
    Returns:
        The enum value
        
    Raises:
        HTTPException: If the value cannot be converted to the enum
    """
    if value is None:
        return None
        
    try:
        # If it's already the correct enum type, return it
        if isinstance(value, enum_class):
            return value
            
        # If it's a string, normalize and find matching enum
        if isinstance(value, str):
            normalized_value = value.strip().lower()
            if not normalized_value:
                raise HTTPException(
                    status_code=400, 
                    detail=f"{field_name} cannot be empty"
                )
                
            # Find matching enum value (case-insensitive)
            for enum_item in enum_class:
                if enum_item.value.lower() == normalized_value:
                    return enum_item
                    
            # If no match found, provide helpful error
            valid_values = [item.value for item in enum_class]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {field_name} '{value}'. Valid values are: {valid_values}"
            )
        else:
            # For other types, try direct conversion
            return enum_class(value)
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error converting {field_name} value '{value}': {str(e)}")
        valid_values = [item.value for item in enum_class]
        raise HTTPException(
            status_code=400,
            detail=f"Error processing {field_name}. Valid values are: {valid_values}"
        )

def get_machine(db: Session, machine_id: uuid.UUID):
    """Retrieve a single machine by ID."""
    try:
        if not machine_id:
            logger.warning("get_machine called with None or empty machine_id")
            return None
            
        machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        
        if machine:
            logger.debug(f"Successfully retrieved machine {machine_id}")
        else:
            logger.info(f"Machine not found with ID: {machine_id}")
            
        return machine
        
    except (OperationalError, TimeoutError) as e:
        logger.error(f"Database connection/timeout error retrieving machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable. Please try again later."
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving machine"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the machine"
        )

def get_machines(db: Session, skip: int = 0, limit: int = 100, organization_id: Optional[uuid.UUID] = None):
    """
    Retrieve a list of machines, optionally filtered by organization ID.
    This function handles the database query and filtering.
    Authentication/Authorization is handled in the router.
    """
    try:
        # Validate input parameters
        if skip < 0:
            logger.warning(f"Invalid skip parameter: {skip}, setting to 0")
            skip = 0
        if limit <= 0 or limit > 1000:
            logger.warning(f"Invalid limit parameter: {limit}, setting to 100")
            limit = 100
            
        query = db.query(models.Machine)
        
        if organization_id:
            logger.debug(f"Filtering machines by organization_id: {organization_id}")
            query = query.filter(models.Machine.customer_organization_id == organization_id)
        
        machines = query.order_by(models.Machine.created_at.desc()).offset(skip).limit(limit).all()
        
        # Handle case where machines might be None or not a list
        if machines is None:
            machines = []
        
        # Safe logging that handles different types
        try:
            machine_count = len(machines) if hasattr(machines, '__len__') else 0
            logger.debug(f"Successfully retrieved {machine_count} machines (skip={skip}, limit={limit})")
        except Exception:
            logger.debug(f"Successfully retrieved machines (skip={skip}, limit={limit})")
            
        return machines
        
    except (OperationalError, TimeoutError) as e:
        logger.error(f"Database connection/timeout error retrieving machines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable. Please try again later."
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving machines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving machines"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving machines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving machines"
        )

def create_machine(db: Session, machine: schemas.MachineCreate):
    """Create a new machine."""
    try:
        # Validate input data
        if not machine.customer_organization_id:
            logger.error("create_machine called with missing customer_organization_id")
            raise HTTPException(status_code=400, detail="Customer organization ID is required")
            
        if not machine.serial_number or not machine.serial_number.strip():
            logger.error("create_machine called with missing or empty serial_number")
            raise HTTPException(status_code=400, detail="Serial number is required")
            
        # Check if organization_id exists BEFORE creating the machine
        organization = db.query(models.Organization).filter(
            models.Organization.id == machine.customer_organization_id
        ).first()
        
        if not organization:
            logger.warning(f"Organization not found: {machine.customer_organization_id}")
            raise HTTPException(status_code=400, detail="Organization ID not found")
        
        # Ensure the organization is a customer organization
        if organization.organization_type != models.OrganizationType.customer:
            logger.warning(f"Attempted to assign machine to non-customer organization: {organization.organization_type}")
            raise HTTPException(status_code=400, detail="Machines can only be assigned to customer organizations")

        # Handle enum conversion for status if provided
        machine_data = machine.dict()
        
        # Temporarily filter out commented fields until DB migration is complete
        commented_fields = [
            'purchase_date', 'warranty_expiry_date', 'status', 
            'last_maintenance_date', 'next_maintenance_date', 
            'location', 'notes'
        ]
        machine_data_filtered = {k: v for k, v in machine_data.items() if k not in commented_fields}

        db_machine = models.Machine(**machine_data_filtered)
        db.add(db_machine)
        db.commit()
        db.refresh(db_machine)
        
        logger.info(f"Successfully created machine: {db_machine.id} with serial number: {db_machine.serial_number}")
        return db_machine
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating machine: {str(e)}")
        
        # Handle specific constraint violations
        if isinstance(e.orig, UniqueViolation):
            if "serial_number" in str(e.orig):
                raise HTTPException(status_code=409, detail="Machine with this serial number already exists")
            else:
                raise HTTPException(status_code=409, detail="Machine data violates uniqueness constraint")
        elif isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=400, detail="Referenced organization does not exist")
        else:
            raise HTTPException(status_code=400, detail="Data integrity constraint violation")
            
    except DataError as e:
        db.rollback()
        logger.error(f"Data error creating machine: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data format provided")
        
    except (OperationalError, TimeoutError) as e:
        db.rollback()
        logger.error(f"Database connection/timeout error creating machine: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable. Please try again later."
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating machine: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating the machine"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating machine: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the machine"
        )

def update_machine(db: Session, machine_id: uuid.UUID, machine_update: schemas.MachineUpdate):
    """Update an existing machine."""
    try:
        # Validate input parameters
        if not machine_id:
            logger.error("update_machine called with missing machine_id")
            raise HTTPException(status_code=400, detail="Machine ID is required")
            
        db_machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not db_machine:
            logger.info(f"Machine not found for update: {machine_id}")
            return None

        update_data = machine_update.dict(exclude_unset=True)
        
        # Handle null/empty update data
        if not update_data:
            logger.info(f"No update data provided for machine: {machine_id}")
            return db_machine

        # If customer_organization_id is being updated, check if the new ID exists and is a customer
        if "customer_organization_id" in update_data and update_data["customer_organization_id"] != db_machine.customer_organization_id:
            if not update_data["customer_organization_id"]:
                raise HTTPException(status_code=400, detail="Customer organization ID cannot be null")
                
            organization = db.query(models.Organization).filter(
                models.Organization.id == update_data["customer_organization_id"]
            ).first()
            
            if not organization:
                logger.warning(f"Organization not found for machine update: {update_data['customer_organization_id']}")
                raise HTTPException(status_code=400, detail="New Organization ID not found for machine update")
                
            if organization.organization_type != models.OrganizationType.customer:
                logger.warning(f"Attempted to assign machine to non-customer organization: {organization.organization_type}")
                raise HTTPException(status_code=400, detail="Machines can only be assigned to customer organizations")

        # Temporarily filter out commented fields until DB migration is complete
        commented_fields = [
            'purchase_date', 'warranty_expiry_date', 'status', 
            'last_maintenance_date', 'next_maintenance_date', 
            'location', 'notes'
        ]
        update_data_filtered = {k: v for k, v in update_data.items() if k not in commented_fields}

        # Apply updates, handling null values gracefully
        for key, value in update_data_filtered.items():
            if hasattr(db_machine, key):
                # Handle special cases for certain fields
                if key == 'serial_number' and (not value or not str(value).strip()):
                    logger.error(f"Attempted to set empty serial_number for machine {machine_id}")
                    raise HTTPException(status_code=400, detail="Serial number cannot be empty")
                
                # Set the value, allowing None for nullable fields
                try:
                    setattr(db_machine, key, value)
                except Exception as e:
                    logger.error(f"Error setting field {key} to value {value}: {str(e)}")
                    raise HTTPException(status_code=400, detail=f"Invalid value for field {key}")
            else:
                logger.warning(f"Attempted to update non-existent field: {key}")
                # Don't raise an error for unknown fields, just log and continue
        
        db.add(db_machine) # Re-add to session to mark as dirty for update
        db.commit()
        db.refresh(db_machine)
        
        logger.info(f"Successfully updated machine: {machine_id}")
        return db_machine
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating machine {machine_id}: {str(e)}")
        
        # Handle specific constraint violations
        if isinstance(e.orig, UniqueViolation):
            if "serial_number" in str(e.orig):
                raise HTTPException(status_code=409, detail="Machine with this serial number already exists")
            else:
                raise HTTPException(status_code=409, detail="Machine data violates uniqueness constraint")
        elif isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=400, detail="Referenced organization does not exist")
        else:
            raise HTTPException(status_code=400, detail="Data integrity constraint violation")
            
    except DataError as e:
        db.rollback()
        logger.error(f"Data error updating machine {machine_id}: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data format provided")
        
    except (OperationalError, TimeoutError) as e:
        db.rollback()
        logger.error(f"Database connection/timeout error updating machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable. Please try again later."
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating the machine"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the machine"
        )

def delete_machine(db: Session, machine_id: uuid.UUID):
    """Delete a machine by ID."""
    try:
        # Validate input parameters
        if not machine_id:
            logger.error("delete_machine called with missing machine_id")
            raise HTTPException(status_code=400, detail="Machine ID is required")
            
        db_machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not db_machine:
            logger.info(f"Machine not found for deletion: {machine_id}")
            return None
            
        db.delete(db_machine)
        db.commit()
        
        logger.info(f"Successfully deleted machine: {machine_id}")
        return {"message": "Machine deleted successfully"}
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error deleting machine {machine_id}: {str(e)}")
        
        # Handle specific constraint violations
        if isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete machine due to existing dependent records (e.g., part usage, maintenance records). Please delete associated records first."
            )
        else:
            raise HTTPException(status_code=400, detail="Data integrity constraint violation")
            
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while deleting the machine"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the machine"
        )

def transfer_machine(db: Session, transfer: schemas.MachineTransferRequest):
    """Transfer a machine to a new customer organization."""
    try:
        # Validate input parameters
        if not transfer.machine_id:
            logger.error("transfer_machine called with missing machine_id")
            raise HTTPException(status_code=400, detail="Machine ID is required")
            
        if not transfer.new_customer_organization_id:
            logger.error("transfer_machine called with missing new_customer_organization_id")
            raise HTTPException(status_code=400, detail="New customer organization ID is required")
        
        # Get the machine
        db_machine = db.query(models.Machine).filter(models.Machine.id == transfer.machine_id).first()
        if not db_machine:
            logger.warning(f"Machine not found for transfer: {transfer.machine_id}")
            raise HTTPException(status_code=404, detail="Machine not found")
        
        # Get the new organization
        new_organization = db.query(models.Organization).filter(
            models.Organization.id == transfer.new_customer_organization_id
        ).first()
        if not new_organization:
            logger.warning(f"New organization not found for transfer: {transfer.new_customer_organization_id}")
            raise HTTPException(status_code=400, detail="New organization not found")
        
        # Ensure the new organization is a customer organization
        if new_organization.organization_type != models.OrganizationType.customer:
            logger.warning(f"Attempted to transfer machine to non-customer organization: {new_organization.organization_type}")
            raise HTTPException(status_code=400, detail="Machines can only be transferred to customer organizations")
        
        # Get the old organization for the transaction notes
        old_organization = db.query(models.Organization).filter(
            models.Organization.id == db_machine.customer_organization_id
        ).first()
        
        # Handle case where old organization might not exist (data integrity issue)
        old_org_name = old_organization.name if old_organization else "Unknown Organization"
        
        # Update the machine's customer_organization_id
        db_machine.customer_organization_id = transfer.new_customer_organization_id
        
        # Add a note about the transfer, handling null notes gracefully
        transfer_date = datetime.now()
        transfer_note = f"Transferred from {old_org_name} to {new_organization.name} on {transfer_date.strftime('%Y-%m-%d')}"
        
        # Safely access notes field
        transfer_notes = getattr(transfer, 'notes', None)
        if transfer_notes and transfer_notes.strip():
            transfer_note += f": {transfer_notes.strip()}"
        
        if db_machine.notes and db_machine.notes.strip():
            db_machine.notes += f"\n\n{transfer_note}"
        else:
            db_machine.notes = transfer_note
        
        # Note: Transaction creation removed due to schema constraints
        # Machine transfer transactions would need a valid part_id
        
        db.add(db_machine)
        db.commit()
        db.refresh(db_machine)
        
        logger.info(f"Successfully transferred machine {transfer.machine_id} from {old_org_name} to {new_organization.name}")
        return db_machine
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error transferring machine {transfer.machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while transferring the machine"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error transferring machine {transfer.machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while transferring the machine"
        )

def get_machine_maintenance_history(db: Session, machine_id: uuid.UUID, skip: int = 0, limit: int = 100):
    """Get maintenance history for a specific machine."""
    try:
        # Validate input parameters
        if not machine_id:
            logger.error("get_machine_maintenance_history called with missing machine_id")
            raise HTTPException(status_code=400, detail="Machine ID is required")
            
        if skip < 0:
            logger.warning(f"Invalid skip parameter: {skip}, setting to 0")
            skip = 0
        if limit <= 0 or limit > 1000:
            logger.warning(f"Invalid limit parameter: {limit}, setting to 100")
            limit = 100
        
        # Check if machine exists
        machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not machine:
            logger.warning(f"Machine not found for maintenance history: {machine_id}")
            raise HTTPException(status_code=404, detail="Machine not found")
        
        # Temporarily return empty list due to missing machine_maintenance table
        # TODO: Implement proper maintenance history when table is created
        logger.info(f"Returning empty maintenance history for machine {machine_id} - table not implemented")
        return []
        
        # Get maintenance records with left join to handle missing users gracefully
        # maintenance_records = db.query(
        #     models.MachineMaintenance
        # ).filter(
        #     models.MachineMaintenance.machine_id == machine_id
        # ).order_by(
        #     desc(models.MachineMaintenance.maintenance_date)
        # ).offset(skip).limit(limit).all()
        
        results = maintenance_records
        
        logger.debug(f"Successfully retrieved {len(results)} maintenance records for machine {machine_id}")
        return results
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving maintenance history for machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving maintenance history"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving maintenance history for machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving maintenance history"
        )

def create_machine_maintenance(db: Session, maintenance: schemas.MaintenanceCreate):
    """Create a new maintenance record for a machine."""
    try:
        # Validate input parameters
        if not maintenance.machine_id:
            logger.error("create_machine_maintenance called with missing machine_id")
            raise HTTPException(status_code=400, detail="Machine ID is required")
            
        if not maintenance.performed_by_user_id:
            logger.error("create_machine_maintenance called with missing performed_by_user_id")
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # Check if machine exists
        machine = db.query(models.Machine).filter(models.Machine.id == maintenance.machine_id).first()
        if not machine:
            logger.warning(f"Machine not found for maintenance creation: {maintenance.machine_id}")
            raise HTTPException(status_code=404, detail="Machine not found")
        
        # Check if user exists
        user = db.query(models.User).filter(models.User.id == maintenance.performed_by_user_id).first()
        if not user:
            logger.warning(f"User not found for maintenance creation: {maintenance.performed_by_user_id}")
            raise HTTPException(status_code=400, detail="User not found")
        
        # Handle enum conversion for maintenance_type if needed
        maintenance_data = maintenance.dict()
        if 'maintenance_type' in maintenance_data and maintenance_data['maintenance_type'] is not None:
            try:
                # Validate maintenance_type if it's a string
                if isinstance(maintenance_data['maintenance_type'], str):
                    # Normalize the maintenance type value
                    maintenance_type_value = maintenance_data['maintenance_type'].strip()
                    if not maintenance_type_value:
                        logger.error("Empty maintenance type provided")
                        raise HTTPException(status_code=400, detail="Maintenance type cannot be empty")
                    
                    # Let SQLAlchemy handle the conversion, but catch any enum errors
                    maintenance_data['maintenance_type'] = maintenance_type_value
                    
            except ValueError as e:
                logger.error(f"Invalid maintenance type value: {maintenance_data['maintenance_type']} - {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid maintenance type value")
            except Exception as e:
                logger.error(f"Unexpected error processing maintenance type: {str(e)}")
                raise HTTPException(status_code=400, detail="Error processing maintenance type")
        
        db_maintenance = models.MachineMaintenance(**maintenance_data)
        db.add(db_maintenance)
        
        # Update the machine's last_maintenance_date and next_maintenance_date
        machine.last_maintenance_date = maintenance.maintenance_date
        if maintenance.next_maintenance_date:
            machine.next_maintenance_date = maintenance.next_maintenance_date
        
        db.add(machine)
        db.commit()
        db.refresh(db_maintenance)
        
        logger.info(f"Successfully created maintenance record: {db_maintenance.id} for machine {maintenance.machine_id}")
        return db_maintenance
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating maintenance record: {str(e)}")
        
        # Handle specific constraint violations
        if isinstance(e.orig, ForeignKeyViolation):
            if "machine_id" in str(e.orig):
                raise HTTPException(status_code=400, detail="Machine not found")
            elif "performed_by_user_id" in str(e.orig):
                raise HTTPException(status_code=400, detail="User not found")
            else:
                raise HTTPException(status_code=400, detail="Referenced record does not exist")
        else:
            raise HTTPException(status_code=400, detail="Data integrity constraint violation")
            
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating maintenance record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating maintenance record"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating maintenance record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating maintenance record"
        )

# --- Machine Hours CRUD Operations ---

def get_machine_hours(db: Session, machine_id: uuid.UUID, skip: int = 0, limit: int = 100):
    """Get machine hours history for a specific machine."""
    try:
        # Validate input parameters
        if not machine_id:
            logger.error("get_machine_hours called with missing machine_id")
            raise HTTPException(status_code=400, detail="Machine ID is required")
            
        if skip < 0:
            logger.warning(f"Invalid skip parameter: {skip}, setting to 0")
            skip = 0
        if limit <= 0 or limit > 1000:
            logger.warning(f"Invalid limit parameter: {limit}, setting to 100")
            limit = 100
        
        # Check if machine exists
        machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not machine:
            logger.warning(f"Machine not found for hours history: {machine_id}")
            raise HTTPException(status_code=404, detail="Machine not found")
        
        # Get machine hours records with user information
        from sqlalchemy.orm import selectinload
        hours_records = db.query(models.MachineHours).options(
            selectinload(models.MachineHours.recorded_by_user)
        ).filter(
            models.MachineHours.machine_id == machine_id
        ).order_by(
            desc(models.MachineHours.recorded_date)
        ).offset(skip).limit(limit).all()
        
        # Populate username for response
        result = []
        for record in hours_records:
            record_dict = {
                "id": record.id,
                "machine_id": record.machine_id,
                "recorded_by_user_id": record.recorded_by_user_id,
                "hours_value": record.hours_value,
                "recorded_date": record.recorded_date,
                "notes": record.notes,
                "created_at": record.created_at,
                "updated_at": record.updated_at,
                "recorded_by_username": record.recorded_by_user.username if record.recorded_by_user else "Unknown"
            }
            result.append(record_dict)
        
        logger.debug(f"Successfully retrieved {len(result)} hours records for machine {machine_id}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving machine hours for machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving machine hours"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving machine hours for machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving machine hours"
        )

def create_machine_hours(db: Session, machine_id: uuid.UUID, hours: schemas.MachineHoursCreate, user_id: uuid.UUID):
    """Create a new machine hours record."""
    try:
        # Validate input parameters
        if not machine_id:
            logger.error("create_machine_hours called with missing machine_id")
            raise HTTPException(status_code=400, detail="Machine ID is required")
            
        if not user_id:
            logger.error("create_machine_hours called with missing user_id")
            raise HTTPException(status_code=400, detail="User ID is required")
        
        logger.info(f"Creating machine hours record - Machine: {machine_id}, User: {user_id}, Hours: {hours.hours_value}")
        
        # Check if machine exists
        machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not machine:
            logger.warning(f"Machine not found for hours recording: {machine_id}")
            raise HTTPException(status_code=404, detail="Machine not found")
        
        # Check if user exists
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.warning(f"User not found for hours recording: {user_id}")
            raise HTTPException(status_code=400, detail="User not found")
        
        # Validate hours value
        if hours.hours_value <= 0:
            logger.error(f"Invalid hours value: {hours.hours_value}")
            raise HTTPException(status_code=400, detail="Hours value must be positive")
        
        if hours.hours_value > 99999:
            logger.error(f"Hours value too high: {hours.hours_value}")
            raise HTTPException(status_code=400, detail="Hours value seems unreasonably high (max 99,999)")
        
        # Get the recorded date from the schema or use current time
        from datetime import timezone
        if hours.recorded_date:
            # If recorded_date is provided, ensure it's timezone-aware
            if hours.recorded_date.tzinfo is None:
                # Make it timezone-aware (assume UTC)
                recorded_date = hours.recorded_date.replace(tzinfo=timezone.utc)
            else:
                recorded_date = hours.recorded_date
        else:
            # Use current UTC time
            recorded_date = datetime.now(timezone.utc)
        
        # Validate recorded date is not in the future
        current_time = datetime.now(timezone.utc)
        if recorded_date > current_time:
            logger.error(f"Future recorded date: {recorded_date}")
            raise HTTPException(status_code=400, detail="Recorded date cannot be in the future")
        
        # Create the machine hours record directly with explicit values
        db_hours = models.MachineHours(
            machine_id=machine_id,
            recorded_by_user_id=user_id,
            hours_value=hours.hours_value,
            recorded_date=recorded_date,
            notes=hours.notes
        )
        
        logger.info(f"Adding machine hours record to database: {db_hours}")
        db.add(db_hours)
        db.commit()
        db.refresh(db_hours)
        
        logger.info(f"Successfully created machine hours record: {db_hours.id} for machine {machine_id}")
        return db_hours
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating machine hours record: {str(e)}")
        
        # Handle specific constraint violations
        if isinstance(e.orig, ForeignKeyViolation):
            if "machine_id" in str(e.orig):
                raise HTTPException(status_code=400, detail="Machine not found")
            elif "recorded_by_user_id" in str(e.orig):
                raise HTTPException(status_code=400, detail="User not found")
            else:
                raise HTTPException(status_code=400, detail="Referenced record does not exist")
        else:
            raise HTTPException(status_code=400, detail="Data integrity constraint violation")
            
    except DataError as e:
        db.rollback()
        logger.error(f"Data error creating machine hours record: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data format provided")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating machine hours record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating machine hours record"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating machine hours record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating machine hours record"
        )

def update_machine_name(db: Session, machine_id: uuid.UUID, new_name: str, user_id: uuid.UUID):
    """Update machine name with proper authorization checks."""
    try:
        # Validate input parameters
        if not machine_id:
            logger.error("update_machine_name called with missing machine_id")
            raise HTTPException(status_code=400, detail="Machine ID is required")
            
        if not user_id:
            logger.error("update_machine_name called with missing user_id")
            raise HTTPException(status_code=400, detail="User ID is required")
            
        if not new_name or not new_name.strip():
            logger.error("update_machine_name called with empty name")
            raise HTTPException(status_code=400, detail="Machine name cannot be empty")
        
        # Get the machine
        machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not machine:
            logger.warning(f"Machine not found for name update: {machine_id}")
            raise HTTPException(status_code=404, detail="Machine not found")
        
        # Get the user
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.warning(f"User not found for name update: {user_id}")
            raise HTTPException(status_code=400, detail="User not found")
        
        # Get the user's organization
        user_org = db.query(models.Organization).filter(models.Organization.id == user.organization_id).first()
        if not user_org:
            logger.warning(f"User organization not found: {user.organization_id}")
            raise HTTPException(status_code=400, detail="User organization not found")
        
        # Check authorization: superadmins can edit any machine name, admins can only edit machines in their org
        if user.role != models.UserRole.super_admin:
            if user.role != models.UserRole.admin:
                logger.warning(f"User {user_id} with role {user.role} attempted to update machine name")
                raise HTTPException(status_code=403, detail="Only admins and superadmins can update machine names")
            
            if machine.customer_organization_id != user.organization_id:
                logger.warning(f"Admin user {user_id} attempted to update machine {machine_id} outside their organization")
                raise HTTPException(status_code=403, detail="Admins can only update machine names within their own organization")
        
        # Update the machine name
        old_name = machine.name
        machine.name = new_name.strip()
        
        # Add a note about the name change
        name_change_note = f"Name changed from '{old_name}' to '{new_name}' by {user.username} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if machine.notes:
            machine.notes += f"\n{name_change_note}"
        else:
            machine.notes = name_change_note
        
        db.add(machine)
        db.commit()
        db.refresh(machine)
        
        logger.info(f"Successfully updated machine name: {machine_id} from '{old_name}' to '{new_name}' by user {user_id}")
        return machine
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating machine name {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating machine name"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating machine name {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating machine name"
        )

def validate_machine_model_type(model_type: str) -> bool:
    """Validate that the machine model type is supported."""
    try:
        valid_types = [models.MachineModelType.V3_1B.value, models.MachineModelType.V4_0.value]
        return model_type in valid_types
    except Exception as e:
        logger.error(f"Error validating machine model type {model_type}: {str(e)}")
        return False
        
        db.commit()
        db.refresh(db_maintenance)
        
        logger.info(f"Successfully created maintenance record for machine {maintenance.machine_id}")
        return db_maintenance
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating maintenance record: {str(e)}")
        
        if isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=400, detail="Referenced machine or user does not exist")
        else:
            raise HTTPException(status_code=400, detail="Data integrity constraint violation")
            
    except DataError as e:
        db.rollback()
        logger.error(f"Data error creating maintenance record: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data format provided")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating maintenance record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating maintenance record"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating maintenance record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating maintenance record"
        )

def add_part_to_maintenance(db: Session, part_usage: schemas.MaintenancePartUsageCreate):
    """Add a part to a maintenance record."""
    try:
        # Validate input parameters
        if not part_usage.maintenance_id:
            logger.error("add_part_to_maintenance called with missing maintenance_id")
            raise HTTPException(status_code=400, detail="Maintenance ID is required")
            
        if not part_usage.part_id:
            logger.error("add_part_to_maintenance called with missing part_id")
            raise HTTPException(status_code=400, detail="Part ID is required")
            
        if not part_usage.warehouse_id:
            logger.error("add_part_to_maintenance called with missing warehouse_id")
            raise HTTPException(status_code=400, detail="Warehouse ID is required")
            
        if not part_usage.quantity or part_usage.quantity <= 0:
            logger.error(f"add_part_to_maintenance called with invalid quantity: {part_usage.quantity}")
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        
        # Check if maintenance record exists
        maintenance = db.query(models.MachineMaintenance).filter(
            models.MachineMaintenance.id == part_usage.maintenance_id
        ).first()
        if not maintenance:
            logger.warning(f"Maintenance record not found: {part_usage.maintenance_id}")
            raise HTTPException(status_code=404, detail="Maintenance record not found")
        
        # Check if part exists
        part = db.query(models.Part).filter(models.Part.id == part_usage.part_id).first()
        if not part:
            logger.warning(f"Part not found: {part_usage.part_id}")
            raise HTTPException(status_code=400, detail="Part not found")
        
        # Check if warehouse exists
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == part_usage.warehouse_id).first()
        if not warehouse:
            logger.warning(f"Warehouse not found: {part_usage.warehouse_id}")
            raise HTTPException(status_code=400, detail="Warehouse not found")
        
        # Check if there's enough stock in the warehouse
        inventory = db.query(models.Inventory).filter(
            models.Inventory.warehouse_id == part_usage.warehouse_id,
            models.Inventory.part_id == part_usage.part_id
        ).first()
        
        if not inventory:
            logger.warning(f"No inventory record found for part {part_usage.part_id} in warehouse {part_usage.warehouse_id}")
            raise HTTPException(status_code=400, detail="Part not available in specified warehouse")
            
        if inventory.current_stock < part_usage.quantity:
            logger.warning(f"Insufficient stock: requested {part_usage.quantity}, available {inventory.current_stock}")
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock in warehouse. Available: {inventory.current_stock}, Requested: {part_usage.quantity}"
            )
        
        db_part_usage = models.MaintenancePartUsage(**part_usage.dict())
        db.add(db_part_usage)
        
        # Create a transaction for the part consumption
        transaction = models.Transaction(
            transaction_type=models.TransactionType.CONSUMPTION.value,
            part_id=part_usage.part_id,
            from_warehouse_id=part_usage.warehouse_id,
            machine_id=maintenance.machine_id,
            quantity=part_usage.quantity,
            unit_of_measure=part.unit_of_measure or "units",
            performed_by_user_id=maintenance.performed_by_user_id,
            transaction_date=maintenance.maintenance_date,
            notes=f"Part used in maintenance: {part.name or 'Unknown Part'} for {getattr(maintenance.maintenance_type, 'value', 'unknown')} maintenance",
            reference_number=f"MAINT-PART-{uuid.uuid4().hex[:8]}"
        )
        db.add(transaction)
        
        db.commit()
        db.refresh(db_part_usage)
        
        # Get the part usage record with related data, handling null values
        result = {
            **db_part_usage.__dict__,
            "part_number": part.part_number or "Unknown",
            "part_name": part.name or "Unknown Part",
            "warehouse_name": warehouse.name or "Unknown Warehouse"
        }
        
        # Remove SQLAlchemy internal attributes
        result.pop('_sa_instance_state', None)
        
        logger.info(f"Successfully added part {part_usage.part_id} to maintenance {part_usage.maintenance_id}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error adding part to maintenance: {str(e)}")
        
        if isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=400, detail="Referenced maintenance, part, or warehouse does not exist")
        else:
            raise HTTPException(status_code=400, detail="Data integrity constraint violation")
            
    except DataError as e:
        db.rollback()
        logger.error(f"Data error adding part to maintenance: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data format provided")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error adding part to maintenance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while adding part to maintenance"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error adding part to maintenance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding part to maintenance"
        )

def get_machine_part_compatibility(db: Session, machine_id: uuid.UUID, skip: int = 0, limit: int = 100):
    """Get compatible parts for a specific machine."""
    try:
        # Validate input parameters
        if not machine_id:
            logger.error("get_machine_part_compatibility called with missing machine_id")
            raise HTTPException(status_code=400, detail="Machine ID is required")
            
        if skip < 0:
            logger.warning(f"Invalid skip parameter: {skip}, setting to 0")
            skip = 0
        if limit <= 0 or limit > 1000:
            logger.warning(f"Invalid limit parameter: {limit}, setting to 100")
            limit = 100
        
        # Check if machine exists
        machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not machine:
            logger.warning(f"Machine not found for compatibility check: {machine_id}")
            raise HTTPException(status_code=404, detail="Machine not found")
        
        # Temporarily return empty list due to missing machine_part_compatibility table
        # TODO: Implement proper part compatibility when table is created
        logger.info(f"Returning empty compatibility list for machine {machine_id} - table not implemented")
        return []
        
        # Get compatible parts with left join to handle missing parts gracefully
        # compatibility_records = db.query(
        #     models.MachinePartCompatibility,
        #     models.Part.part_number.label("part_number"),
        #     models.Part.name.label("part_name")
        # ).outerjoin(
        #     models.Part, models.MachinePartCompatibility.part_id == models.Part.id
        # ).filter(
        #     models.MachinePartCompatibility.machine_id == machine_id
        # ).order_by(
        #     models.MachinePartCompatibility.is_recommended.desc(),
        #     models.Part.part_number
        # ).offset(skip).limit(limit).all()
        
        # results = []
        # for compatibility, part_number, part_name in compatibility_records:
        #     # Handle null values gracefully
        #     result = {
        #         **compatibility.__dict__,
        #         "part_number": part_number or "Unknown",
        #         "part_name": part_name or "Unknown Part",
        #         "machine_name": machine.name or "Unknown Machine",
        #         "machine_model_type": machine.model_type or "Unknown Model"
        #     }
        #     
        #     # Remove SQLAlchemy internal attributes
        #     result.pop('_sa_instance_state', None)
        #     results.append(result)
        # 
        # logger.debug(f"Successfully retrieved {len(results)} compatibility records for machine {machine_id}")
        # return results
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving compatibility for machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving part compatibility"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving compatibility for machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving part compatibility"
        )

def add_compatible_part(db: Session, compatibility: schemas.MachinePartCompatibilityCreate):
    """Add a compatible part to a machine."""
    try:
        # Validate input parameters
        if not compatibility.machine_id:
            logger.error("add_compatible_part called with missing machine_id")
            raise HTTPException(status_code=400, detail="Machine ID is required")
            
        if not compatibility.part_id:
            logger.error("add_compatible_part called with missing part_id")
            raise HTTPException(status_code=400, detail="Part ID is required")
        
        # Check if machine exists
        machine = db.query(models.Machine).filter(models.Machine.id == compatibility.machine_id).first()
        if not machine:
            logger.warning(f"Machine not found for compatibility addition: {compatibility.machine_id}")
            raise HTTPException(status_code=404, detail="Machine not found")
        
        # Check if part exists
        part = db.query(models.Part).filter(models.Part.id == compatibility.part_id).first()
        if not part:
            logger.warning(f"Part not found for compatibility addition: {compatibility.part_id}")
            raise HTTPException(status_code=400, detail="Part not found")
        
        # Check if compatibility record already exists
        existing_compatibility = db.query(models.MachinePartCompatibility).filter(
            models.MachinePartCompatibility.machine_id == compatibility.machine_id,
            models.MachinePartCompatibility.part_id == compatibility.part_id
        ).first()
        
        if existing_compatibility:
            logger.info(f"Compatibility already exists between machine {compatibility.machine_id} and part {compatibility.part_id}")
            raise HTTPException(status_code=409, detail="Part is already marked as compatible with this machine")
        
        db_compatibility = models.MachinePartCompatibility(**compatibility.dict())
        db.add(db_compatibility)
        db.commit()
        db.refresh(db_compatibility)
        
        # Get the compatibility record with related data, handling null values
        result = {
            **db_compatibility.__dict__,
            "part_number": part.part_number or "Unknown",
            "part_name": part.name or "Unknown Part",
            "machine_name": machine.name or "Unknown Machine",
            "machine_model_type": machine.model_type or "Unknown Model"
        }
        
        # Remove SQLAlchemy internal attributes
        result.pop('_sa_instance_state', None)
        
        logger.info(f"Successfully added compatibility between machine {compatibility.machine_id} and part {compatibility.part_id}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error adding compatible part: {str(e)}")
        
        if isinstance(e.orig, UniqueViolation):
            raise HTTPException(status_code=409, detail="Part is already marked as compatible with this machine")
        elif isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=400, detail="Referenced machine or part does not exist")
        else:
            raise HTTPException(status_code=400, detail="Data integrity constraint violation")
            
    except DataError as e:
        db.rollback()
        logger.error(f"Data error adding compatible part: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data format provided")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error adding compatible part: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while adding compatible part"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error adding compatible part: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding compatible part"
        )

def remove_compatible_part(db: Session, machine_id: uuid.UUID, part_id: uuid.UUID):
    """Remove a compatible part from a machine."""
    try:
        # Validate input parameters
        if not machine_id:
            logger.error("remove_compatible_part called with missing machine_id")
            raise HTTPException(status_code=400, detail="Machine ID is required")
            
        if not part_id:
            logger.error("remove_compatible_part called with missing part_id")
            raise HTTPException(status_code=400, detail="Part ID is required")
        
        # Check if compatibility record exists
        compatibility = db.query(models.MachinePartCompatibility).filter(
            models.MachinePartCompatibility.machine_id == machine_id,
            models.MachinePartCompatibility.part_id == part_id
        ).first()
        
        if not compatibility:
            logger.info(f"Compatibility not found between machine {machine_id} and part {part_id}")
            raise HTTPException(status_code=404, detail="Part is not marked as compatible with this machine")
        
        db.delete(compatibility)
        db.commit()
        
        logger.info(f"Successfully removed compatibility between machine {machine_id} and part {part_id}")
        return {"message": "Compatible part removed successfully"}
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error removing compatible part: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while removing compatible part"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error removing compatible part: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while removing compatible part"
        )

def get_machine_usage_history(db: Session, machine_id: uuid.UUID, skip: int = 0, limit: int = 100):
    """Get part usage history for a specific machine."""
    try:
        # Validate input parameters
        if not machine_id:
            logger.error("get_machine_usage_history called with missing machine_id")
            raise HTTPException(status_code=400, detail="Machine ID is required")
            
        if skip < 0:
            logger.warning(f"Invalid skip parameter: {skip}, setting to 0")
            skip = 0
        if limit <= 0 or limit > 1000:
            logger.warning(f"Invalid limit parameter: {limit}, setting to 100")
            limit = 100
        
        # Check if machine exists
        machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not machine:
            logger.warning(f"Machine not found for usage history: {machine_id}")
            raise HTTPException(status_code=404, detail="Machine not found")
        
        # Temporarily return empty list due to missing part_usage table columns
        # TODO: Implement proper usage history when table schema is fixed
        logger.info(f"Returning empty usage history for machine {machine_id} - table schema not aligned")
        return []
        
        # Get part usage records with left joins to handle missing data gracefully
        # usage_records = db.query(
        #     models.PartUsage,
        #     models.Part.part_number.label("part_number"),
        #     models.Part.name.label("part_name"),
        #     models.User.username.label("recorded_by_username")
        # ).outerjoin(
        #     models.Part, models.PartUsage.part_id == models.Part.id
        # ).outerjoin(
        #     models.User, models.PartUsage.recorded_by_user_id == models.User.id
        # ).filter(
        #     models.PartUsage.machine_id == machine_id
        # ).order_by(
        #     desc(models.PartUsage.usage_date)
        # ).offset(skip).limit(limit).all()
        
        results = []
        for usage, part_number, part_name, recorded_by_username in usage_records:
            # Handle null values gracefully
            result = {
                **usage.__dict__,
                "part_number": part_number or "Unknown",
                "part_name": part_name or "Unknown Part",
                "recorded_by_username": recorded_by_username or "Unknown User",
                "machine_name": machine.name or "Unknown Machine"
            }
            
            # Remove SQLAlchemy internal attributes
            result.pop('_sa_instance_state', None)
            results.append(result)
        
        logger.debug(f"Successfully retrieved {len(results)} usage records for machine {machine_id}")
        return results
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving usage history for machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving usage history"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving usage history for machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving usage history"
        )


def get_machines_with_hours_data(db: Session, skip: int = 0, limit: int = 100, organization_id: Optional[uuid.UUID] = None):
    """
    Retrieve machines with enriched hours data for display in machine cards.
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func, desc
    
    logger.info(f"get_machines_with_hours_data called - org_id: {organization_id}")
    
    try:
        # Get basic machines
        machines = get_machines(db, skip, limit, organization_id)
        logger.info(f"Retrieved {len(machines)} machines to enrich")
        
        # Enrich each machine with hours data
        enriched_machines = []
        for machine in machines:
            # Get latest hours record
            latest_hours_record = db.query(models.MachineHours)\
                .filter(models.MachineHours.machine_id == machine.id)\
                .order_by(desc(models.MachineHours.recorded_date))\
                .first()
            
            if latest_hours_record:
                logger.info(f"Machine {machine.name}: Found hours record - {latest_hours_record.hours_value} hrs recorded on {latest_hours_record.recorded_date}")
            else:
                logger.info(f"Machine {machine.name}: No hours records found")
            
            # Get total hours records count
            total_records = db.query(models.MachineHours)\
                .filter(models.MachineHours.machine_id == machine.id)\
                .count()
            
            # Calculate days since last record
            days_since_last = None
            if latest_hours_record:
                from datetime import timezone
                # Ensure both datetimes are timezone-aware for comparison
                now = datetime.now(timezone.utc)
                recorded_date = latest_hours_record.recorded_date
                if recorded_date.tzinfo is None:
                    recorded_date = recorded_date.replace(tzinfo=timezone.utc)
                days_since_last = (now - recorded_date).days
            
            # Create enriched machine data - include all base fields
            machine_dict = {
                'id': machine.id,
                'customer_organization_id': machine.customer_organization_id,
                'model_type': machine.model_type,
                'name': machine.name,
                'serial_number': machine.serial_number,
                # Include all MachineBase fields
                'purchase_date': getattr(machine, 'purchase_date', None),
                'warranty_expiry_date': getattr(machine, 'warranty_expiry_date', None),
                'status': getattr(machine, 'status', 'active'),
                'last_maintenance_date': getattr(machine, 'last_maintenance_date', None),
                'next_maintenance_date': getattr(machine, 'next_maintenance_date', None),
                'location': getattr(machine, 'location', None),
                'notes': getattr(machine, 'notes', None),
                # BaseSchema fields
                'created_at': machine.created_at,
                'updated_at': machine.updated_at,
                # Enriched fields
                'latest_hours': float(latest_hours_record.hours_value) if latest_hours_record else None,
                'latest_hours_date': latest_hours_record.recorded_date if latest_hours_record else None,
                'days_since_last_hours_record': days_since_last,
                'total_hours_records': total_records,
                'customer_organization_name': machine.customer_organization.name if machine.customer_organization else None
            }
            
            enriched_machines.append(machine_dict)
        
        logger.info(f"Returning {len(enriched_machines)} enriched machines")
        # Log first machine to verify data structure
        if enriched_machines:
            logger.info(f"Sample enriched machine: {enriched_machines[0]}")
        return enriched_machines
        
    except Exception as e:
        logger.error(f"Error enriching machines with hours data: {str(e)}", exc_info=True)
        # Fall back to basic machines if enrichment fails
        logger.warning("Falling back to basic machines without hours data")
        return get_machines(db, skip, limit, organization_id)

def get_machine_hours_history(db: Session, machine_id: uuid.UUID, skip: int = 0, limit: int = 50):
    """
    Get machine hours history for a specific machine.
    """
    try:
        hours_records = db.query(models.MachineHours)\
            .filter(models.MachineHours.machine_id == machine_id)\
            .order_by(models.MachineHours.recorded_date.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return hours_records
        
    except Exception as e:
        logger.error(f"Error getting machine hours history: {str(e)}")
        return []

def get_machine_hours_chart_data(db: Session, machine_id: uuid.UUID, days: int = 90):
    """
    Get machine hours data for charting (last N days).
    """
    from datetime import datetime, timedelta
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        hours_records = db.query(models.MachineHours)\
            .filter(
                models.MachineHours.machine_id == machine_id,
                models.MachineHours.recorded_date >= cutoff_date
            )\
            .order_by(models.MachineHours.recorded_date.asc())\
            .all()
        
        # Format for chart
        chart_data = []
        for record in hours_records:
            chart_data.append({
                'date': record.recorded_date.strftime('%Y-%m-%d'),
                'hours': float(record.hours_value),
                'recorded_by': record.recorded_by_user.username if record.recorded_by_user else 'Unknown'
            })
        
        return chart_data
        
    except Exception as e:
        logger.error(f"Error getting machine hours chart data: {str(e)}")
        return []