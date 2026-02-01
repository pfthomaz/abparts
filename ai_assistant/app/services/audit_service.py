"""
Comprehensive Audit Logging Service for AI Assistant

This service implements comprehensive audit logging for all AI interactions,
including conversation tracking, user actions, system events, and compliance monitoring.

Validates Requirements: 10.2, 10.3, 10.5
"""

import logging
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events."""
    # AI Interaction Events
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    AI_RESPONSE_GENERATED = "ai_response_generated"
    
    # User Actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    MACHINE_SELECTED = "machine_selected"
    FEEDBACK_PROVIDED = "feedback_provided"
    ESCALATION_REQUESTED = "escalation_requested"
    
    # Data Management
    DATA_EXPORTED = "data_exported"
    DATA_DELETED = "data_deleted"
    CONSENT_GIVEN = "consent_given"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    
    # System Events
    SENSITIVE_DATA_DETECTED = "sensitive_data_detected"
    ENCRYPTION_APPLIED = "encryption_applied"
    RETENTION_POLICY_APPLIED = "retention_policy_applied"
    DATA_CLEANUP_EXECUTED = "data_cleanup_executed"
    
    # Knowledge Base Events
    KNOWLEDGE_ACCESSED = "knowledge_accessed"
    EXPERT_KNOWLEDGE_ADDED = "expert_knowledge_added"
    DOCUMENT_UPLOADED = "document_uploaded"
    
    # Security Events
    AUTHENTICATION_FAILED = "authentication_failed"
    UNAUTHORIZED_ACCESS_ATTEMPT = "unauthorized_access_attempt"
    SUSPICIOUS_ACTIVITY_DETECTED = "suspicious_activity_detected"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditService:
    """
    Service for comprehensive audit logging of all AI Assistant interactions.
    
    Features:
    - Track all AI interactions and user actions
    - Compliance monitoring and reporting
    - Security event logging
    - Data access tracking
    - Retention policy enforcement logging
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_audit_id(self, event_type: str, user_id: str, timestamp: datetime) -> str:
        """Generate a unique audit ID."""
        data = f"{event_type}{user_id}{timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    async def log_ai_interaction(
        self,
        db: Session,
        event_type: AuditEventType,
        user_id: str,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Log an AI interaction event.
        
        Args:
            db: Database session
            event_type: Type of audit event
            user_id: User identifier
            session_id: AI session identifier (if applicable)
            message_id: Message identifier (if applicable)
            details: Additional event details
            severity: Event severity level
            ip_address: User's IP address
            user_agent: User's browser/client information
            
        Returns:
            True if logged successfully, False otherwise
        """
        try:
            timestamp = datetime.utcnow()
            audit_id = self.generate_audit_id(event_type.value, user_id, timestamp)
            
            # Prepare details JSON
            details_json = json.dumps(details) if details else None
            
            query = text("""
                INSERT INTO ai_interaction_audit_logs (
                    audit_id, event_type, user_id, session_id, message_id,
                    details, severity, ip_address, user_agent, created_at
                ) VALUES (
                    :audit_id, :event_type, :user_id, :session_id, :message_id,
                    :details, :severity, :ip_address, :user_agent, :created_at
                )
            """)
            
            db.execute(query, {
                "audit_id": audit_id,
                "event_type": event_type.value,
                "user_id": user_id,
                "session_id": session_id,
                "message_id": message_id,
                "details": details_json,
                "severity": severity.value,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": timestamp
            })
            
            db.commit()
            self.logger.info(f"Audit log created: {event_type.value} for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create audit log: {e}")
            db.rollback()
            # Don't raise - audit log failure shouldn't block operations
            return False
    
    async def log_data_access(
        self,
        db: Session,
        user_id: str,
        accessed_user_id: str,
        access_type: str,
        data_type: str,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Log data access events for compliance tracking.
        
        Args:
            db: Database session
            user_id: User performing the access
            accessed_user_id: User whose data is being accessed
            access_type: Type of access (read, export, delete)
            data_type: Type of data accessed (messages, sessions, etc.)
            reason: Reason for access
            ip_address: IP address of accessor
            
        Returns:
            True if logged successfully
        """
        try:
            timestamp = datetime.utcnow()
            
            query = text("""
                INSERT INTO data_access_logs (
                    accessor_user_id, accessed_user_id, access_type, data_type,
                    reason, ip_address, accessed_at
                ) VALUES (
                    :accessor_user_id, :accessed_user_id, :access_type, :data_type,
                    :reason, :ip_address, :accessed_at
                )
            """)
            
            db.execute(query, {
                "accessor_user_id": user_id,
                "accessed_user_id": accessed_user_id,
                "access_type": access_type,
                "data_type": data_type,
                "reason": reason,
                "ip_address": ip_address,
                "accessed_at": timestamp
            })
            
            db.commit()
            self.logger.info(f"Data access logged: {access_type} on {data_type} by {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log data access: {e}")
            db.rollback()
            return False
    
    async def get_user_audit_trail(
        self,
        db: Session,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail for a specific user.
        
        Args:
            db: Database session
            user_id: User identifier
            start_date: Start date for filtering
            end_date: End date for filtering
            event_types: List of event types to filter
            limit: Maximum number of records to return
            
        Returns:
            List of audit log entries
        """
        try:
            # Build query with filters
            where_clauses = ["user_id = :user_id"]
            params = {"user_id": user_id, "limit": limit}
            
            if start_date:
                where_clauses.append("created_at >= :start_date")
                params["start_date"] = start_date
            
            if end_date:
                where_clauses.append("created_at <= :end_date")
                params["end_date"] = end_date
            
            if event_types:
                placeholders = ", ".join([f":event_type_{i}" for i in range(len(event_types))])
                where_clauses.append(f"event_type IN ({placeholders})")
                for i, event_type in enumerate(event_types):
                    params[f"event_type_{i}"] = event_type
            
            where_clause = " AND ".join(where_clauses)
            
            query = text(f"""
                SELECT 
                    audit_id, event_type, user_id, session_id, message_id,
                    details, severity, ip_address, user_agent, created_at
                FROM ai_interaction_audit_logs
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit
            """)
            
            result = db.execute(query, params).fetchall()
            
            audit_trail = []
            for row in result:
                audit_trail.append({
                    "audit_id": row.audit_id,
                    "event_type": row.event_type,
                    "user_id": row.user_id,
                    "session_id": row.session_id,
                    "message_id": row.message_id,
                    "details": json.loads(row.details) if row.details else None,
                    "severity": row.severity,
                    "ip_address": row.ip_address,
                    "user_agent": row.user_agent,
                    "created_at": row.created_at.isoformat() if row.created_at else None
                })
            
            return audit_trail
            
        except Exception as e:
            self.logger.error(f"Failed to get user audit trail: {e}")
            return []
    
    async def generate_compliance_report(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        report_type: str = "full"
    ) -> Dict[str, Any]:
        """
        Generate a compliance report for the specified period.
        
        Args:
            db: Database session
            start_date: Report start date
            end_date: Report end date
            report_type: Type of report (full, gdpr, security, data_access)
            
        Returns:
            Compliance report data
        """
        try:
            report = {
                "report_type": report_type,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Total AI interactions
            interactions_query = text("""
                SELECT COUNT(*) as total_interactions,
                       COUNT(DISTINCT user_id) as unique_users,
                       COUNT(DISTINCT session_id) as total_sessions
                FROM ai_interaction_audit_logs
                WHERE created_at BETWEEN :start_date AND :end_date
            """)
            
            result = db.execute(interactions_query, {
                "start_date": start_date,
                "end_date": end_date
            }).fetchone()
            
            report["ai_interactions"] = {
                "total_interactions": result.total_interactions if result else 0,
                "unique_users": result.unique_users if result else 0,
                "total_sessions": result.total_sessions if result else 0
            }
            
            # Data access events
            data_access_query = text("""
                SELECT access_type, COUNT(*) as count
                FROM data_access_logs
                WHERE accessed_at BETWEEN :start_date AND :end_date
                GROUP BY access_type
            """)
            
            result = db.execute(data_access_query, {
                "start_date": start_date,
                "end_date": end_date
            }).fetchall()
            
            report["data_access"] = {
                row.access_type: row.count for row in result
            }
            
            # GDPR requests
            gdpr_query = text("""
                SELECT status, COUNT(*) as count
                FROM user_data_deletion_requests
                WHERE request_date BETWEEN :start_date AND :end_date
                GROUP BY status
            """)
            
            result = db.execute(gdpr_query, {
                "start_date": start_date,
                "end_date": end_date
            }).fetchall()
            
            report["gdpr_requests"] = {
                row.status: row.count for row in result
            }
            
            # Sensitive data detections
            sensitive_data_query = text("""
                SELECT detection_type, COUNT(*) as count
                FROM sensitive_data_detections
                WHERE detected_at BETWEEN :start_date AND :end_date
                GROUP BY detection_type
            """)
            
            result = db.execute(sensitive_data_query, {
                "start_date": start_date,
                "end_date": end_date
            }).fetchall()
            
            report["sensitive_data_detections"] = {
                row.detection_type: row.count for row in result
            }
            
            # Security events
            security_query = text("""
                SELECT event_type, severity, COUNT(*) as count
                FROM ai_interaction_audit_logs
                WHERE created_at BETWEEN :start_date AND :end_date
                  AND event_type IN ('authentication_failed', 'unauthorized_access_attempt', 'suspicious_activity_detected')
                GROUP BY event_type, severity
            """)
            
            result = db.execute(security_query, {
                "start_date": start_date,
                "end_date": end_date
            }).fetchall()
            
            report["security_events"] = [
                {
                    "event_type": row.event_type,
                    "severity": row.severity,
                    "count": row.count
                }
                for row in result
            ]
            
            # User consent tracking
            consent_query = text("""
                SELECT consent_type, status, COUNT(*) as count
                FROM user_consent_records
                WHERE updated_at BETWEEN :start_date AND :end_date
                GROUP BY consent_type, status
            """)
            
            result = db.execute(consent_query, {
                "start_date": start_date,
                "end_date": end_date
            }).fetchall()
            
            report["user_consent"] = [
                {
                    "consent_type": row.consent_type,
                    "status": row.status,
                    "count": row.count
                }
                for row in result
            ]
            
            # Data retention compliance
            retention_query = text("""
                SELECT record_type, 
                       COUNT(*) as total_records,
                       COUNT(CASE WHEN deleted_at IS NOT NULL THEN 1 END) as deleted_records
                FROM data_retention_tracking
                WHERE created_at BETWEEN :start_date AND :end_date
                GROUP BY record_type
            """)
            
            result = db.execute(retention_query, {
                "start_date": start_date,
                "end_date": end_date
            }).fetchall()
            
            report["data_retention"] = [
                {
                    "record_type": row.record_type,
                    "total_records": row.total_records,
                    "deleted_records": row.deleted_records,
                    "retention_compliance_rate": (row.deleted_records / row.total_records * 100) if row.total_records > 0 else 0
                }
                for row in result
            ]
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {e}")
            return {"error": str(e)}
    
    async def get_system_audit_summary(
        self,
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get a summary of system audit events for the specified period.
        
        Args:
            db: Database session
            days: Number of days to include in summary
            
        Returns:
            Audit summary data
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Event type distribution
            event_distribution_query = text("""
                SELECT event_type, severity, COUNT(*) as count
                FROM ai_interaction_audit_logs
                WHERE created_at >= :start_date
                GROUP BY event_type, severity
                ORDER BY count DESC
            """)
            
            result = db.execute(event_distribution_query, {
                "start_date": start_date
            }).fetchall()
            
            event_distribution = [
                {
                    "event_type": row.event_type,
                    "severity": row.severity,
                    "count": row.count
                }
                for row in result
            ]
            
            # Daily activity
            daily_activity_query = text("""
                SELECT DATE(created_at) as date, COUNT(*) as event_count
                FROM ai_interaction_audit_logs
                WHERE created_at >= :start_date
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            
            result = db.execute(daily_activity_query, {
                "start_date": start_date
            }).fetchall()
            
            daily_activity = [
                {
                    "date": row.date.isoformat() if row.date else None,
                    "event_count": row.event_count
                }
                for row in result
            ]
            
            # Top users by activity
            top_users_query = text("""
                SELECT user_id, COUNT(*) as event_count
                FROM ai_interaction_audit_logs
                WHERE created_at >= :start_date
                GROUP BY user_id
                ORDER BY event_count DESC
                LIMIT 10
            """)
            
            result = db.execute(top_users_query, {
                "start_date": start_date
            }).fetchall()
            
            top_users = [
                {
                    "user_id": row.user_id,
                    "event_count": row.event_count
                }
                for row in result
            ]
            
            return {
                "period_days": days,
                "event_distribution": event_distribution,
                "daily_activity": daily_activity,
                "top_users": top_users,
                "summary": {
                    "total_events": sum(e["count"] for e in event_distribution),
                    "unique_users": len(top_users),
                    "avg_daily_events": sum(d["event_count"] for d in daily_activity) / len(daily_activity) if daily_activity else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system audit summary: {e}")
            return {"error": str(e)}


# Global audit service instance
_audit_service: Optional[AuditService] = None


def get_audit_service() -> AuditService:
    """Get or create the global audit service instance."""
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service
