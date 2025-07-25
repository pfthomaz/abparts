# backend/app/routers/machines.py

import uuid
import logging
from typing import List, Optional
from datetime import datetime
from functools import wraps

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError, OperationalError, TimeoutError
from pydantic import BaseModel

from .. import schemas # Import schemas
from ..crud import machines # Corrected: Import machines directly from crud
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, TokenData # Import authentication dependencies
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_super_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)

# Set up logging for machine endpoints
logger = logging.getLogger(__name__)

# Enhanced error response models
class MachineErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: datetime
    resource: str = "machine"
    
class MachineErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: Optional[str] = None

router = APIRouter()

# Machine-specific error handling decorator
def handle_machine_errors(operation_name: str):
    """
    Decorator for comprehensive error handling in machine endpoints.
    Provides structured error responses and detailed logging.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            request_id = None
            
            # Extract request object from kwargs for logging
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
                    break
            
            # If no request found in args, check kwargs
            if not request:
                request = kwargs.get('request')
                if request:
                    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
            
            # Generate request_id if not found
            if not request_id:
                request_id = str(uuid.uuid4())
            
            try:
                # Log the start of the operation
                logger.info(f"Starting {operation_name} operation - Request ID: {request_id}")
                
                # Execute the original function
                result = await func(*args, **kwargs)
                
                # Log successful completion
                logger.info(f"Successfully completed {operation_name} operation - Request ID: {request_id}")
                
                return result
                
            except HTTPException as e:
                # Log HTTP exceptions with context
                logger.warning(f"{operation_name} failed with HTTP {e.status_code}: {e.detail} - Request ID: {request_id}")
                
                # Enhance the error response with additional context
                if hasattr(e, 'detail') and isinstance(e.detail, str):
                    enhanced_detail = {
                        "detail": e.detail,
                        "error_code": getattr(e, 'error_code', None),
                        "request_id": request_id,
                        "timestamp": datetime.utcnow(),
                        "resource": "machine",
                        "operation": operation_name
                    }
                    e.detail = enhanced_detail
                
                raise e
                
            except IntegrityError as e:
                logger.error(f"{operation_name} failed with integrity error: {str(e)} - Request ID: {request_id}")
                
                # Handle specific database constraint violations
                error_detail = "Data integrity constraint violation"
                status_code = status.HTTP_409_CONFLICT
                
                if "unique" in str(e).lower():
                    if "serial_number" in str(e).lower():
                        error_detail = "Machine with this serial number already exists"
                    else:
                        error_detail = "Machine data violates uniqueness constraint"
                elif "foreign key" in str(e).lower():
                    error_detail = "Referenced organization does not exist"
                    status_code = status.HTTP_400_BAD_REQUEST
                
                raise HTTPException(
                    status_code=status_code,
                    detail={
                        "detail": error_detail,
                        "error_code": "INTEGRITY_ERROR",
                        "request_id": request_id,
                        "timestamp": datetime.utcnow(),
                        "resource": "machine",
                        "operation": operation_name
                    }
                )
                
            except (OperationalError, TimeoutError) as e:
                logger.error(f"{operation_name} failed with database connection/timeout error: {str(e)} - Request ID: {request_id}")
                
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "detail": "Database service temporarily unavailable. Please try again later.",
                        "error_code": "DATABASE_UNAVAILABLE",
                        "request_id": request_id,
                        "timestamp": datetime.utcnow(),
                        "resource": "machine",
                        "operation": operation_name
                    }
                )
                
            except DataError as e:
                logger.error(f"{operation_name} failed with data error: {str(e)} - Request ID: {request_id}")
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "detail": "Invalid data format provided",
                        "error_code": "INVALID_DATA_FORMAT",
                        "request_id": request_id,
                        "timestamp": datetime.utcnow(),
                        "resource": "machine",
                        "operation": operation_name
                    }
                )
                
            except SQLAlchemyError as e:
                logger.error(f"{operation_name} failed with database error: {str(e)} - Request ID: {request_id}")
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "detail": f"Database error occurred during {operation_name}",
                        "error_code": "DATABASE_ERROR",
                        "request_id": request_id,
                        "timestamp": datetime.utcnow(),
                        "resource": "machine",
                        "operation": operation_name
                    }
                )
                
            except Exception as e:
                logger.error(f"{operation_name} failed with unexpected error: {str(e)} - Request ID: {request_id}", exc_info=True)
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "detail": f"An unexpected error occurred during {operation_name}",
                        "error_code": "UNEXPECTED_ERROR",
                        "request_id": request_id,
                        "timestamp": datetime.utcnow(),
                        "resource": "machine",
                        "operation": operation_name
                    }
                )
                
        return wrapper
    return decorator

# Enhanced authentication error handler
def handle_auth_errors(func):
    """
    Decorator to handle authentication and authorization errors with detailed logging.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            if e.status_code == status.HTTP_401_UNAUTHORIZED:
                logger.warning(f"Authentication failed for machine endpoint: {func.__name__}")
                e.detail = {
                    "detail": "Authentication required. Please provide a valid token.",
                    "error_code": "AUTHENTICATION_REQUIRED",
                    "timestamp": datetime.utcnow(),
                    "resource": "machine"
                }
            elif e.status_code == status.HTTP_403_FORBIDDEN:
                logger.warning(f"Authorization failed for machine endpoint: {func.__name__}")
                e.detail = {
                    "detail": "Insufficient permissions for this machine operation.",
                    "error_code": "INSUFFICIENT_PERMISSIONS",
                    "timestamp": datetime.utcnow(),
                    "resource": "machine"
                }
            raise e
    return wrapper

# Request/Response logging middleware for machine endpoints
async def log_machine_request(request: Request, endpoint_name: str):
    """Log machine endpoint requests with relevant details."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    client_ip = request.client.host if request.client else "unknown"
    
    logger.info(f"Machine API Request - {endpoint_name}: {request.method} {request.url} from {client_ip} - Request ID: {request_id}")
    
    # Log request headers for debugging (excluding sensitive data)
    headers_to_log = {k: v for k, v in request.headers.items() if k.lower() not in ['authorization', 'cookie']}
    logger.debug(f"Request headers - Request ID {request_id}: {headers_to_log}")

async def log_machine_response(request: Request, response_data, endpoint_name: str, status_code: int = 200):
    """Log machine endpoint responses with relevant details."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    logger.info(f"Machine API Response - {endpoint_name}: Status {status_code} - Request ID: {request_id}")
    
    # Log response summary (avoid logging sensitive data)
    if isinstance(response_data, list):
        logger.debug(f"Response summary - Request ID {request_id}: Returned {len(response_data)} items")
    elif isinstance(response_data, dict) and 'id' in response_data:
        logger.debug(f"Response summary - Request ID {request_id}: Returned machine with ID {response_data.get('id')}")
    else:
        logger.debug(f"Response summary - Request ID {request_id}: Operation completed successfully")

# --- Machines CRUD ---
@router.get("/", response_model=List[schemas.MachineResponse])
@handle_auth_errors
@handle_machine_errors("get_machines")
async def get_machines(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Retrieve a list of machines with organization-scoped filtering.
    Super admins see all machines, regular users see only their organization's machines.
    """
    await log_machine_request(request, "get_machines")
    
    # Validate pagination parameters
    if skip < 0:
        logger.warning(f"Invalid skip parameter: {skip}, setting to 0")
        skip = 0
    if limit <= 0 or limit > 1000:
        logger.warning(f"Invalid limit parameter: {limit}, setting to 100")
        limit = 100
    
    # If user is not a super_admin, filter machines by organization
    if not permission_checker.is_super_admin(current_user):
        machines_data = machines.get_machines(db, skip, limit, current_user.organization_id)
    else:
        machines_data = machines.get_machines(db, skip, limit)
    
    await log_machine_response(request, machines_data, "get_machines")
    return machines_data

@router.get("/{machine_id}", response_model=schemas.MachineResponse)
@handle_auth_errors
@handle_machine_errors("get_machine")
async def get_machine(
    machine_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Retrieve a single machine by ID with organization access control.
    """
    await log_machine_request(request, f"get_machine/{machine_id}")
    
    # Validate machine_id
    if not machine_id:
        logger.error("get_machine called with invalid machine_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid machine ID provided"
        )
    
    machine = machines.get_machine(db, machine_id)
    if not machine:
        logger.info(f"Machine not found: {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )

    # Check if user can access this machine's organization
    if not check_organization_access(current_user, machine.customer_organization_id, db):
        logger.warning(f"User {current_user.user_id} attempted to access machine {machine_id} without proper organization access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this machine"
        )

    await log_machine_response(request, machine.__dict__, "get_machine")
    return machine

@router.post("/", response_model=schemas.MachineResponse, status_code=status.HTTP_201_CREATED)
@handle_auth_errors
@handle_machine_errors("create_machine")
async def create_machine(
    machine: schemas.MachineCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Create a new machine. Only super admins can register machines.
    """
    await log_machine_request(request, "create_machine")
    
    # Additional validation: ensure the target organization exists and user can access it
    if not permission_checker.is_super_admin(current_user):
        logger.warning(f"Non-super admin user {current_user.user_id} attempted to create machine")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can register machines"
        )
    
    # Validate required fields
    if not machine.customer_organization_id:
        logger.error("create_machine called with missing customer_organization_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer organization ID is required"
        )
    
    if not machine.serial_number or not machine.serial_number.strip():
        logger.error("create_machine called with missing or empty serial_number")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Serial number is required and cannot be empty"
        )
    
    db_machine = machines.create_machine(db, machine)
    if not db_machine:
        logger.error("Machine creation failed - create_machine returned None")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create machine"
        )
    
    await log_machine_response(request, db_machine.__dict__, "create_machine", status.HTTP_201_CREATED)
    return db_machine

@router.put("/{machine_id}", response_model=schemas.MachineResponse)
@handle_auth_errors
@handle_machine_errors("update_machine")
async def update_machine(
    machine_id: uuid.UUID,
    machine_update: schemas.MachineUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Update an existing machine. Only super admins can update machines.
    """
    await log_machine_request(request, f"update_machine/{machine_id}")
    
    # Validate machine_id
    if not machine_id:
        logger.error("update_machine called with invalid machine_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid machine ID provided"
        )
    
    db_machine = machines.get_machine(db, machine_id)
    if not db_machine:
        logger.info(f"Machine not found for update: {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )

    # Only super admins can update machines
    if not permission_checker.is_super_admin(current_user):
        logger.warning(f"Non-super admin user {current_user.user_id} attempted to update machine {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can update machines"
        )

    # Validate update data
    update_data = machine_update.dict(exclude_unset=True)
    if not update_data:
        logger.info(f"No update data provided for machine: {machine_id}")
        await log_machine_response(request, db_machine.__dict__, "update_machine")
        return db_machine

    updated_machine = machines.update_machine(db, machine_id, machine_update)
    if not updated_machine:
        logger.error(f"Machine update failed - update_machine returned None for machine {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update machine"
        )
    
    await log_machine_response(request, updated_machine.__dict__, "update_machine")
    return updated_machine

@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_auth_errors
@handle_machine_errors("delete_machine")
async def delete_machine(
    machine_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.DELETE))
):
    """
    Delete a machine by ID. Only super admins can delete machines.
    """
    await log_machine_request(request, f"delete_machine/{machine_id}")
    
    # Validate machine_id
    if not machine_id:
        logger.error("delete_machine called with invalid machine_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid machine ID provided"
        )
    
    db_machine = machines.get_machine(db, machine_id)
    if not db_machine:
        logger.info(f"Machine not found for deletion: {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )

    # Only super admins can delete machines
    if not permission_checker.is_super_admin(current_user):
        logger.warning(f"Non-super admin user {current_user.user_id} attempted to delete machine {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can delete machines"
        )

    result = machines.delete_machine(db, machine_id)
    if not result:
        logger.error(f"Machine deletion failed - delete_machine returned None for machine {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete machine. Check for dependent records."
        )
    
    await log_machine_response(request, {"deleted": True}, "delete_machine", status.HTTP_204_NO_CONTENT)
    return result

# --- Machine Transfer ---
@router.post("/transfer", response_model=schemas.MachineResponse)
@handle_auth_errors
@handle_machine_errors("transfer_machine")
async def transfer_machine(
    transfer: schemas.MachineTransferRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Transfer a machine to a new customer organization.
    Only super admins can transfer machines.
    """
    await log_machine_request(request, f"transfer_machine/{transfer.machine_id}")
    
    # Validate transfer request
    if not transfer.machine_id:
        logger.error("transfer_machine called with missing machine_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Machine ID is required for transfer"
        )
    
    if not transfer.new_customer_organization_id:
        logger.error("transfer_machine called with missing new_customer_organization_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New customer organization ID is required for transfer"
        )
    
    # Check if machine exists
    machine = machines.get_machine(db, transfer.machine_id)
    if not machine:
        logger.info(f"Machine not found for transfer: {transfer.machine_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    # Only super admins can transfer machines
    if not permission_checker.is_super_admin(current_user):
        logger.warning(f"Non-super admin user {current_user.user_id} attempted to transfer machine {transfer.machine_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can transfer machines"
        )
    
    # Transfer the machine
    transferred_machine = machines.transfer_machine(db, transfer)
    if not transferred_machine:
        logger.error(f"Machine transfer failed - transfer_machine returned None for machine {transfer.machine_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transfer machine"
        )
    
    await log_machine_response(request, transferred_machine.__dict__, "transfer_machine")
    return transferred_machine

# --- Machine Maintenance ---
@router.get("/{machine_id}/maintenance", response_model=List[schemas.MaintenanceResponse])
@handle_auth_errors
@handle_machine_errors("get_machine_maintenance_history")
async def get_machine_maintenance_history(
    machine_id: uuid.UUID,
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get maintenance history for a specific machine.
    Users can only view maintenance history for machines owned by their organization.
    """
    await log_machine_request(request, f"get_machine_maintenance_history/{machine_id}")
    
    # Validate parameters
    if not machine_id:
        logger.error("get_machine_maintenance_history called with invalid machine_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid machine ID provided"
        )
    
    if skip < 0:
        logger.warning(f"Invalid skip parameter: {skip}, setting to 0")
        skip = 0
    if limit <= 0 or limit > 1000:
        logger.warning(f"Invalid limit parameter: {limit}, setting to 100")
        limit = 100
    
    # Check if machine exists and user has access to it
    machine = machines.get_machine(db, machine_id)
    if not machine:
        logger.info(f"Machine not found for maintenance history: {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    # Check if user can access this machine's organization
    if not check_organization_access(current_user, machine.customer_organization_id, db):
        logger.warning(f"User {current_user.user_id} attempted to access maintenance history for machine {machine_id} without proper organization access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this machine's maintenance history"
        )
    
    # Get maintenance history
    maintenance_history = machines.get_machine_maintenance_history(db, machine_id, skip, limit)
    
    await log_machine_response(request, maintenance_history, "get_machine_maintenance_history")
    return maintenance_history

@router.post("/{machine_id}/maintenance", response_model=schemas.MaintenanceResponse, status_code=status.HTTP_201_CREATED)
@handle_auth_errors
@handle_machine_errors("create_machine_maintenance")
async def create_machine_maintenance(
    machine_id: uuid.UUID,
    maintenance: schemas.MaintenanceCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Create a new maintenance record for a machine.
    Users can only create maintenance records for machines owned by their organization.
    """
    await log_machine_request(request, f"create_machine_maintenance/{machine_id}")
    
    # Validate parameters
    if not machine_id:
        logger.error("create_machine_maintenance called with invalid machine_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid machine ID provided"
        )
    
    # Check if machine exists and user has access to it
    machine = machines.get_machine(db, machine_id)
    if not machine:
        logger.info(f"Machine not found for maintenance creation: {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    # Check if user can access this machine's organization
    if not check_organization_access(current_user, machine.customer_organization_id, db):
        logger.warning(f"User {current_user.user_id} attempted to create maintenance record for machine {machine_id} without proper organization access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create maintenance records for this machine"
        )
    
    # Ensure the machine_id in the path matches the machine_id in the request body
    if maintenance.machine_id != machine_id:
        logger.info(f"Correcting machine_id in maintenance request from {maintenance.machine_id} to {machine_id}")
        maintenance.machine_id = machine_id
    
    # Set performed_by_user_id to current user if not provided
    if not maintenance.performed_by_user_id:
        logger.info(f"Setting performed_by_user_id to current user: {current_user.user_id}")
        maintenance.performed_by_user_id = current_user.user_id
    
    # Create maintenance record
    maintenance_record = machines.create_machine_maintenance(db, maintenance)
    if not maintenance_record:
        logger.error(f"Maintenance record creation failed - create_machine_maintenance returned None for machine {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create maintenance record"
        )
    
    await log_machine_response(request, maintenance_record.__dict__, "create_machine_maintenance", status.HTTP_201_CREATED)
    return maintenance_record

@router.post("/{machine_id}/maintenance/{maintenance_id}/parts", response_model=schemas.MaintenancePartUsageResponse, status_code=status.HTTP_201_CREATED)
@handle_auth_errors
@handle_machine_errors("add_part_to_maintenance")
async def add_part_to_maintenance(
    machine_id: uuid.UUID,
    maintenance_id: uuid.UUID,
    part_usage: schemas.MaintenancePartUsageCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Add a part to a maintenance record.
    Users can only add parts to maintenance records for machines owned by their organization.
    """
    await log_machine_request(request, f"add_part_to_maintenance/{machine_id}/{maintenance_id}")
    
    # Validate parameters
    if not machine_id:
        logger.error("add_part_to_maintenance called with invalid machine_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid machine ID provided"
        )
    
    if not maintenance_id:
        logger.error("add_part_to_maintenance called with invalid maintenance_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid maintenance ID provided"
        )
    
    # Check if machine exists and user has access to it
    machine = machines.get_machine(db, machine_id)
    if not machine:
        logger.info(f"Machine not found for part addition to maintenance: {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    # Check if user can access this machine's organization
    if not check_organization_access(current_user, machine.customer_organization_id, db):
        logger.warning(f"User {current_user.user_id} attempted to add parts to maintenance for machine {machine_id} without proper organization access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add parts to maintenance records for this machine"
        )
    
    # Ensure the maintenance_id in the path matches the maintenance_id in the request body
    if part_usage.maintenance_id != maintenance_id:
        logger.info(f"Correcting maintenance_id in part usage request from {part_usage.maintenance_id} to {maintenance_id}")
        part_usage.maintenance_id = maintenance_id
    
    # Add part to maintenance record
    part_usage_record = machines.add_part_to_maintenance(db, part_usage)
    if not part_usage_record:
        logger.error(f"Part addition to maintenance failed - add_part_to_maintenance returned None for machine {machine_id}, maintenance {maintenance_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add part to maintenance record"
        )
    
    await log_machine_response(request, part_usage_record.__dict__, "add_part_to_maintenance", status.HTTP_201_CREATED)
    return part_usage_record

# --- Machine Part Compatibility ---
@router.get("/{machine_id}/compatible-parts", response_model=List[schemas.MachinePartCompatibilityResponse])
@handle_auth_errors
@handle_machine_errors("get_machine_part_compatibility")
async def get_machine_part_compatibility(
    machine_id: uuid.UUID,
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get compatible parts for a specific machine.
    Users can only view compatible parts for machines owned by their organization.
    """
    await log_machine_request(request, f"get_machine_part_compatibility/{machine_id}")
    
    # Validate parameters
    if not machine_id:
        logger.error("get_machine_part_compatibility called with invalid machine_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid machine ID provided"
        )
    
    if skip < 0:
        logger.warning(f"Invalid skip parameter: {skip}, setting to 0")
        skip = 0
    if limit <= 0 or limit > 1000:
        logger.warning(f"Invalid limit parameter: {limit}, setting to 100")
        limit = 100
    
    # Check if machine exists and user has access to it
    machine = machines.get_machine(db, machine_id)
    if not machine:
        logger.info(f"Machine not found for part compatibility: {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    # Check if user can access this machine's organization
    if not check_organization_access(current_user, machine.customer_organization_id, db):
        logger.warning(f"User {current_user.user_id} attempted to view compatible parts for machine {machine_id} without proper organization access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view compatible parts for this machine"
        )
    
    # Get compatible parts
    compatible_parts = machines.get_machine_part_compatibility(db, machine_id, skip, limit)
    
    await log_machine_response(request, compatible_parts, "get_machine_part_compatibility")
    return compatible_parts

@router.post("/{machine_id}/compatible-parts", response_model=schemas.MachinePartCompatibilityResponse, status_code=status.HTTP_201_CREATED)
@handle_auth_errors
@handle_machine_errors("add_compatible_part")
async def add_compatible_part(
    machine_id: uuid.UUID,
    compatibility: schemas.MachinePartCompatibilityCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Add a compatible part to a machine.
    Only super admins can add compatible parts to machines.
    """
    await log_machine_request(request, f"add_compatible_part/{machine_id}")
    
    # Validate parameters
    if not machine_id:
        logger.error("add_compatible_part called with invalid machine_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid machine ID provided"
        )
    
    # Check if machine exists
    machine = machines.get_machine(db, machine_id)
    if not machine:
        logger.info(f"Machine not found for adding compatible part: {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    # Only super admins can add compatible parts to machines
    if not permission_checker.is_super_admin(current_user):
        logger.warning(f"Non-super admin user {current_user.user_id} attempted to add compatible part to machine {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can add compatible parts to machines"
        )
    
    # Ensure the machine_id in the path matches the machine_id in the request body
    if compatibility.machine_id != machine_id:
        logger.info(f"Correcting machine_id in compatibility request from {compatibility.machine_id} to {machine_id}")
        compatibility.machine_id = machine_id
    
    # Add compatible part
    compatible_part = machines.add_compatible_part(db, compatibility)
    if not compatible_part:
        logger.error(f"Compatible part addition failed - add_compatible_part returned None for machine {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add compatible part"
        )
    
    await log_machine_response(request, compatible_part.__dict__, "add_compatible_part", status.HTTP_201_CREATED)
    return compatible_part

@router.delete("/{machine_id}/compatible-parts/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_auth_errors
@handle_machine_errors("remove_compatible_part")
async def remove_compatible_part(
    machine_id: uuid.UUID,
    part_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.DELETE))
):
    """
    Remove a compatible part from a machine.
    Only super admins can remove compatible parts from machines.
    """
    await log_machine_request(request, f"remove_compatible_part/{machine_id}/{part_id}")
    
    # Validate parameters
    if not machine_id:
        logger.error("remove_compatible_part called with invalid machine_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid machine ID provided"
        )
    
    if not part_id:
        logger.error("remove_compatible_part called with invalid part_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid part ID provided"
        )
    
    # Check if machine exists
    machine = machines.get_machine(db, machine_id)
    if not machine:
        logger.info(f"Machine not found for removing compatible part: {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    # Only super admins can remove compatible parts from machines
    if not permission_checker.is_super_admin(current_user):
        logger.warning(f"Non-super admin user {current_user.user_id} attempted to remove compatible part from machine {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can remove compatible parts from machines"
        )
    
    # Remove compatible part
    result = machines.remove_compatible_part(db, machine_id, part_id)
    if not result:
        logger.error(f"Compatible part removal failed - remove_compatible_part returned None for machine {machine_id}, part {part_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove compatible part"
        )
    
    await log_machine_response(request, {"removed": True}, "remove_compatible_part", status.HTTP_204_NO_CONTENT)
    return result

# --- Machine Usage History ---
@router.get("/{machine_id}/usage-history", response_model=List[schemas.PartUsageResponse])
@handle_auth_errors
@handle_machine_errors("get_machine_usage_history")
async def get_machine_usage_history(
    machine_id: uuid.UUID,
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get part usage history for a specific machine.
    Users can only view usage history for machines owned by their organization.
    """
    await log_machine_request(request, f"get_machine_usage_history/{machine_id}")
    
    # Validate parameters
    if not machine_id:
        logger.error("get_machine_usage_history called with invalid machine_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid machine ID provided"
        )
    
    if skip < 0:
        logger.warning(f"Invalid skip parameter: {skip}, setting to 0")
        skip = 0
    if limit <= 0 or limit > 1000:
        logger.warning(f"Invalid limit parameter: {limit}, setting to 100")
        limit = 100
    
    # Check if machine exists and user has access to it
    machine = machines.get_machine(db, machine_id)
    if not machine:
        logger.info(f"Machine not found for usage history: {machine_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    # Check if user can access this machine's organization
    if not check_organization_access(current_user, machine.customer_organization_id, db):
        logger.warning(f"User {current_user.user_id} attempted to view usage history for machine {machine_id} without proper organization access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view usage history for this machine"
        )
    
    # Get usage history
    usage_history = machines.get_machine_usage_history(db, machine_id, skip, limit)
    
    await log_machine_response(request, usage_history, "get_machine_usage_history")
    return usage_history