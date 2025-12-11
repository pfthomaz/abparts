# backend/app/routers/sessions.py

import uuid
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from sqlalchemy.orm import Session

from .. import schemas, models
from ..database import get_db
from ..auth import get_current_user, has_role, has_roles, TokenData
from ..session_manager import session_manager

router = APIRouter()

# --- Session Management Endpoints ---

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Logout the current user by terminating their session.
    Requirements: 2D.5
    """
    # Extract token from authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        
        # Terminate the session
        session_manager.terminate_session(token, "logout", db)
        
        # Clear cookie if using cookie-based auth
        response.delete_cookie(key="session_token")
        
        return {"message": "Successfully logged out"}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid authorization header"
    )

@router.get("/me/sessions", response_model=List[schemas.UserSessionResponse])
async def get_my_sessions(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all active sessions for the current user.
    Requirements: 2D.7
    """
    # Get active sessions from Redis
    redis_sessions = session_manager.get_active_sessions(current_user.user_id)
    
    # Get sessions from database for additional details
    db_sessions = db.query(models.UserSession).filter(
        models.UserSession.user_id == current_user.user_id,
        models.UserSession.is_active == True
    ).all()
    
    # Create a mapping of session tokens to database records
    db_sessions_map = {s.session_token: s for s in db_sessions}
    
    # Combine Redis and database session data
    sessions = []
    for redis_session in redis_sessions:
        session_token = redis_session.get("session_token")
        db_session = db_sessions_map.get(session_token)
        
        if db_session:
            sessions.append({
                "id": db_session.id,
                "session_token": session_token,
                "ip_address": redis_session.get("ip_address") or db_session.ip_address,
                "user_agent": redis_session.get("user_agent") or db_session.user_agent,
                "created_at": db_session.created_at,
                "last_activity": datetime.fromisoformat(redis_session.get("last_activity")) if redis_session.get("last_activity") else db_session.last_activity,
                "expires_at": datetime.fromisoformat(redis_session.get("expires_at")) if redis_session.get("expires_at") else db_session.expires_at,
                "is_current": session_token == request.headers.get("Authorization", "").replace("Bearer ", "")
            })
    
    return sessions

@router.delete("/me/sessions/{session_token}")
async def terminate_my_session(
    session_token: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Terminate a specific session for the current user.
    Requirements: 2D.5
    """
    # Verify the session belongs to the current user
    session_data = session_manager.get_session(session_token)
    if not session_data or session_data.get("user_id") != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or does not belong to you"
        )
    
    # Check if trying to terminate current session
    current_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if session_token == current_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot terminate your current session. Use the logout endpoint instead."
        )
    
    # Terminate the session
    session_manager.terminate_session(session_token, "user_terminated", db)
    
    return {"message": "Session terminated successfully"}

@router.delete("/me/sessions")
async def terminate_all_my_sessions(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Terminate all sessions for the current user except the current one.
    Requirements: 2D.5
    """
    # Get current session token
    current_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # Terminate all sessions except current one
    terminated_count = session_manager.terminate_sessions_on_password_change(
        current_user.user_id, 
        current_token, 
        db
    )
    
    return {"message": f"Successfully terminated {terminated_count} sessions"}

# --- Admin Session Management Endpoints ---

@router.get("/admin/users/{user_id}/sessions", response_model=List[schemas.UserSessionResponse])
async def get_user_sessions(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Get all active sessions for a specific user (admin only).
    Requirements: 2D.7
    """
    # Check permissions - admins can only view sessions for users in their organization
    if current_user.role == "admin":
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user or user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view sessions for users in your organization"
            )
    
    # Get active sessions from database
    db_sessions = db.query(models.UserSession).filter(
        models.UserSession.user_id == user_id,
        models.UserSession.is_active == True
    ).all()
    
    # Get active sessions from Redis for additional details
    redis_sessions = session_manager.get_active_sessions(user_id)
    redis_sessions_map = {s.get("session_token"): s for s in redis_sessions}
    
    # Combine database and Redis session data
    sessions = []
    for db_session in db_sessions:
        redis_session = redis_sessions_map.get(db_session.session_token)
        
        if redis_session:  # Session is still active in Redis
            sessions.append({
                "id": db_session.id,
                "session_token": db_session.session_token,
                "ip_address": db_session.ip_address,
                "user_agent": db_session.user_agent,
                "created_at": db_session.created_at,
                "last_activity": datetime.fromisoformat(redis_session.get("last_activity")) if redis_session.get("last_activity") else db_session.last_activity,
                "expires_at": db_session.expires_at,
                "is_current": False  # Admin is viewing someone else's sessions
            })
    
    return sessions

@router.delete("/admin/users/{user_id}/sessions")
async def terminate_user_sessions(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Terminate all sessions for a specific user (admin only).
    Requirements: 2D.6
    """
    # Check permissions - admins can only terminate sessions for users in their organization
    if current_user.role == "admin":
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user or user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only terminate sessions for users in your organization"
            )
    
    # Prevent terminating own sessions through this endpoint
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot terminate your own sessions through this endpoint. Use the user endpoints instead."
        )
    
    # Terminate all sessions for the user
    terminated_count = session_manager.terminate_all_user_sessions(user_id, "admin_terminated", db)
    
    # Log the action
    admin_user = db.query(models.User).filter(models.User.id == current_user.user_id).first()
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if admin_user and target_user:
        security_event = models.SecurityEvent(
            user_id=user_id,
            event_type="admin_session_termination",
            details=f"All sessions terminated by admin {admin_user.username} (ID: {admin_user.id})",
            risk_level="medium"
        )
        db.add(security_event)
        db.commit()
    
    return {"message": f"Successfully terminated {terminated_count} sessions for user {user_id}"}

# --- Security Events Endpoints ---

@router.get("/me/security-events", response_model=List[schemas.SecurityEventResponse])
async def get_my_security_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get security events for the current user.
    Requirements: 2D.7
    """
    query = db.query(models.SecurityEvent).filter(models.SecurityEvent.user_id == current_user.user_id)
    
    # Apply filters
    if event_type:
        query = query.filter(models.SecurityEvent.event_type == event_type)
    
    if risk_level:
        query = query.filter(models.SecurityEvent.risk_level == risk_level)
    
    if start_date:
        query = query.filter(models.SecurityEvent.timestamp >= start_date)
    
    if end_date:
        query = query.filter(models.SecurityEvent.timestamp <= end_date)
    
    # Order by timestamp descending (newest first)
    query = query.order_by(models.SecurityEvent.timestamp.desc())
    
    # Apply pagination
    events = query.offset(skip).limit(limit).all()
    
    return events

@router.get("/admin/security-events", response_model=List[schemas.SecurityEventResponse])
async def get_security_events(
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("super_admin"))  # Only super admins can view all security events
):
    """
    Get security events with advanced filtering (super admin only).
    Requirements: 2D.7
    """
    query = db.query(models.SecurityEvent)
    
    # Apply filters
    if user_id:
        query = query.filter(models.SecurityEvent.user_id == user_id)
    
    if organization_id:
        # Join with User to filter by organization
        query = query.join(models.User, models.SecurityEvent.user_id == models.User.id)
        query = query.filter(models.User.organization_id == organization_id)
    
    if event_type:
        query = query.filter(models.SecurityEvent.event_type == event_type)
    
    if risk_level:
        query = query.filter(models.SecurityEvent.risk_level == risk_level)
    
    if ip_address:
        query = query.filter(models.SecurityEvent.ip_address == ip_address)
    
    if start_date:
        query = query.filter(models.SecurityEvent.timestamp >= start_date)
    
    if end_date:
        query = query.filter(models.SecurityEvent.timestamp <= end_date)
    
    # Order by timestamp descending (newest first)
    query = query.order_by(models.SecurityEvent.timestamp.desc())
    
    # Apply pagination
    events = query.offset(skip).limit(limit).all()
    
    return events

@router.get("/admin/security-dashboard")
async def get_security_dashboard(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in statistics"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """
    Get security dashboard statistics.
    Requirements: 2D.7
    """
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Base query with date filter
    base_query = db.query(models.SecurityEvent).filter(
        models.SecurityEvent.timestamp >= start_date,
        models.SecurityEvent.timestamp <= end_date
    )
    
    # For admin users, limit to their organization
    if current_user.role == "admin":
        base_query = base_query.join(models.User, models.SecurityEvent.user_id == models.User.id)
        base_query = base_query.filter(models.User.organization_id == current_user.organization_id)
    
    # Total events
    total_events = base_query.count()
    
    # Events by risk level
    risk_levels = ["low", "medium", "high", "critical"]
    events_by_risk = {}
    for risk in risk_levels:
        count = base_query.filter(models.SecurityEvent.risk_level == risk).count()
        events_by_risk[risk] = count
    
    # Events by type
    events_by_type = {}
    event_types = db.query(models.SecurityEvent.event_type).distinct().all()
    for (event_type,) in event_types:
        count = base_query.filter(models.SecurityEvent.event_type == event_type).count()
        events_by_type[event_type] = count
    
    # Failed login attempts
    failed_logins = base_query.filter(models.SecurityEvent.event_type == "login_failed").count()
    
    # Account lockouts
    account_lockouts = base_query.filter(models.SecurityEvent.event_type == "account_locked").count()
    
    # Suspicious activity
    suspicious_activity = base_query.filter(models.SecurityEvent.event_type == "suspicious_activity").count()
    
    # Active sessions
    active_sessions_query = db.query(models.UserSession).filter(models.UserSession.is_active == True)
    if current_user.role == "admin":
        active_sessions_query = active_sessions_query.join(models.User, models.UserSession.user_id == models.User.id)
        active_sessions_query = active_sessions_query.filter(models.User.organization_id == current_user.organization_id)
    
    active_sessions = active_sessions_query.count()
    
    return {
        "total_events": total_events,
        "events_by_risk": events_by_risk,
        "events_by_type": events_by_type,
        "failed_logins": failed_logins,
        "account_lockouts": account_lockouts,
        "suspicious_activity": suspicious_activity,
        "active_sessions": active_sessions,
        "date_range": {
            "start_date": start_date,
            "end_date": end_date,
            "days": days
        }
    }

# --- Additional Verification Endpoints ---

@router.post("/verify")
async def verify_session(
    verification: schemas.AdditionalVerification,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Complete additional verification when required due to suspicious activity.
    Requirements: 2D.3
    """
    # Check if additional verification is required
    if not session_manager.is_additional_verification_required(current_user.user_id):
        return {"message": "No additional verification required"}
    
    # Verify the provided code using the enhanced verification system
    if verification.verification_type == "email_code":
        is_valid = session_manager.verify_verification_code(
            current_user.user_id, 
            verification.verification_code, 
            "email", 
            db
        )
        
        if is_valid:
            session_manager.clear_additional_verification(current_user.user_id)
            return {"message": "Verification completed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code"
            )
    
    # If we get here, verification method not supported
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported verification method"
    )

@router.get("/verification-status")
async def get_verification_status(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Check if additional verification is required for the current user.
    Requirements: 2D.3
    """
    verification_required = session_manager.is_additional_verification_required(current_user.user_id)
    
    return {
        "verification_required": verification_required,
        "verification_methods": ["email_code"] if verification_required else []
    }

@router.post("/send-verification-code")
async def send_verification_code(
    method: str = "email",
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Send a verification code to the user for additional verification.
    Enhancement: Improved additional verification
    """
    try:
        verification_code = session_manager.send_verification_code(current_user.user_id, method, db)
        
        return {
            "message": f"Verification code sent via {method}",
            "method": method,
            "expires_in_minutes": 10
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification code: {str(e)}"
        )

@router.post("/regenerate-token")
async def regenerate_session_token(
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Regenerate session token for security (e.g., after privilege escalation).
    Enhancement: Session fixation protection
    """
    # Extract current token from authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization header"
        )
    
    current_token = auth_header.replace("Bearer ", "")
    
    try:
        new_token = session_manager.regenerate_session_token(current_token, db)
        
        if not new_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to regenerate session token"
            )
        
        return {
            "access_token": new_token,
            "token_type": "bearer",
            "message": "Session token regenerated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate token: {str(e)}"
        )

@router.get("/rate-limit-status")
async def get_rate_limit_status(
    request: Request,
    action: str = "login"
):
    """
    Get current rate limit status for the requesting IP.
    Enhancement: Rate limiting monitoring
    """
    ip_address = request.client.host if request.client else None
    
    if not ip_address:
        return {"message": "Unable to determine IP address"}
    
    status_info = session_manager.get_rate_limit_status(ip_address, action)
    
    return {
        "ip_address": ip_address,
        "action": action,
        **status_info
    }

# --- Session Cleanup Background Task ---

@router.post("/admin/cleanup-sessions")
async def cleanup_expired_sessions(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("super_admin"))
):
    """
    Manually trigger cleanup of expired sessions (super admin only).
    Requirements: 2D.2
    """
    expired_count = session_manager.cleanup_expired_sessions(db)
    
    return {"message": f"Cleaned up {expired_count} expired sessions"}