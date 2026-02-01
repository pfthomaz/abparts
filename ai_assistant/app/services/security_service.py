"""
Security and Privacy Service for AI Assistant

This service implements:
- End-to-end encryption for AI communications
- Data retention policies and automatic cleanup
- User data deletion functionality (GDPR compliance)
- Sensitive data detection and filtering

Validates Requirements: 10.1, 10.3, 10.4, 10.5
"""

import re
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os

logger = logging.getLogger(__name__)


class SecurityService:
    """
    Handles security and privacy features for AI Assistant.
    
    Features:
    - Message encryption/decryption
    - Sensitive data detection and filtering
    - Data retention policy enforcement
    - GDPR-compliant data deletion
    """
    
    # Sensitive data patterns
    SENSITIVE_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'api_key': r'\b[A-Za-z0-9]{32,}\b',
        'password': r'(?i)(password|passwd|pwd)[\s:=]+[^\s]+',
    }
    
    # Data retention periods (in days)
    RETENTION_PERIODS = {
        'active_sessions': 30,      # Active conversation sessions
        'completed_sessions': 90,   # Completed troubleshooting sessions
        'escalated_sessions': 365,  # Escalated sessions (longer for support)
        'abandoned_sessions': 7,    # Abandoned sessions (quick cleanup)
        'analytics_data': 730,      # Analytics and learning data (2 years)
        'audit_logs': 1095,         # Audit logs (3 years for compliance)
    }
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize security service.
        
        Args:
            encryption_key: Base encryption key (from environment variable)
        """
        self.encryption_key = encryption_key or os.getenv('AI_ENCRYPTION_KEY')
        if not self.encryption_key:
            # Generate a new key if none provided (for development)
            self.encryption_key = Fernet.generate_key().decode()
            logger.warning("No encryption key provided, generated temporary key")
        
        # Initialize Fernet cipher
        self._cipher = self._initialize_cipher()
    
    def _initialize_cipher(self) -> Fernet:
        """Initialize Fernet cipher with the encryption key."""
        try:
            # Ensure key is properly formatted
            key_bytes = self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key
            
            # If key is not 32 bytes, derive it using PBKDF2
            if len(key_bytes) != 44:  # Fernet keys are 44 bytes when base64 encoded
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b'ai_assistant_salt',  # In production, use unique salt per deployment
                    iterations=100000,
                    backend=default_backend()
                )
                key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
            else:
                key = key_bytes
            
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize cipher: {e}")
            # Fallback to a generated key
            return Fernet(Fernet.generate_key())
    
    def encrypt_message(self, content: str) -> str:
        """
        Encrypt message content for storage.
        
        Args:
            content: Plain text message content
            
        Returns:
            Encrypted message content (base64 encoded)
        """
        try:
            encrypted = self._cipher.encrypt(content.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            # In case of encryption failure, return original (log warning)
            logger.warning("Storing message without encryption due to encryption failure")
            return content
    
    def decrypt_message(self, encrypted_content: str) -> str:
        """
        Decrypt message content for retrieval.
        
        Args:
            encrypted_content: Encrypted message content (base64 encoded)
            
        Returns:
            Decrypted plain text content
        """
        try:
            decrypted = self._cipher.decrypt(encrypted_content.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            # If decryption fails, assume content is not encrypted
            return encrypted_content
    
    def detect_sensitive_data(self, content: str) -> List[Dict[str, Any]]:
        """
        Detect sensitive data in message content.
        
        Args:
            content: Message content to analyze
            
        Returns:
            List of detected sensitive data patterns with types and positions
        """
        detections = []
        
        for data_type, pattern in self.SENSITIVE_PATTERNS.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                detections.append({
                    'type': data_type,
                    'value': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        return detections
    
    def filter_sensitive_data(self, content: str, redact: bool = True) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Filter sensitive data from message content.
        
        Args:
            content: Message content to filter
            redact: If True, replace sensitive data with [REDACTED]. If False, just detect.
            
        Returns:
            Tuple of (filtered_content, detections)
        """
        detections = self.detect_sensitive_data(content)
        
        if not redact or not detections:
            return content, detections
        
        # Sort detections by position (reverse order to maintain indices)
        detections.sort(key=lambda x: x['start'], reverse=True)
        
        filtered_content = content
        for detection in detections:
            # Replace sensitive data with redacted placeholder
            redacted = f"[REDACTED_{detection['type'].upper()}]"
            filtered_content = (
                filtered_content[:detection['start']] +
                redacted +
                filtered_content[detection['end']:]
            )
        
        return filtered_content, detections
    
    def hash_user_id(self, user_id: str) -> str:
        """
        Create a one-way hash of user ID for anonymized analytics.
        
        Args:
            user_id: User identifier
            
        Returns:
            Hashed user ID
        """
        return hashlib.sha256(user_id.encode()).hexdigest()
    
    async def delete_user_data(self, user_id: str, db_session) -> Dict[str, int]:
        """
        Delete all user data for GDPR compliance.
        
        Args:
            user_id: User identifier
            db_session: Database session
            
        Returns:
            Dictionary with counts of deleted records by type
        """
        from sqlalchemy import text
        
        deleted_counts = {}
        
        try:
            # Delete AI sessions and related data
            result = db_session.execute(
                text("DELETE FROM ai_messages WHERE session_id IN (SELECT id FROM ai_sessions WHERE user_id = :user_id)"),
                {'user_id': user_id}
            )
            deleted_counts['messages'] = result.rowcount
            
            result = db_session.execute(
                text("DELETE FROM troubleshooting_steps WHERE session_id IN (SELECT id FROM ai_sessions WHERE user_id = :user_id)"),
                {'user_id': user_id}
            )
            deleted_counts['troubleshooting_steps'] = result.rowcount
            
            result = db_session.execute(
                text("DELETE FROM escalation_triggers WHERE session_id IN (SELECT id FROM ai_sessions WHERE user_id = :user_id)"),
                {'user_id': user_id}
            )
            deleted_counts['escalation_triggers'] = result.rowcount
            
            result = db_session.execute(
                text("DELETE FROM ai_sessions WHERE user_id = :user_id"),
                {'user_id': user_id}
            )
            deleted_counts['sessions'] = result.rowcount
            
            # Delete expert knowledge contributions
            result = db_session.execute(
                text("DELETE FROM expert_knowledge WHERE expert_user_id = :user_id"),
                {'user_id': user_id}
            )
            deleted_counts['expert_knowledge'] = result.rowcount
            
            # Delete expert feedback
            result = db_session.execute(
                text("DELETE FROM expert_feedback WHERE expert_user_id = :user_id"),
                {'user_id': user_id}
            )
            deleted_counts['expert_feedback'] = result.rowcount
            
            # Anonymize support tickets (keep for support history but remove PII)
            result = db_session.execute(
                text("""
                    UPDATE support_tickets 
                    SET session_summary = '[USER DATA DELETED]',
                        machine_context = NULL,
                        expert_contact_info = NULL
                    WHERE session_id IN (
                        SELECT id FROM ai_sessions WHERE user_id = :user_id
                    )
                """),
                {'user_id': user_id}
            )
            deleted_counts['anonymized_tickets'] = result.rowcount
            
            db_session.commit()
            
            logger.info(f"Deleted user data for user {user_id}: {deleted_counts}")
            return deleted_counts
            
        except Exception as e:
            db_session.rollback()
            logger.error(f"Failed to delete user data for {user_id}: {e}")
            raise
    
    async def cleanup_expired_data(self, db_session) -> Dict[str, int]:
        """
        Clean up expired data based on retention policies.
        
        Args:
            db_session: Database session
            
        Returns:
            Dictionary with counts of deleted records by type
        """
        from sqlalchemy import text
        
        deleted_counts = {}
        current_time = datetime.utcnow()
        
        try:
            # Clean up abandoned sessions
            cutoff_date = current_time - timedelta(days=self.RETENTION_PERIODS['abandoned_sessions'])
            result = db_session.execute(
                text("""
                    DELETE FROM ai_messages 
                    WHERE session_id IN (
                        SELECT id FROM ai_sessions 
                        WHERE status = 'abandoned' 
                        AND updated_at < :cutoff_date
                    )
                """),
                {'cutoff_date': cutoff_date}
            )
            deleted_counts['abandoned_messages'] = result.rowcount
            
            result = db_session.execute(
                text("""
                    DELETE FROM ai_sessions 
                    WHERE status = 'abandoned' 
                    AND updated_at < :cutoff_date
                """),
                {'cutoff_date': cutoff_date}
            )
            deleted_counts['abandoned_sessions'] = result.rowcount
            
            # Clean up completed sessions
            cutoff_date = current_time - timedelta(days=self.RETENTION_PERIODS['completed_sessions'])
            result = db_session.execute(
                text("""
                    DELETE FROM ai_messages 
                    WHERE session_id IN (
                        SELECT id FROM ai_sessions 
                        WHERE status = 'completed' 
                        AND updated_at < :cutoff_date
                    )
                """),
                {'cutoff_date': cutoff_date}
            )
            deleted_counts['completed_messages'] = result.rowcount
            
            result = db_session.execute(
                text("""
                    DELETE FROM ai_sessions 
                    WHERE status = 'completed' 
                    AND updated_at < :cutoff_date
                """),
                {'cutoff_date': cutoff_date}
            )
            deleted_counts['completed_sessions'] = result.rowcount
            
            # Clean up old analytics data (keep aggregated metrics, remove detailed logs)
            cutoff_date = current_time - timedelta(days=self.RETENTION_PERIODS['analytics_data'])
            result = db_session.execute(
                text("""
                    DELETE FROM session_analytics 
                    WHERE created_at < :cutoff_date
                """),
                {'cutoff_date': cutoff_date}
            )
            deleted_counts['old_analytics'] = result.rowcount
            
            db_session.commit()
            
            logger.info(f"Cleaned up expired data: {deleted_counts}")
            return deleted_counts
            
        except Exception as e:
            db_session.rollback()
            logger.error(f"Failed to cleanup expired data: {e}")
            raise
    
    def get_retention_info(self) -> Dict[str, Any]:
        """
        Get information about data retention policies.
        
        Returns:
            Dictionary with retention periods and policy details
        """
        return {
            'retention_periods': self.RETENTION_PERIODS,
            'policy_description': {
                'active_sessions': 'Active conversations are retained for 30 days',
                'completed_sessions': 'Completed troubleshooting sessions are retained for 90 days',
                'escalated_sessions': 'Escalated sessions are retained for 1 year for support purposes',
                'abandoned_sessions': 'Abandoned sessions are deleted after 7 days',
                'analytics_data': 'Analytics data is retained for 2 years for learning purposes',
                'audit_logs': 'Audit logs are retained for 3 years for compliance',
            },
            'user_rights': {
                'access': 'Users can request access to all their data',
                'deletion': 'Users can request deletion of all their data (GDPR right to be forgotten)',
                'portability': 'Users can export their conversation history',
                'rectification': 'Users can request corrections to their data',
            }
        }
    
    async def export_user_data(self, user_id: str, db_session) -> Dict[str, Any]:
        """
        Export all user data for GDPR data portability.
        
        Args:
            user_id: User identifier
            db_session: Database session
            
        Returns:
            Dictionary containing all user data
        """
        from sqlalchemy import text
        
        try:
            # Get all sessions
            sessions = db_session.execute(
                text("""
                    SELECT id, machine_id, status, language, created_at, updated_at, session_metadata
                    FROM ai_sessions 
                    WHERE user_id = :user_id
                    ORDER BY created_at DESC
                """),
                {'user_id': user_id}
            ).fetchall()
            
            sessions_data = []
            for session in sessions:
                # Get messages for this session
                messages = db_session.execute(
                    text("""
                        SELECT id, sender, content, message_type, language, timestamp, message_metadata
                        FROM ai_messages 
                        WHERE session_id = :session_id
                        ORDER BY timestamp ASC
                    """),
                    {'session_id': session[0]}
                ).fetchall()
                
                # Decrypt messages if encrypted
                decrypted_messages = []
                for msg in messages:
                    decrypted_content = self.decrypt_message(msg[2])
                    decrypted_messages.append({
                        'id': msg[0],
                        'sender': msg[1],
                        'content': decrypted_content,
                        'message_type': msg[3],
                        'language': msg[4],
                        'timestamp': msg[5].isoformat() if msg[5] else None,
                        'metadata': msg[6]
                    })
                
                sessions_data.append({
                    'session_id': session[0],
                    'machine_id': session[1],
                    'status': session[2],
                    'language': session[3],
                    'created_at': session[4].isoformat() if session[4] else None,
                    'updated_at': session[5].isoformat() if session[5] else None,
                    'metadata': session[6],
                    'messages': decrypted_messages
                })
            
            # Get expert knowledge contributions
            expert_knowledge = db_session.execute(
                text("""
                    SELECT id, problem_description, solution, machine_version, tags, verified, created_at
                    FROM expert_knowledge 
                    WHERE expert_user_id = :user_id
                    ORDER BY created_at DESC
                """),
                {'user_id': user_id}
            ).fetchall()
            
            expert_data = [{
                'id': ek[0],
                'problem_description': ek[1],
                'solution': ek[2],
                'machine_version': ek[3],
                'tags': ek[4],
                'verified': ek[5],
                'created_at': ek[6].isoformat() if ek[6] else None
            } for ek in expert_knowledge]
            
            return {
                'user_id': user_id,
                'export_date': datetime.utcnow().isoformat(),
                'sessions': sessions_data,
                'expert_knowledge': expert_data,
                'total_sessions': len(sessions_data),
                'total_messages': sum(len(s['messages']) for s in sessions_data),
                'total_expert_contributions': len(expert_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to export user data for {user_id}: {e}")
            raise
    
    def create_audit_log(self, action: str, user_id: str, details: Dict[str, Any], db_session) -> None:
        """
        Create an audit log entry for security-sensitive actions.
        
        Args:
            action: Action performed (e.g., 'data_deletion', 'data_export')
            user_id: User who performed the action
            details: Additional details about the action
            db_session: Database session
        """
        from sqlalchemy import text
        
        try:
            db_session.execute(
                text("""
                    INSERT INTO security_audit_logs 
                    (id, action, user_id, details, created_at)
                    VALUES (:id, :action, :user_id, :details, :created_at)
                """),
                {
                    'id': hashlib.sha256(f"{action}{user_id}{datetime.utcnow()}".encode()).hexdigest()[:32],
                    'action': action,
                    'user_id': user_id,
                    'details': str(details),
                    'created_at': datetime.utcnow()
                }
            )
            db_session.commit()
            logger.info(f"Audit log created: {action} by {user_id}")
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            # Don't raise - audit log failure shouldn't block operations


# Global security service instance
_security_service: Optional[SecurityService] = None


def get_security_service() -> SecurityService:
    """Get or create the global security service instance."""
    global _security_service
    if _security_service is None:
        _security_service = SecurityService()
    return _security_service
