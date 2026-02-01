"""
User Consent Management Service for AI Assistant

This service manages user consent for data processing, privacy policies,
and terms of service in compliance with GDPR and other privacy regulations.

Validates Requirements: 10.2, 10.3, 10.5
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class ConsentType(str, Enum):
    """Types of user consent."""
    DATA_PROCESSING = "data_processing"
    AI_INTERACTION = "ai_interaction"
    DATA_STORAGE = "data_storage"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    THIRD_PARTY_SHARING = "third_party_sharing"


class ConsentStatus(str, Enum):
    """Status of user consent."""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"


class ConsentService:
    """
    Service for managing user consent and privacy policy acceptance.
    
    Features:
    - Track user consent for various data processing activities
    - Manage privacy policy versions and acceptance
    - Handle consent withdrawal
    - Generate consent reports for compliance
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_consent_id(self, user_id: str, consent_type: str, timestamp: datetime) -> str:
        """Generate a unique consent record ID."""
        data = f"{user_id}{consent_type}{timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    async def record_consent(
        self,
        db: Session,
        user_id: str,
        consent_type: ConsentType,
        status: ConsentStatus,
        consent_text: Optional[str] = None,
        privacy_policy_version: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Record user consent for a specific type of data processing.
        
        Args:
            db: Database session
            user_id: User identifier
            consent_type: Type of consent
            status: Consent status (granted, denied, withdrawn)
            consent_text: Text of the consent agreement
            privacy_policy_version: Version of privacy policy accepted
            ip_address: User's IP address
            user_agent: User's browser/client information
            
        Returns:
            True if recorded successfully
        """
        try:
            timestamp = datetime.utcnow()
            consent_id = self.generate_consent_id(user_id, consent_type.value, timestamp)
            
            query = text("""
                INSERT INTO user_consent_records (
                    consent_id, user_id, consent_type, status, consent_text,
                    privacy_policy_version, ip_address, user_agent, created_at, updated_at
                ) VALUES (
                    :consent_id, :user_id, :consent_type, :status, :consent_text,
                    :privacy_policy_version, :ip_address, :user_agent, :created_at, :updated_at
                )
                ON CONFLICT (user_id, consent_type) 
                DO UPDATE SET 
                    status = :status,
                    consent_text = :consent_text,
                    privacy_policy_version = :privacy_policy_version,
                    ip_address = :ip_address,
                    user_agent = :user_agent,
                    updated_at = :updated_at
            """)
            
            db.execute(query, {
                "consent_id": consent_id,
                "user_id": user_id,
                "consent_type": consent_type.value,
                "status": status.value,
                "consent_text": consent_text,
                "privacy_policy_version": privacy_policy_version,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": timestamp,
                "updated_at": timestamp
            })
            
            db.commit()
            self.logger.info(f"Consent recorded: {consent_type.value} - {status.value} for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record consent: {e}")
            db.rollback()
            return False
    
    async def get_user_consent(
        self,
        db: Session,
        user_id: str,
        consent_type: Optional[ConsentType] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user consent records.
        
        Args:
            db: Database session
            user_id: User identifier
            consent_type: Optional specific consent type to retrieve
            
        Returns:
            List of consent records
        """
        try:
            if consent_type:
                query = text("""
                    SELECT consent_id, user_id, consent_type, status, consent_text,
                           privacy_policy_version, ip_address, user_agent, created_at, updated_at
                    FROM user_consent_records
                    WHERE user_id = :user_id AND consent_type = :consent_type
                    ORDER BY updated_at DESC
                """)
                result = db.execute(query, {
                    "user_id": user_id,
                    "consent_type": consent_type.value
                }).fetchall()
            else:
                query = text("""
                    SELECT consent_id, user_id, consent_type, status, consent_text,
                           privacy_policy_version, ip_address, user_agent, created_at, updated_at
                    FROM user_consent_records
                    WHERE user_id = :user_id
                    ORDER BY updated_at DESC
                """)
                result = db.execute(query, {"user_id": user_id}).fetchall()
            
            consents = []
            for row in result:
                consents.append({
                    "consent_id": row.consent_id,
                    "user_id": row.user_id,
                    "consent_type": row.consent_type,
                    "status": row.status,
                    "consent_text": row.consent_text,
                    "privacy_policy_version": row.privacy_policy_version,
                    "ip_address": row.ip_address,
                    "user_agent": row.user_agent,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None
                })
            
            return consents
            
        except Exception as e:
            self.logger.error(f"Failed to get user consent: {e}")
            return []
    
    async def check_consent(
        self,
        db: Session,
        user_id: str,
        consent_type: ConsentType
    ) -> bool:
        """
        Check if user has granted consent for a specific type.
        
        Args:
            db: Database session
            user_id: User identifier
            consent_type: Type of consent to check
            
        Returns:
            True if consent is granted, False otherwise
        """
        try:
            query = text("""
                SELECT status
                FROM user_consent_records
                WHERE user_id = :user_id AND consent_type = :consent_type
                ORDER BY updated_at DESC
                LIMIT 1
            """)
            
            result = db.execute(query, {
                "user_id": user_id,
                "consent_type": consent_type.value
            }).fetchone()
            
            return result and result.status == ConsentStatus.GRANTED.value
            
        except Exception as e:
            self.logger.error(f"Failed to check consent: {e}")
            return False
    
    async def withdraw_consent(
        self,
        db: Session,
        user_id: str,
        consent_type: ConsentType,
        reason: Optional[str] = None
    ) -> bool:
        """
        Withdraw user consent for a specific type.
        
        Args:
            db: Database session
            user_id: User identifier
            consent_type: Type of consent to withdraw
            reason: Optional reason for withdrawal
            
        Returns:
            True if withdrawn successfully
        """
        try:
            timestamp = datetime.utcnow()
            
            query = text("""
                UPDATE user_consent_records
                SET status = :status,
                    updated_at = :updated_at,
                    consent_text = COALESCE(consent_text, '') || ' [WITHDRAWN: ' || :reason || ']'
                WHERE user_id = :user_id AND consent_type = :consent_type
            """)
            
            db.execute(query, {
                "status": ConsentStatus.WITHDRAWN.value,
                "updated_at": timestamp,
                "reason": reason or "User requested",
                "user_id": user_id,
                "consent_type": consent_type.value
            })
            
            db.commit()
            self.logger.info(f"Consent withdrawn: {consent_type.value} for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to withdraw consent: {e}")
            db.rollback()
            return False
    
    async def record_privacy_policy_acceptance(
        self,
        db: Session,
        user_id: str,
        policy_version: str,
        policy_text: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Record user acceptance of privacy policy.
        
        Args:
            db: Database session
            user_id: User identifier
            policy_version: Version of privacy policy
            policy_text: Full text of privacy policy
            ip_address: User's IP address
            user_agent: User's browser/client information
            
        Returns:
            True if recorded successfully
        """
        try:
            timestamp = datetime.utcnow()
            acceptance_id = hashlib.sha256(f"{user_id}{policy_version}{timestamp}".encode()).hexdigest()[:32]
            
            query = text("""
                INSERT INTO privacy_policy_acceptances (
                    acceptance_id, user_id, policy_version, policy_text,
                    ip_address, user_agent, accepted_at
                ) VALUES (
                    :acceptance_id, :user_id, :policy_version, :policy_text,
                    :ip_address, :user_agent, :accepted_at
                )
            """)
            
            db.execute(query, {
                "acceptance_id": acceptance_id,
                "user_id": user_id,
                "policy_version": policy_version,
                "policy_text": policy_text,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "accepted_at": timestamp
            })
            
            db.commit()
            self.logger.info(f"Privacy policy acceptance recorded: v{policy_version} for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record privacy policy acceptance: {e}")
            db.rollback()
            return False
    
    async def get_privacy_policy_acceptance(
        self,
        db: Session,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user's latest privacy policy acceptance.
        
        Args:
            db: Database session
            user_id: User identifier
            
        Returns:
            Privacy policy acceptance record or None
        """
        try:
            query = text("""
                SELECT acceptance_id, user_id, policy_version, policy_text,
                       ip_address, user_agent, accepted_at
                FROM privacy_policy_acceptances
                WHERE user_id = :user_id
                ORDER BY accepted_at DESC
                LIMIT 1
            """)
            
            result = db.execute(query, {"user_id": user_id}).fetchone()
            
            if result:
                return {
                    "acceptance_id": result.acceptance_id,
                    "user_id": result.user_id,
                    "policy_version": result.policy_version,
                    "policy_text": result.policy_text,
                    "ip_address": result.ip_address,
                    "user_agent": result.user_agent,
                    "accepted_at": result.accepted_at.isoformat() if result.accepted_at else None
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get privacy policy acceptance: {e}")
            return None
    
    async def get_consent_summary(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get summary of consent records for compliance reporting.
        
        Args:
            db: Database session
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Consent summary data
        """
        try:
            where_clauses = []
            params = {}
            
            if start_date:
                where_clauses.append("updated_at >= :start_date")
                params["start_date"] = start_date
            
            if end_date:
                where_clauses.append("updated_at <= :end_date")
                params["end_date"] = end_date
            
            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            # Consent by type and status
            query = text(f"""
                SELECT consent_type, status, COUNT(*) as count
                FROM user_consent_records
                WHERE {where_clause}
                GROUP BY consent_type, status
            """)
            
            result = db.execute(query, params).fetchall()
            
            consent_by_type = {}
            for row in result:
                if row.consent_type not in consent_by_type:
                    consent_by_type[row.consent_type] = {}
                consent_by_type[row.consent_type][row.status] = row.count
            
            # Privacy policy acceptances
            policy_query = text(f"""
                SELECT policy_version, COUNT(*) as count
                FROM privacy_policy_acceptances
                WHERE {where_clause.replace('updated_at', 'accepted_at')}
                GROUP BY policy_version
            """)
            
            result = db.execute(policy_query, params).fetchall()
            
            policy_acceptances = {
                row.policy_version: row.count for row in result
            }
            
            return {
                "consent_by_type": consent_by_type,
                "privacy_policy_acceptances": policy_acceptances,
                "total_consent_records": sum(
                    sum(statuses.values()) for statuses in consent_by_type.values()
                ),
                "total_policy_acceptances": sum(policy_acceptances.values())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get consent summary: {e}")
            return {"error": str(e)}
    
    def get_required_consents(self) -> List[Dict[str, Any]]:
        """
        Get list of required consents for AI Assistant usage.
        
        Returns:
            List of required consent types with descriptions
        """
        return [
            {
                "consent_type": ConsentType.DATA_PROCESSING.value,
                "required": True,
                "description": "Processing of personal data for AI assistance",
                "purpose": "To provide AI-powered troubleshooting assistance"
            },
            {
                "consent_type": ConsentType.AI_INTERACTION.value,
                "required": True,
                "description": "AI interaction and conversation storage",
                "purpose": "To maintain conversation history and improve responses"
            },
            {
                "consent_type": ConsentType.DATA_STORAGE.value,
                "required": True,
                "description": "Storage of conversation data",
                "purpose": "To enable session continuity and historical reference"
            },
            {
                "consent_type": ConsentType.ANALYTICS.value,
                "required": False,
                "description": "Usage analytics and performance monitoring",
                "purpose": "To improve AI Assistant quality and user experience"
            },
            {
                "consent_type": ConsentType.MARKETING.value,
                "required": False,
                "description": "Marketing communications",
                "purpose": "To send product updates and feature announcements"
            },
            {
                "consent_type": ConsentType.THIRD_PARTY_SHARING.value,
                "required": False,
                "description": "Sharing data with third-party service providers",
                "purpose": "To enable advanced AI features through external services"
            }
        ]


# Global consent service instance
_consent_service: Optional[ConsentService] = None


def get_consent_service() -> ConsentService:
    """Get or create the global consent service instance."""
    global _consent_service
    if _consent_service is None:
        _consent_service = ConsentService()
    return _consent_service
