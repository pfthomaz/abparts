# backend/app/models.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .database import Base # Import Base from your database configuration

# --- SQLAlchemy Models ---
class Organization(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    type = Column(String(50), nullable=False) # e.g., 'Warehouse', 'Customer', 'Supplier'
    address = Column(Text)
    contact_info = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    users = relationship("User", back_populates="organization")
    inventories = relationship("Inventory", back_populates="organization")
    supplier_orders_placed = relationship("SupplierOrder", foreign_keys="[SupplierOrder.ordering_organization_id]", back_populates="ordering_organization")
    customer_orders_placed = relationship("CustomerOrder", foreign_keys="[CustomerOrder.customer_organization_id]", back_populates="customer_organization")
    customer_orders_received = relationship("CustomerOrder", foreign_keys="[CustomerOrder.oraseas_organization_id]", back_populates="oraseas_organization")
    part_usages = relationship("PartUsage", back_populates="customer_organization")

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    role = Column(String(50), nullable=False) # e.g., 'Oraseas Admin', 'Customer Admin', 'Customer User'
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    organization = relationship("Organization", back_populates="users")
    customer_orders_placed_by = relationship("CustomerOrder", back_populates="ordered_by_user")
    part_usages_recorded_by = relationship("PartUsage", back_populates="recorded_by_user")


class Part(Base):
    __tablename__ = "parts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_number = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_proprietary = Column(Boolean, nullable=False, default=False)
    is_consumable = Column(Boolean, nullable=False, default=False)
    manufacturer_delivery_time_days = Column(Integer)
    local_supplier_delivery_time_days = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    inventories = relationship("Inventory", back_populates="part")
    supplier_order_items = relationship("SupplierOrderItem", back_populates="part")
    customer_order_items = relationship("CustomerOrderItem", back_populates="part")
    part_usages = relationship("PartUsage", back_populates="part")


class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    current_stock = Column(Integer, nullable=False, default=0)
    minimum_stock_recommendation = Column(Integer, nullable=False, default=0)
    reorder_threshold_set_by = Column(String(50))
    last_recommendation_update = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (UniqueConstraint('organization_id', 'part_id', name='_organization_part_uc'),)

    organization = relationship("Organization", back_populates="inventories")
    part = relationship("Part", back_populates="inventories")


class SupplierOrder(Base):
    __tablename__ = "supplier_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ordering_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    supplier_name = Column(String(255), nullable=False)
    order_date = Column(DateTime(timezone=True), nullable=False)
    expected_delivery_date = Column(DateTime(timezone=True))
    actual_delivery_date = Column(DateTime(timezone=True))
    status = Column(String(50), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    ordering_organization = relationship("Organization", foreign_keys=[ordering_organization_id], back_populates="supplier_orders_placed")
    items = relationship("SupplierOrderItem", back_populates="supplier_order")


class SupplierOrderItem(Base):
    __tablename__ = "supplier_order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_order_id = Column(UUID(as_uuid=True), ForeignKey("supplier_orders.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(DECIMAL(10, 2))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    supplier_order = relationship("SupplierOrder", back_populates="items")
    part = relationship("Part", back_populates="supplier_order_items")


class CustomerOrder(Base):
    __tablename__ = "customer_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    oraseas_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    order_date = Column(DateTime(timezone=True), nullable=False)
    expected_delivery_date = Column(DateTime(timezone=True))
    actual_delivery_date = Column(DateTime(timezone=True))
    status = Column(String(50), nullable=False)
    ordered_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    customer_organization = relationship("Organization", foreign_keys=[customer_organization_id], back_populates="customer_orders_placed")
    oraseas_organization = relationship("Organization", foreign_keys=[oraseas_organization_id], back_populates="customer_orders_received")
    ordered_by_user = relationship("User", back_populates="customer_orders_placed_by")
    items = relationship("CustomerOrderItem", back_populates="customer_order")


class CustomerOrderItem(Base):
    __tablename__ = "customer_order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_order_id = Column(UUID(as_uuid=True), ForeignKey("customer_orders.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(DECIMAL(10, 2))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    customer_order = relationship("CustomerOrder", back_populates="items")
    part = relationship("Part", back_populates="customer_order_items")


class PartUsage(Base):
    __tablename__ = "part_usage"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    usage_date = Column(DateTime(timezone=True), nullable=False)
    quantity_used = Column(Integer, nullable=False, default=1)
    machine_id = Column(String(255))
    recorded_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)

    customer_organization = relationship("Organization", back_populates="part_usages")
    part = relationship("Part", back_populates="part_usages")
    recorded_by_user = relationship("User", back_populates="part_usages_recorded_by")

