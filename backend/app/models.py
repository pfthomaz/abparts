# backend/app/models.py

import uuid
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, ARRAY # Import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    address = Column(Text)
    contact_info = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    users = relationship("User", back_populates="organization")
    inventory_items = relationship("Inventory", back_populates="organization")
    supplier_orders = relationship("SupplierOrder", back_populates="ordering_organization")
    customer_orders_placed = relationship("CustomerOrder", foreign_keys="[CustomerOrder.customer_organization_id]", back_populates="customer_organization")
    customer_orders_received = relationship("CustomerOrder", foreign_keys="[CustomerOrder.oraseas_organization_id]", back_populates="oraseas_organization")
    part_usages = relationship("PartUsage", back_populates="customer_organization")


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    organization = relationship("Organization", back_populates="users")
    customer_orders_placed = relationship("CustomerOrder", back_populates="ordered_by_user")
    part_usages = relationship("PartUsage", back_populates="recorded_by_user")


class Part(Base):
    __tablename__ = "parts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_number = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_proprietary = Column(Boolean, default=False, nullable=False)
    is_consumable = Column(Boolean, default=False, nullable=False)
    manufacturer_delivery_time_days = Column(Integer)
    local_supplier_delivery_time_days = Column(Integer)
    image_urls = Column(ARRAY(String), default=[], nullable=False) # New: Column to store image URLs
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    inventory_items = relationship("Inventory", back_populates="part")
    supplier_order_items = relationship("SupplierOrderItem", back_populates="part")
    customer_order_items = relationship("CustomerOrderItem", back_populates="part")
    part_usages = relationship("PartUsage", back_populates="part")


class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    current_stock = Column(Integer, default=0, nullable=False)
    minimum_stock_recommendation = Column(Integer, default=0, nullable=False)
    reorder_threshold_set_by = Column(String)
    last_recommendation_update = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    organization = relationship("Organization", back_populates="inventory_items")
    part = relationship("Part", back_populates="inventory_items")

    __table_args__ = (
        # Ensure unique inventory record per organization-part pair
        # This covers the "UNIQUE(organization_id, part_id)" requirement
        # from the database schema design document.
        # This will create a unique constraint in the DB.
        {"unique_together": ("organization_id", "part_id")},
    )


class SupplierOrder(Base):
    __tablename__ = "supplier_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ordering_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    supplier_name = Column(String, nullable=False)
    order_date = Column(DateTime(timezone=True), nullable=False)
    expected_delivery_date = Column(DateTime(timezone=True))
    actual_delivery_date = Column(DateTime(timezone=True))
    status = Column(String, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    ordering_organization = relationship("Organization", back_populates="supplier_orders")
    items = relationship("SupplierOrderItem", back_populates="supplier_order")


class SupplierOrderItem(Base):
    __tablename__ = "supplier_order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_order_id = Column(UUID(as_uuid=True), ForeignKey("supplier_orders.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(DECIMAL(10, 2))
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    supplier_order = relationship("SupplierOrder", back_populates="items")
    part = relationship("Part", back_populates="supplier_order_items")


class CustomerOrder(Base):
    __tablename__ = "customer_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    oraseas_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False) # Points to Oraseas EE
    order_date = Column(DateTime(timezone=True), nullable=False)
    expected_delivery_date = Column(DateTime(timezone=True))
    actual_delivery_date = Column(DateTime(timezone=True))
    status = Column(String, nullable=False)
    ordered_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    customer_organization = relationship("Organization", foreign_keys=[customer_organization_id], back_populates="customer_orders_placed")
    oraseas_organization = relationship("Organization", foreign_keys=[oraseas_organization_id], back_populates="customer_orders_received")
    ordered_by_user = relationship("User", back_populates="customer_orders_placed")
    items = relationship("CustomerOrderItem", back_populates="customer_order")


class CustomerOrderItem(Base):
    __tablename__ = "customer_order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_order_id = Column(UUID(as_uuid=True), ForeignKey("customer_orders.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(DECIMAL(10, 2))
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    customer_order = relationship("CustomerOrder", back_populates="items")
    part = relationship("Part", back_populates="customer_order_items")


class PartUsage(Base):
    __tablename__ = "part_usage"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    usage_date = Column(DateTime(timezone=True), nullable=False)
    quantity_used = Column(Integer, default=1, nullable=False)
    machine_id = Column(String)
    recorded_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    customer_organization = relationship("Organization", back_populates="part_usages")
    part = relationship("Part", back_populates="part_usages")
    recorded_by_user = relationship("User", back_populates="part_usages")
