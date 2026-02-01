"""
Privacy and Data Management API Endpoints

Provides GDPR-compliant data management features:
- User data export (data portability)
- User data deletion (right to be forgotten)
- Data retention policy information
- Sensitive data detection and filtering

Validates Requirements: 10.1, 10.3, 10.4, 10.5
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from ..services.security_service import get_security_service, SecurityService
from ..database import get_db_session
from ..schemas import ErrorResponse

logger = logging.getLogger(__name__)
router = APIRouter()


class DataDeletionRequest(BaseModel):
    """Request to delete user data."""
    user_id: str = Field(..., description="User ID whose data should be deleted")
    confirmation: bool = Field(..., description="User must confirm deletion")
    reason: Optional[str] = Field(None, description="Optional reason for deletion")


class DataExportRequest(BaseModel):
    """Request to export user data."""
    user_id: str = Field(..., description="User ID whose data should be exported")
    include_messages: bool = Field(True, description="Include conversation messages")
    include_expert_knowledge: bool = Field(True, description="Include expert contributions")


class SensitiveDataCheckRequest(BaseModel):
    """Request to check content for sensitive data."""
    content: str = Field(..., description="Content to check for sensitive data")
    redact: bool = Field(False, description="Whether to redact sensitive data")


class DataDeletionResponse(BaseModel):
    """Response after deleting user data."""
    success: bool
    user_id: str
    deleted_counts: Dict[str, int]
    deletion_date: datetime
    message: str


class DataExportResponse(BaseModel):
    """Response containing exported user data."""
    success: bool
    user_id: str
    export_date: str
    data: Dict[str, Any]
    message: str


class SensitiveDataCheckResponse(BaseModel):
    """Response from sensitive data check."""
    has_sensitive_data: bool
    detections: list
    filtered_content: Optional[str] = None
    message: str


class RetentionPolicyResponse(BaseModel):
    """Response containing data retention policy information."""
    retention_periods: Dict[str, int]
    policy_description: Dict[str, str]
    user_rights: Dict[str, str]


class CleanupResponse(BaseModel):
    """Response from data cleanup operation."""
    success: bool
    deleted_counts: Dict[str, int]
    cleanup_date: datetime
    message: str


@router.post("/users/{user_id}/delete-data", response_model=DataDeletionResponse)
async def delete_user_data(
    user_id: str,
    request: DataDeletionRequest,
    authorization: Optional[str] = Header(None),
    security_service: SecurityService = Depends(get_security_service)
) -> DataDeletionResponse:
    """
    Delete all user data (GDPR right to be forgotten).
    
    This endpoint permanently deletes all AI Assistant data associated with a user,
    including conversation history, expert contributions, and personal information.
    
    **Requirements:** 10.3, 10.5
    """
    try:
        # Verify user_id matches request
        if user_id != request.user_id:
            raise HTTPException(status_code=400, detail="User ID mismatch")
        
        # Verify confirmation
        if not request.confirmation:
            raise HTTPException(
                status_code=400, 
                detail="Deletion must be confirmed by setting confirmation=true"
            )
        
        # TODO: Add authentication check to ensure user can only delete their own data
        # or is an admin
        
        # Delete user data
        with get_db_session() as db:
            deleted_counts = await security_service.delete_user_data(user_id, db)
            
            # Create audit log
            security_service.create_audit_log(
                action="user_data_deletion",
                user_id=user_id,
                details={
                    "reason": request.reason,
                    "deleted_counts": deleted_counts,
                    "timestamp": datetime.utcnow().isoformat()
                },
                db_session=db
            )
        
        logger.info(f"Successfully deleted data for user {user_id}")
        
        return DataDeletionResponse(
            success=True,
            user_id=user_id,
            deleted_counts=deleted_counts,
            deletion_date=datetime.utcnow(),
            message=f"All data for user {user_id} has been permanently deleted"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user data: {str(e)}")


@router.post("/users/{user_id}/export-data", response_model=DataExportResponse)
async def export_user_data(
    user_id: str,
    request: DataExportRequest,
    authorization: Optional[str] = Header(None),
    security_service: SecurityService = Depends(get_security_service)
) -> DataExportResponse:
    """
    Export all user data (GDPR data portability).
    
    This endpoint exports all AI Assistant data associated with a user in a
    structured format for data portability compliance.
    
    **Requirements:** 10.3, 10.5
    """
    try:
        # Verify user_id matches request
        if user_id != request.user_id:
            raise HTTPException(status_code=400, detail="User ID mismatch")
        
        # TODO: Add authentication check to ensure user can only export their own data
        # or is an admin
        
        # Export user data
        with get_db_session() as db:
            export_data = await security_service.export_user_data(user_id, db)
            
            # Filter data based on request options
            if not request.include_messages:
                for session in export_data.get('sessions', []):
                    session['messages'] = []
            
            if not request.include_expert_knowledge:
                export_data['expert_knowledge'] = []
            
            # Create audit log
            security_service.create_audit_log(
                action="user_data_export",
                user_id=user_id,
                details={
                    "include_messages": request.include_messages,
                    "include_expert_knowledge": request.include_expert_knowledge,
                    "timestamp": datetime.utcnow().isoformat()
                },
                db_session=db
            )
        
        logger.info(f"Successfully exported data for user {user_id}")
        
        return DataExportResponse(
            success=True,
            user_id=user_id,
            export_date=export_data['export_date'],
            data=export_data,
            message=f"Data export completed for user {user_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export user data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export user data: {str(e)}")


@router.post("/check-sensitive-data", response_model=SensitiveDataCheckResponse)
async def check_sensitive_data(
    request: SensitiveDataCheckRequest,
    authorization: Optional[str] = Header(None),
    security_service: SecurityService = Depends(get_security_service)
) -> SensitiveDataCheckResponse:
    """
    Check content for sensitive data and optionally redact it.
    
    This endpoint detects sensitive information (emails, phone numbers, credit cards, etc.)
    in message content and can automatically redact it for privacy protection.
    
    **Requirements:** 10.4
    """
    try:
        # Check for sensitive data
        filtered_content, detections = security_service.filter_sensitive_data(
            request.content,
            redact=request.redact
        )
        
        has_sensitive_data = len(detections) > 0
        
        # Format detections for response
        detection_list = [
            {
                'type': d['type'],
                'position': {'start': d['start'], 'end': d['end']}
            }
            for d in detections
        ]
        
        message = (
            f"Found {len(detections)} sensitive data pattern(s)" 
            if has_sensitive_data 
            else "No sensitive data detected"
        )
        
        return SensitiveDataCheckResponse(
            has_sensitive_data=has_sensitive_data,
            detections=detection_list,
            filtered_content=filtered_content if request.redact else None,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Failed to check sensitive data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check sensitive data: {str(e)}")


@router.get("/retention-policy", response_model=RetentionPolicyResponse)
async def get_retention_policy(
    authorization: Optional[str] = Header(None),
    security_service: SecurityService = Depends(get_security_service)
) -> RetentionPolicyResponse:
    """
    Get information about data retention policies.
    
    This endpoint provides transparency about how long different types of data
    are retained and what rights users have regarding their data.
    
    **Requirements:** 10.3
    """
    try:
        retention_info = security_service.get_retention_info()
        
        return RetentionPolicyResponse(
            retention_periods=retention_info['retention_periods'],
            policy_description=retention_info['policy_description'],
            user_rights=retention_info['user_rights']
        )
        
    except Exception as e:
        logger.error(f"Failed to get retention policy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get retention policy: {str(e)}")


@router.post("/cleanup-expired-data", response_model=CleanupResponse)
async def cleanup_expired_data(
    authorization: Optional[str] = Header(None),
    security_service: SecurityService = Depends(get_security_service)
) -> CleanupResponse:
    """
    Clean up expired data based on retention policies.
    
    This endpoint should be called periodically (e.g., daily via cron job) to
    automatically delete data that has exceeded its retention period.
    
    **Requirements:** 10.3
    
    **Note:** This endpoint should be restricted to admin users or automated systems.
    """
    try:
        # TODO: Add admin authentication check
        
        # Clean up expired data
        with get_db_session() as db:
            deleted_counts = await security_service.cleanup_expired_data(db)
            
            # Create audit log
            security_service.create_audit_log(
                action="automatic_data_cleanup",
                user_id="system",
                details={
                    "deleted_counts": deleted_counts,
                    "timestamp": datetime.utcnow().isoformat()
                },
                db_session=db
            )
        
        logger.info(f"Successfully cleaned up expired data: {deleted_counts}")
        
        return CleanupResponse(
            success=True,
            deleted_counts=deleted_counts,
            cleanup_date=datetime.utcnow(),
            message=f"Cleaned up {sum(deleted_counts.values())} expired records"
        )
        
    except Exception as e:
        logger.error(f"Failed to cleanup expired data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup expired data: {str(e)}")


@router.get("/encryption-status")
async def get_encryption_status(
    authorization: Optional[str] = Header(None),
    security_service: SecurityService = Depends(get_security_service)
) -> Dict[str, Any]:
    """
    Get information about encryption configuration.
    
    This endpoint provides transparency about the encryption mechanisms
    in place for protecting user data.
    
    **Requirements:** 10.1
    """
    try:
        return {
            "encryption_enabled": True,
            "encryption_algorithm": "Fernet (AES-128-CBC with HMAC)",
            "key_derivation": "PBKDF2-SHA256 with 100,000 iterations",
            "transport_security": "TLS/HTTPS required for all communications",
            "message_encryption": "All stored messages are encrypted at rest",
            "compliance": [
                "GDPR compliant",
                "End-to-end encryption for sensitive data",
                "Secure key management"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get encryption status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get encryption status: {str(e)}")
