# backend/app/session_manager.py

import os
import uuid
import json
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from fastapi import Request
import redis
from sqlalchemy.orm import Session

from . import models
from .database import get_db

logger = logging.getLogger(__name__)

# Session configuration
SESSION_EXPIRY_HOURS = 8
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
SUSPICIOUS_ACTIVITY_THRESHOLD = 10  # Failed attempts from same IP

# Rate limiting configuration
RATE_LIMIT_LOGIN_ATTEMPTS = 10  # Per minute per IP
RATE_LIMIT_WINDOW_MINUTES = 1
RATE_LIMIT_API_REQUESTS = 100  # Per minute per user

class SessionManager:
    """
    Redis-based session management with security features.
    Requirements: 2D.1, 2D.2, 2D.3, 2D.4, 2D.5, 2D.6, 2D.7
    """
    
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            raise ValueError("REDIS_URL environment variable is not set")
        
        self.redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=True)
        self.session_prefix = "session:"
        self.failed_attempts_prefix = "failed_attempts:"
        self.ip_attempts_prefix = "ip_attempts:"
        self.rate_limit_prefix = "rate_limit:"
        self.verification_code_prefix = "verification_code:"
    
    def create_session(self, user: models.User, ip_address: str = None, user_agent: str = None, db: Session = None) -> str:
        """
        Create a new user session with 8-hour expiration.
        Requirements: 2D.1
        """
        session_token = secrets.token_urlsafe(32)
        session_id = f"{self.session_prefix}{session_token}"
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS)
        
        # Session data
        session_data = {
            "user_id": str(user.id),
            "username": user.username,
            "organization_id": str(user.organization_id),
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "is_active": True
        }
        
        # Store in Redis with expiration
        self.redis_client.setex(
            session_id, 
            timedelta(hours=SESSION_EXPIRY_HOURS), 
            json.dumps(session_data)
        )
        
        # Store in database for audit trail
        # Temporarily disabled due to missing user_sessions table
        # TODO: Add user_sessions table and re-enable database storage
        if db:
            # db_session = models.UserSession(
            #     user_id=user.id,
            #     session_token=session_token,
            #     ip_address=ip_address,
            #     user_agent=user_agent,
            #     expires_at=expires_at,
            #     is_active=True
            # )
            # db.add(db_session)
            
            # Update user's last login
            user.last_login = datetime.utcnow()
            db.commit()
        
        logger.info(f"Session created for user {user.username} (ID: {user.id})")
        return session_token
    
    def get_session(self, session_token: str) -> Optional[Dict]:
        """
        Retrieve session data and update last activity.
        Requirements: 2D.1, 2D.2
        """
        session_id = f"{self.session_prefix}{session_token}"
        session_data_str = self.redis_client.get(session_id)
        
        if not session_data_str:
            return None
        
        try:
            session_data = json.loads(session_data_str)
            
            # Check if session is expired
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            if datetime.utcnow() > expires_at:
                self.terminate_session(session_token, "timeout")
                return None
            
            # Update last activity
            session_data["last_activity"] = datetime.utcnow().isoformat()
            self.redis_client.setex(
                session_id,
                timedelta(hours=SESSION_EXPIRY_HOURS),
                json.dumps(session_data)
            )
            
            return session_data
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Invalid session data for token {session_token}: {e}")
            self.terminate_session(session_token, "invalid_data")
            return None
    
    def terminate_session(self, session_token: str, reason: str = "logout", db: Session = None):
        """
        Terminate a specific session.
        Requirements: 2D.5, 2D.6
        """
        session_id = f"{self.session_prefix}{session_token}"
        
        # Get session data before deletion for logging
        session_data_str = self.redis_client.get(session_id)
        if session_data_str:
            try:
                session_data = json.loads(session_data_str)
                user_id = session_data.get("user_id")
                
                # Log security event
                if db and user_id:
                    security_event = models.SecurityEvent(
                        user_id=uuid.UUID(user_id),
                        event_type="session_terminated",
                        session_id=session_token,
                        details=f"Session terminated: {reason}",
                        risk_level="low" if reason == "logout" else "medium"
                    )
                    db.add(security_event)
                    
                    # Update database session record
                    # Temporarily disabled due to missing user_sessions table
                    # db_session = db.query(models.UserSession).filter(
                    #     models.UserSession.session_token == session_token
                    # ).first()
                    # if db_session:
                    #     db_session.is_active = False
                    #     db_session.terminated_reason = reason
                    # 
                    # db.commit()
                
                logger.info(f"Session terminated for user {session_data.get('username')} - Reason: {reason}")
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error processing session termination: {e}")
        
        # Remove from Redis
        self.redis_client.delete(session_id)
    
    def terminate_all_user_sessions(self, user_id: uuid.UUID, reason: str = "admin_terminated", db: Session = None):
        """
        Terminate all sessions for a specific user.
        Requirements: 2D.6
        """
        # Find all sessions for the user in Redis
        pattern = f"{self.session_prefix}*"
        session_keys = self.redis_client.keys(pattern)
        
        terminated_count = 0
        for session_key in session_keys:
            session_data_str = self.redis_client.get(session_key)
            if session_data_str:
                try:
                    session_data = json.loads(session_data_str)
                    if session_data.get("user_id") == str(user_id):
                        session_token = session_key.replace(self.session_prefix, "")
                        self.terminate_session(session_token, reason, db)
                        terminated_count += 1
                except (json.JSONDecodeError, ValueError):
                    continue
        
        logger.info(f"Terminated {terminated_count} sessions for user {user_id} - Reason: {reason}")
        return terminated_count
    
    def terminate_sessions_on_password_change(self, user_id: uuid.UUID, current_session_token: str = None, db: Session = None):
        """
        Terminate all sessions for a user except the current one when password is changed.
        Requirements: 2D.5
        """
        # Find all sessions for the user in Redis
        pattern = f"{self.session_prefix}*"
        session_keys = self.redis_client.keys(pattern)
        
        terminated_count = 0
        for session_key in session_keys:
            session_data_str = self.redis_client.get(session_key)
            if session_data_str:
                try:
                    session_data = json.loads(session_data_str)
                    if session_data.get("user_id") == str(user_id):
                        session_token = session_key.replace(self.session_prefix, "")
                        # Don't terminate the current session (the one used to change password)
                        if session_token != current_session_token:
                            self.terminate_session(session_token, "password_changed", db)
                            terminated_count += 1
                except (json.JSONDecodeError, ValueError):
                    continue
        
        logger.info(f"Terminated {terminated_count} sessions for user {user_id} due to password change")
        return terminated_count
    
    def detect_suspicious_activity(self, ip_address: str, user_agent: str = None, db: Session = None) -> bool:
        """
        Detect suspicious login activity and require additional verification.
        Requirements: 2D.3
        """
        if not ip_address:
            return False
        
        # Check for multiple failed attempts from same IP
        ip_key = f"{self.ip_attempts_prefix}{ip_address}"
        ip_attempts = self.redis_client.get(ip_key)
        
        if ip_attempts and int(ip_attempts) >= SUSPICIOUS_ACTIVITY_THRESHOLD:
            # Log suspicious activity
            if db:
                security_event = models.SecurityEvent(
                    event_type="suspicious_activity",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details=f"Suspicious activity detected from IP: {ip_address}",
                    risk_level="high"
                )
                db.add(security_event)
                db.commit()
            
            logger.warning(f"Suspicious activity detected from IP: {ip_address}")
            return True
        
        return False
    
    def require_additional_verification(self, user_id: uuid.UUID, ip_address: str = None, db: Session = None):
        """
        Flag user for additional verification due to suspicious activity.
        Requirements: 2D.3
        """
        verification_key = f"additional_verification:{user_id}"
        verification_data = {
            "user_id": str(user_id),
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat(),
            "verified": False
        }
        
        # Store verification requirement for 1 hour
        self.redis_client.setex(
            verification_key,
            timedelta(hours=1),
            json.dumps(verification_data)
        )
        
        # Log security event
        if db:
            security_event = models.SecurityEvent(
                user_id=user_id,
                event_type="additional_verification_required",
                ip_address=ip_address,
                details="Additional verification required due to suspicious activity",
                risk_level="medium"
            )
            db.add(security_event)
            db.commit()
        
        logger.info(f"Additional verification required for user {user_id}")
    
    def is_additional_verification_required(self, user_id: uuid.UUID) -> bool:
        """
        Check if user requires additional verification.
        Requirements: 2D.3
        """
        verification_key = f"additional_verification:{user_id}"
        verification_data_str = self.redis_client.get(verification_key)
        
        if verification_data_str:
            try:
                verification_data = json.loads(verification_data_str)
                return not verification_data.get("verified", False)
            except (json.JSONDecodeError, ValueError):
                return False
        
        return False
    
    def clear_additional_verification(self, user_id: uuid.UUID):
        """
        Clear additional verification requirement after successful verification.
        Requirements: 2D.3
        """
        verification_key = f"additional_verification:{user_id}"
        self.redis_client.delete(verification_key)
        logger.info(f"Additional verification cleared for user {user_id}")
    
    def cleanup_expired_sessions(self, db: Session = None):
        """
        Clean up expired sessions from Redis and database.
        Requirements: 2D.2
        """
        pattern = f"{self.session_prefix}*"
        session_keys = self.redis_client.keys(pattern)
        
        expired_count = 0
        for session_key in session_keys:
            session_data_str = self.redis_client.get(session_key)
            if session_data_str:
                try:
                    session_data = json.loads(session_data_str)
                    expires_at = datetime.fromisoformat(session_data["expires_at"])
                    
                    if datetime.utcnow() > expires_at:
                        session_token = session_key.replace(self.session_prefix, "")
                        self.terminate_session(session_token, "timeout", db)
                        expired_count += 1
                        
                except (json.JSONDecodeError, ValueError, KeyError):
                    # Remove invalid session data
                    self.redis_client.delete(session_key)
                    expired_count += 1
        
        logger.info(f"Cleaned up {expired_count} expired sessions")
        return expired_count
    
    def record_failed_login(self, username: str, ip_address: str = None, db: Session = None) -> bool:
        """
        Record failed login attempt and check for account lockout.
        Requirements: 2D.4
        """
        # Increment failed attempts for user
        failed_key = f"{self.failed_attempts_prefix}{username}"
        failed_count = self.redis_client.incr(failed_key)
        self.redis_client.expire(failed_key, timedelta(minutes=LOCKOUT_DURATION_MINUTES))
        
        # Track IP-based attempts for suspicious activity detection
        if ip_address:
            ip_key = f"{self.ip_attempts_prefix}{ip_address}"
            ip_count = self.redis_client.incr(ip_key)
            self.redis_client.expire(ip_key, timedelta(hours=1))
            
            # Check for suspicious activity
            if ip_count >= SUSPICIOUS_ACTIVITY_THRESHOLD:
                if db:
                    security_event = models.SecurityEvent(
                        event_type="suspicious_activity",
                        ip_address=ip_address,
                        details=f"Multiple failed login attempts from IP: {ip_address}",
                        risk_level="high"
                    )
                    db.add(security_event)
        
        # Check if account should be locked
        should_lock = failed_count >= MAX_FAILED_ATTEMPTS
        
        if should_lock and db:
            # Lock the user account
            user = db.query(models.User).filter(models.User.username == username).first()
            if user:
                user.failed_login_attempts = failed_count
                user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                user.user_status = models.UserStatus.locked
                
                # Log security event
                security_event = models.SecurityEvent(
                    user_id=user.id,
                    event_type="account_locked",
                    ip_address=ip_address,
                    details=f"Account locked after {failed_count} failed attempts",
                    risk_level="medium"
                )
                db.add(security_event)
                db.commit()
                
                logger.warning(f"Account locked for user {username} after {failed_count} failed attempts")
        
        return should_lock
    
    def clear_failed_login_attempts(self, username: str, db: Session = None):
        """
        Clear failed login attempts after successful login.
        Requirements: 2D.4
        """
        failed_key = f"{self.failed_attempts_prefix}{username}"
        self.redis_client.delete(failed_key)
        
        if db:
            user = db.query(models.User).filter(models.User.username == username).first()
            if user and user.failed_login_attempts > 0:
                user.failed_login_attempts = 0
                user.locked_until = None
                if user.user_status == models.UserStatus.locked:
                    user.user_status = models.UserStatus.active
                db.commit()
    
    def is_user_locked(self, username: str, db: Session = None) -> bool:
        """
        Check if user account is currently locked.
        Requirements: 2D.4
        """
        if db:
            user = db.query(models.User).filter(models.User.username == username).first()
            if user:
                # Check database lock status
                if user.user_status == models.UserStatus.locked:
                    # Check if lock has expired
                    if user.locked_until and datetime.utcnow() > user.locked_until:
                        # Unlock the account
                        user.user_status = models.UserStatus.active
                        user.locked_until = None
                        user.failed_login_attempts = 0
                        db.commit()
                        return False
                    return True
        
        return False
    
    def get_active_sessions(self, user_id: uuid.UUID) -> List[Dict]:
        """
        Get all active sessions for a user.
        Requirements: 2D.7
        """
        pattern = f"{self.session_prefix}*"
        session_keys = self.redis_client.keys(pattern)
        
        user_sessions = []
        for session_key in session_keys:
            session_data_str = self.redis_client.get(session_key)
            if session_data_str:
                try:
                    session_data = json.loads(session_data_str)
                    if session_data.get("user_id") == str(user_id):
                        session_data["session_token"] = session_key.replace(self.session_prefix, "")
                        user_sessions.append(session_data)
                except (json.JSONDecodeError, ValueError):
                    continue
        
        return user_sessions
    
    def log_security_event(self, event_type: str, user_id: uuid.UUID = None, ip_address: str = None, 
                          user_agent: str = None, session_id: str = None, details: str = None, 
                          risk_level: str = "low", db: Session = None):
        """
        Log security events for monitoring and audit purposes.
        Requirements: 2D.7
        """
        # Temporarily disabled database logging due to missing security_events table
        # TODO: Add security_events table and re-enable database logging
        logger.info(f"Security event: {event_type} - User: {user_id} - IP: {ip_address} - Risk: {risk_level} - Details: {details}")
        
        # if db:
        #     security_event = models.SecurityEvent(
        #         user_id=user_id,
        #         event_type=event_type,
        #         ip_address=ip_address,
        #         user_agent=user_agent,
        #         session_id=session_id,
        #         details=details,
        #         risk_level=risk_level
        #     )
        #     db.add(security_event)
        #     db.commit()
        #     
        #     logger.info(f"Security event logged: {event_type} - Risk: {risk_level}")
    
    def check_rate_limit(self, ip_address: str, action: str, limit: int = None, window_minutes: int = None) -> bool:
        """
        Check if IP has exceeded rate limit for specific action.
        Enhancement: Rate limiting protection
        """
        if not ip_address:
            return True  # Allow if no IP address
        
        # Use default limits if not specified
        if limit is None:
            limit = RATE_LIMIT_LOGIN_ATTEMPTS if action == "login" else RATE_LIMIT_API_REQUESTS
        if window_minutes is None:
            window_minutes = RATE_LIMIT_WINDOW_MINUTES
        
        rate_key = f"{self.rate_limit_prefix}{action}:{ip_address}"
        current_count = self.redis_client.incr(rate_key)
        
        if current_count == 1:
            # Set expiration on first increment
            self.redis_client.expire(rate_key, window_minutes * 60)
        
        is_within_limit = current_count <= limit
        
        if not is_within_limit:
            logger.warning(f"Rate limit exceeded for {action} from IP {ip_address}: {current_count}/{limit}")
        
        return is_within_limit
    
    def send_verification_code(self, user_id: uuid.UUID, method: str = "email", db: Session = None) -> str:
        """
        Generate and store verification code for additional verification.
        Enhancement: Improved additional verification
        """
        # Generate 6-digit verification code
        code = str(secrets.randbelow(900000) + 100000)
        
        # Store verification code in Redis with 10-minute expiration
        verification_key = f"{self.verification_code_prefix}{user_id}:{method}"
        verification_data = {
            "code": code,
            "method": method,
            "user_id": str(user_id),
            "created_at": datetime.utcnow().isoformat(),
            "attempts": 0
        }
        
        self.redis_client.setex(
            verification_key,
            timedelta(minutes=10),
            json.dumps(verification_data)
        )
        
        # Log security event
        if db:
            self.log_security_event(
                event_type="verification_code_sent",
                user_id=user_id,
                details=f"Verification code sent via {method}",
                risk_level="low",
                db=db
            )
        
        logger.info(f"Verification code generated for user {user_id} via {method}")
        
        # In a real implementation, you would send the code via email/SMS here
        # For testing purposes, we'll log it (remove in production)
        logger.info(f"DEBUG: Verification code for user {user_id}: {code}")
        
        return code
    
    def verify_verification_code(self, user_id: uuid.UUID, provided_code: str, method: str = "email", db: Session = None) -> bool:
        """
        Verify the provided verification code.
        Enhancement: Improved additional verification
        """
        verification_key = f"{self.verification_code_prefix}{user_id}:{method}"
        verification_data_str = self.redis_client.get(verification_key)
        
        if not verification_data_str:
            logger.warning(f"No verification code found for user {user_id}")
            return False
        
        try:
            verification_data = json.loads(verification_data_str)
            stored_code = verification_data.get("code")
            attempts = verification_data.get("attempts", 0)
            
            # Increment attempt counter
            verification_data["attempts"] = attempts + 1
            
            # Check if too many attempts (max 3)
            if attempts >= 3:
                self.redis_client.delete(verification_key)
                if db:
                    self.log_security_event(
                        event_type="verification_code_max_attempts",
                        user_id=user_id,
                        details="Maximum verification attempts exceeded",
                        risk_level="medium",
                        db=db
                    )
                logger.warning(f"Maximum verification attempts exceeded for user {user_id}")
                return False
            
            # Update attempts in Redis
            self.redis_client.setex(
                verification_key,
                timedelta(minutes=10),
                json.dumps(verification_data)
            )
            
            # Verify the code
            if provided_code == stored_code:
                # Clear the verification code on successful verification
                self.redis_client.delete(verification_key)
                if db:
                    self.log_security_event(
                        event_type="verification_code_verified",
                        user_id=user_id,
                        details=f"Verification code verified via {method}",
                        risk_level="low",
                        db=db
                    )
                logger.info(f"Verification code verified for user {user_id}")
                return True
            else:
                if db:
                    self.log_security_event(
                        event_type="verification_code_failed",
                        user_id=user_id,
                        details=f"Invalid verification code provided via {method}",
                        risk_level="low",
                        db=db
                    )
                logger.warning(f"Invalid verification code for user {user_id}")
                return False
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error verifying verification code: {e}")
            return False
    
    def regenerate_session_token(self, old_token: str, db: Session = None) -> Optional[str]:
        """
        Regenerate session token for security (e.g., after privilege escalation).
        Enhancement: Session fixation protection
        """
        # Get existing session data
        session_data = self.get_session(old_token)
        if not session_data:
            logger.warning(f"Cannot regenerate token - session not found: {old_token}")
            return None
        
        try:
            # Get user from database
            user_id = uuid.UUID(session_data["user_id"])
            user = db.query(models.User).filter(models.User.id == user_id).first() if db else None
            
            if not user:
                logger.warning(f"Cannot regenerate token - user not found: {user_id}")
                return None
            
            # Terminate old session
            self.terminate_session(old_token, "regenerated", db)
            
            # Create new session with same user data
            new_token = self.create_session(
                user=user,
                ip_address=session_data.get("ip_address"),
                user_agent=session_data.get("user_agent"),
                db=db
            )
            
            # Log security event
            if db:
                self.log_security_event(
                    event_type="session_token_regenerated",
                    user_id=user_id,
                    session_id=new_token,
                    details="Session token regenerated for security",
                    risk_level="low",
                    db=db
                )
            
            logger.info(f"Session token regenerated for user {user.username}")
            return new_token
            
        except (ValueError, KeyError) as e:
            logger.error(f"Error regenerating session token: {e}")
            return None
    
    def create_session_from_data(self, session_data: Dict, db: Session = None) -> Optional[str]:
        """
        Create a new session from existing session data.
        Helper method for session regeneration.
        """
        try:
            user_id = uuid.UUID(session_data["user_id"])
            user = db.query(models.User).filter(models.User.id == user_id).first() if db else None
            
            if not user:
                return None
            
            return self.create_session(
                user=user,
                ip_address=session_data.get("ip_address"),
                user_agent=session_data.get("user_agent"),
                db=db
            )
        except (ValueError, KeyError):
            return None
    
    def get_rate_limit_status(self, ip_address: str, action: str) -> Dict:
        """
        Get current rate limit status for an IP and action.
        Enhancement: Rate limiting monitoring
        """
        if not ip_address:
            return {"current_count": 0, "limit": 0, "remaining": 0, "reset_time": None}
        
        limit = RATE_LIMIT_LOGIN_ATTEMPTS if action == "login" else RATE_LIMIT_API_REQUESTS
        rate_key = f"{self.rate_limit_prefix}{action}:{ip_address}"
        
        current_count = self.redis_client.get(rate_key)
        current_count = int(current_count) if current_count else 0
        
        remaining = max(0, limit - current_count)
        ttl = self.redis_client.ttl(rate_key)
        reset_time = datetime.utcnow() + timedelta(seconds=ttl) if ttl > 0 else None
        
        return {
            "current_count": current_count,
            "limit": limit,
            "remaining": remaining,
            "reset_time": reset_time.isoformat() if reset_time else None
        }


# Global session manager instance
session_manager = SessionManager()