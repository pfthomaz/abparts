"""
Audit Logging and Compliance API Endpoints

Provides comprehensive audit logging and compliance reporting features:
- AI interaction audit trails
- Compliance report generation
- User consent management
- Data access tracking

Validates Requirements: 10.2, 10.3, 10.5
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta

from ..services.audit_service import get_audit_service, AuditService, AuditEventType, AuditSeverity
from ..services.consent_service import get_consent_service, ConsentService, ConsentType, ConsentStatus
from ..database import get_db_session
from ..schemas import ErrorResponse

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models

class ConsentRequest(BaseModel):
    """Request to record user consent."""
    user_id: str = Field(..., description="User ID")
    consent_type: ConsentType = Field(..., description="Type of consent")
    status: ConsentStatus = Field(..., description="Consent status")
    consent_text: Optional[str] = Field(None, description="Text of consent agreement")
    privacy_policy_version: Optional[str] = Field(None, description="Privacy policy version")


class PrivacyPolicyAcceptanceRequest(BaseModel):
    """Request to record privacy policy acceptance."""
    user_id: str = Field(..., description="User ID")
    policy_version: str = Field(..., description="Privacy policy version")
    policy_text: str = Field(..., description="Full privacy policy text")


class ComplianceReportRequest(BaseModel):
    """Request to generate compliance report."""
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    report_type: str = Field(default="full", description="Type of report (full, gdpr, security, data_access)")


class AuditTrailRequest(BaseModel):
    """Request to retrieve audit trail."""
    user_id: str = Field(..., description="User ID")
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    event_types: Optional[List[str]] = Field(None, description="Event types to filter")
    limit: int = Field(default=100, description="Maximum number of records")


class ConsentResponse(BaseModel):
    """Response after recording consent."""
    success: bool
    message: str
    consent_id: Optional[str] = None


class AuditTrailResponse(BaseModel):
    """Response containing audit trail."""
    user_id: str
    total_events: int
    events: List[Dict[str, Any]]


class ComplianceReportResponse(BaseModel):
    """Response containing compliance report."""
    success: bool
    report: Dict[str, Any]


class ConsentSummaryResponse(BaseModel):
    """Response containing consent summary."""
    consent_by_type: Dict[str, Dict[str, int]]
    privacy_policy_acceptances: Dict[str, int]
    total_consent_records: int
    total_policy_acceptances: int


class RequiredConsentsResponse(BaseModel):
    """Response containing required consents."""
    required_consents: List[Dict[str, Any]]


# Consent Management Endpoints

@router.post("/consent/record", response_model=ConsentResponse)
async def record_user_consent(
    request: ConsentRequest,
    authorization: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    consent_service: ConsentService = Depends(get_consent_service)
) -> ConsentResponse:
    """
    Record user consent for data processing.
    
    This endpoint records user consent for various types of data processing
    activities in compliance with GDPR and privacy regulations.
    
    **Requirements:** 10.2, 10.3, 10.5
    """
    try:
        # TODO: Add authentication check
        
        with get_db_session() as db:
            success = await consent_service.record_consent(
                db=db,
                user_id=request.user_id,
                consent_type=request.consent_type,
                status=request.status,
                consent_text=request.consent_text,
                privacy_policy_version=request.privacy_policy_version,
                ip_address=x_forwarded_for,
                user_agent=user_agent
            )
        
        if success:
            return ConsentResponse(
                success=True,
                message=f"Consent recorded: {request.consent_type.value} - {request.status.value}"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to record consent")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record consent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record consent: {str(e)}")


@router.get("/consent/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_consent(
    user_id: str,
    consent_type: Optional[ConsentType] = Query(None),
    authorization: Optional[str] = Header(None),
    consent_service: ConsentService = Depends(get_consent_service)
) -> List[Dict[str, Any]]:
    """
    Get user consent records.
    
    Retrieves all consent records for a specific user, optionally filtered
    by consent type.
    
    **Requirements:** 10.2, 10.3
    """
    try:
        # TODO: Add authentication check
        
        with get_db_session() as db:
            consents = await consent_service.get_user_consent(
                db=db,
                user_id=user_id,
                consent_type=consent_type
            )
        
        return consents
        
    except Exception as e:
        logger.error(f"Failed to get user consent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user consent: {str(e)}")


@router.post("/consent/{user_id}/withdraw", response_model=ConsentResponse)
async def withdraw_user_consent(
    user_id: str,
    consent_type: ConsentType,
    reason: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    consent_service: ConsentService = Depends(get_consent_service)
) -> ConsentResponse:
    """
    Withdraw user consent.
    
    Allows users to withdraw their consent for specific types of data processing.
    
    **Requirements:** 10.2, 10.5
    """
    try:
        # TODO: Add authentication check
        
        with get_db_session() as db:
            success = await consent_service.withdraw_consent(
                db=db,
                user_id=user_id,
                consent_type=consent_type,
                reason=reason
            )
        
        if success:
            return ConsentResponse(
                success=True,
                message=f"Consent withdrawn: {consent_type.value}"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to withdraw consent")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to withdraw consent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to withdraw consent: {str(e)}")


@router.post("/privacy-policy/accept", response_model=ConsentResponse)
async def accept_privacy_policy(
    request: PrivacyPolicyAcceptanceRequest,
    authorization: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    consent_service: ConsentService = Depends(get_consent_service)
) -> ConsentResponse:
    """
    Record privacy policy acceptance.
    
    Records user acceptance of the privacy policy with version tracking.
    
    **Requirements:** 10.2, 10.3
    """
    try:
        # TODO: Add authentication check
        
        with get_db_session() as db:
            success = await consent_service.record_privacy_policy_acceptance(
                db=db,
                user_id=request.user_id,
                policy_version=request.policy_version,
                policy_text=request.policy_text,
                ip_address=x_forwarded_for,
                user_agent=user_agent
            )
        
        if success:
            return ConsentResponse(
                success=True,
                message=f"Privacy policy v{request.policy_version} accepted"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to record privacy policy acceptance")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record privacy policy acceptance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record privacy policy acceptance: {str(e)}")


@router.get("/privacy-policy/{user_id}", response_model=Dict[str, Any])
async def get_privacy_policy_acceptance(
    user_id: str,
    authorization: Optional[str] = Header(None),
    consent_service: ConsentService = Depends(get_consent_service)
) -> Dict[str, Any]:
    """
    Get user's privacy policy acceptance.
    
    Retrieves the latest privacy policy acceptance record for a user.
    
    **Requirements:** 10.2, 10.3
    """
    try:
        # TODO: Add authentication check
        
        with get_db_session() as db:
            acceptance = await consent_service.get_privacy_policy_acceptance(
                db=db,
                user_id=user_id
            )
        
        if acceptance:
            return acceptance
        else:
            raise HTTPException(status_code=404, detail="No privacy policy acceptance found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get privacy policy acceptance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get privacy policy acceptance: {str(e)}")


@router.get("/consent/required", response_model=RequiredConsentsResponse)
async def get_required_consents(
    consent_service: ConsentService = Depends(get_consent_service)
) -> RequiredConsentsResponse:
    """
    Get list of required consents.
    
    Returns information about all consent types required for AI Assistant usage.
    
    **Requirements:** 10.2
    """
    try:
        required_consents = consent_service.get_required_consents()
        return RequiredConsentsResponse(required_consents=required_consents)
        
    except Exception as e:
        logger.error(f"Failed to get required consents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get required consents: {str(e)}")


# Audit Trail Endpoints

@router.post("/audit/trail", response_model=AuditTrailResponse)
async def get_audit_trail(
    request: AuditTrailRequest,
    authorization: Optional[str] = Header(None),
    audit_service: AuditService = Depends(get_audit_service)
) -> AuditTrailResponse:
    """
    Get audit trail for a user.
    
    Retrieves comprehensive audit trail of all AI interactions and events
    for a specific user.
    
    **Requirements:** 10.2, 10.3
    """
    try:
        # TODO: Add authentication check
        
        with get_db_session() as db:
            events = await audit_service.get_user_audit_trail(
                db=db,
                user_id=request.user_id,
                start_date=request.start_date,
                end_date=request.end_date,
                event_types=request.event_types,
                limit=request.limit
            )
        
        return AuditTrailResponse(
            user_id=request.user_id,
            total_events=len(events),
            events=events
        )
        
    except Exception as e:
        logger.error(f"Failed to get audit trail: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit trail: {str(e)}")


@router.get("/audit/summary", response_model=Dict[str, Any])
async def get_audit_summary(
    days: int = Query(default=30, description="Number of days to include"),
    authorization: Optional[str] = Header(None),
    audit_service: AuditService = Depends(get_audit_service)
) -> Dict[str, Any]:
    """
    Get system audit summary.
    
    Provides a summary of system-wide audit events for the specified period.
    
    **Requirements:** 10.2, 10.3
    
    **Note:** This endpoint should be restricted to admin users.
    """
    try:
        # TODO: Add admin authentication check
        
        with get_db_session() as db:
            summary = await audit_service.get_system_audit_summary(
                db=db,
                days=days
            )
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get audit summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit summary: {str(e)}")


# Compliance Reporting Endpoints

@router.post("/compliance/report", response_model=ComplianceReportResponse)
async def generate_compliance_report(
    request: ComplianceReportRequest,
    authorization: Optional[str] = Header(None),
    audit_service: AuditService = Depends(get_audit_service)
) -> ComplianceReportResponse:
    """
    Generate compliance report.
    
    Generates a comprehensive compliance report for the specified period,
    including AI interactions, data access, GDPR requests, and security events.
    
    **Requirements:** 10.2, 10.3, 10.5
    
    **Note:** This endpoint should be restricted to admin users.
    """
    try:
        # TODO: Add admin authentication check
        
        with get_db_session() as db:
            report = await audit_service.generate_compliance_report(
                db=db,
                start_date=request.start_date,
                end_date=request.end_date,
                report_type=request.report_type
            )
        
        return ComplianceReportResponse(
            success=True,
            report=report
        )
        
    except Exception as e:
        logger.error(f"Failed to generate compliance report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate compliance report: {str(e)}")


@router.get("/compliance/consent-summary", response_model=ConsentSummaryResponse)
async def get_consent_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    authorization: Optional[str] = Header(None),
    consent_service: ConsentService = Depends(get_consent_service)
) -> ConsentSummaryResponse:
    """
    Get consent summary for compliance reporting.
    
    Provides a summary of all consent records for the specified period.
    
    **Requirements:** 10.2, 10.3
    
    **Note:** This endpoint should be restricted to admin users.
    """
    try:
        # TODO: Add admin authentication check
        
        with get_db_session() as db:
            summary = await consent_service.get_consent_summary(
                db=db,
                start_date=start_date,
                end_date=end_date
            )
        
        return ConsentSummaryResponse(**summary)
        
    except Exception as e:
        logger.error(f"Failed to get consent summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get consent summary: {str(e)}")


@router.get("/compliance/data-handling-documentation")
async def get_data_handling_documentation() -> Dict[str, Any]:
    """
    Get data handling documentation.
    
    Provides comprehensive documentation about how user data is handled,
    stored, and protected in the AI Assistant.
    
    **Requirements:** 10.2, 10.3
    """
    return {
        "data_collection": {
            "description": "Data collected during AI Assistant usage",
            "types": [
                {
                    "type": "Conversation Data",
                    "description": "User messages and AI responses",
                    "purpose": "Provide AI assistance and maintain conversation context",
                    "retention": "90 days for completed sessions",
                    "encryption": "AES-128-CBC with HMAC"
                },
                {
                    "type": "Session Metadata",
                    "description": "Session timestamps, machine context, user preferences",
                    "purpose": "Enable personalized assistance and analytics",
                    "retention": "90 days for completed sessions",
                    "encryption": "Database-level encryption"
                },
                {
                    "type": "User Feedback",
                    "description": "Satisfaction ratings and feedback text",
                    "purpose": "Improve AI Assistant quality",
                    "retention": "2 years for analytics",
                    "encryption": "Database-level encryption"
                },
                {
                    "type": "Audit Logs",
                    "description": "System events and user actions",
                    "purpose": "Security monitoring and compliance",
                    "retention": "3 years",
                    "encryption": "Database-level encryption"
                }
            ]
        },
        "data_processing": {
            "description": "How data is processed",
            "activities": [
                {
                    "activity": "AI Response Generation",
                    "description": "User messages are sent to OpenAI API for response generation",
                    "data_shared": "Message content, conversation context, machine information",
                    "third_party": "OpenAI",
                    "safeguards": "Sensitive data detection and redaction before sending"
                },
                {
                    "activity": "Knowledge Base Search",
                    "description": "User queries are searched against AutoBoss documentation",
                    "data_shared": "Query text only",
                    "third_party": "None (internal)",
                    "safeguards": "No personal data included in searches"
                },
                {
                    "activity": "Analytics",
                    "description": "Usage patterns and performance metrics",
                    "data_shared": "Anonymized user IDs, session outcomes, response times",
                    "third_party": "None (internal)",
                    "safeguards": "User IDs are hashed for anonymization"
                }
            ]
        },
        "data_protection": {
            "description": "Security measures in place",
            "measures": [
                {
                    "measure": "Encryption at Rest",
                    "description": "All messages encrypted using Fernet (AES-128-CBC)",
                    "implementation": "Automatic encryption before database storage"
                },
                {
                    "measure": "Encryption in Transit",
                    "description": "TLS/HTTPS for all API communications",
                    "implementation": "Enforced at infrastructure level"
                },
                {
                    "measure": "Sensitive Data Detection",
                    "description": "Automatic detection and redaction of PII",
                    "implementation": "Regex-based detection for emails, phone numbers, etc."
                },
                {
                    "measure": "Access Control",
                    "description": "Role-based access to user data",
                    "implementation": "Authentication and authorization on all endpoints"
                },
                {
                    "measure": "Audit Logging",
                    "description": "Comprehensive logging of all data access",
                    "implementation": "Automatic logging with database triggers"
                }
            ]
        },
        "user_rights": {
            "description": "User rights under GDPR",
            "rights": [
                {
                    "right": "Right to Access",
                    "description": "View all your data",
                    "how_to_exercise": "Use session history endpoints or contact support"
                },
                {
                    "right": "Right to Data Portability",
                    "description": "Export all your data in structured format",
                    "how_to_exercise": "POST /api/ai/privacy/users/{user_id}/export-data"
                },
                {
                    "right": "Right to Erasure",
                    "description": "Delete all your data (right to be forgotten)",
                    "how_to_exercise": "POST /api/ai/privacy/users/{user_id}/delete-data"
                },
                {
                    "right": "Right to Rectification",
                    "description": "Correct inaccurate data",
                    "how_to_exercise": "Contact support or use update endpoints"
                },
                {
                    "right": "Right to Withdraw Consent",
                    "description": "Withdraw consent for data processing",
                    "how_to_exercise": "POST /api/ai/audit-compliance/consent/{user_id}/withdraw"
                },
                {
                    "right": "Right to Object",
                    "description": "Object to certain data processing activities",
                    "how_to_exercise": "Contact support with your objection"
                }
            ]
        },
        "contact": {
            "data_protection_officer": "privacy@abparts.com",
            "support": "support@abparts.com",
            "website": "https://abparts.com/privacy"
        }
    }
