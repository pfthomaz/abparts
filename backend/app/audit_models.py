# backend/app/audit_models.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, JSON, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from .database import Base

class AuditLog(Base):
    """Audit log table for tracking all data access and modifications"""
    __tablename__ = "audit_logs"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    organization_id = Column(PostgresUUID(as_uuid=True), nullable=True)
    
    # Resource information
    resource_type = Column(String(100), nullable=False)  # e.g., 'parts', 'machines', 'organizations'
    resource_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    
    # Action information
    action = Column(String(50), nullable=False)  # e.g., 'CREATE', 'READ', 'UPDATE', 'DELETE'
    
    # Change tracking
    old_values = Column(JSON, nullable=True)  # Previous values for updates
    new_values = Column(JSON, nullable=True)  # New values for creates/updates
    
    # Additional context
    details = Column(JSON, nullable=True)  # Additional context information
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    
    # Request information
    endpoint = Column(String(255), nullable=True)
    http_method = Column(String(10), nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class SecurityEvent(Base):
    """Security events table for tracking security-related incidents"""
    __tablename__ = "security_events"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Event classification
    event_type = Column(String(100), nullable=False)  # e.g., 'UNAUTHORIZED_ACCESS', 'ISOLATION_VIOLATION'
    severity = Column(String(20), nullable=False)  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    
    # User and organization context
    user_id = Column(PostgresUUID(as_uuid=True), nullable=True)
    organization_id = Column(PostgresUUID(as_uuid=True), nullable=True)
    
    # Event details
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Request context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True)
    
    # Resolution tracking
    resolved = Column(String(20), nullable=False, default='OPEN')  # 'OPEN', 'INVESTIGATING', 'RESOLVED'
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)