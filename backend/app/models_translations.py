# backend/app/models_translations.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class ProtocolTranslation(Base):
    """
    SQLAlchemy model for maintenance protocol translations.
    Stores translated content for protocols in different languages.
    """
    __tablename__ = "protocol_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    protocol_id = Column(UUID(as_uuid=True), ForeignKey("maintenance_protocols.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(5), nullable=False)  # 'en', 'el', 'ar', 'es', 'tr', 'no'
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    protocol = relationship("MaintenanceProtocol", back_populates="translations")

    def __repr__(self):
        return f"<ProtocolTranslation(protocol_id={self.protocol_id}, language={self.language_code}, name='{self.name[:30]}...')>"


class ChecklistItemTranslation(Base):
    """
    SQLAlchemy model for checklist item translations.
    Stores translated content for checklist items in different languages.
    """
    __tablename__ = "checklist_item_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    checklist_item_id = Column(UUID(as_uuid=True), ForeignKey("checklist_items.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(5), nullable=False)
    item_description = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    item_category = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    checklist_item = relationship("ChecklistItem", back_populates="translations")

    def __repr__(self):
        return f"<ChecklistItemTranslation(item_id={self.checklist_item_id}, language={self.language_code}, description='{self.item_description[:30]}...')>"