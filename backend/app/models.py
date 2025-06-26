# backend/app/models.py

import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Text, ARRAY, DECIMAL, UniqueConstraint # Added UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Import func for default timestamps

from .database import Base

class Organization(Base):
    """
    SQLAlchemy model for the 'organizations' table.
    Represents Oraseas EE and its customer organizations.
    """
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    type = Column(String(50), nullable=False) # e.g., 'Warehouse', 'Customer', 'Supplier'
    address = Column(Text)
    contact_info = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    machines = relationship("Machine", back_populates="organization", cascade="all, delete-orphan") # New: Machines relationship
    inventory_items = relationship("Inventory", back_populates="organization", cascade="all, delete-orphan")
    supplier_orders = relationship("SupplierOrder", back_populates="ordering_organization", cascade="all, delete-orphan")
    customer_orders_placed = relationship(
        "CustomerOrder",
        foreign_keys="[CustomerOrder.customer_organization_id]",
        back_populates="customer_organization",
        cascade="all, delete-orphan"
    )
    customer_orders_received = relationship(
        "CustomerOrder",
        foreign_keys="[CustomerOrder.oraseas_organization_id]",
        back_populates="oraseas_organization",
        cascade="all, delete-orphan"
    )
    part_usage_records = relationship("PartUsage", back_populates="customer_organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', type='{self.type}')>"


class User(Base):
    """
    SQLAlchemy model for the 'users' table.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    role = Column(String(50), nullable=False) # e.g., 'Oraseas Admin', 'Customer User'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    part_usage_records = relationship("PartUsage", back_populates="recorded_by_user")
    customer_orders_placed = relationship("CustomerOrder", back_populates="ordered_by_user") # This side is correct

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', organization_id={self.organization_id})>"


class Machine(Base):
    """
    SQLAlchemy model for the 'machines' table. (New!)
    Represents AutoBoss machines owned by customer organizations.
    """
    __tablename__ = "machines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    model_type = Column(String(100), nullable=False) # e.g., 'V3.1B', 'V4.0'
    name = Column(String(255), nullable=False)
    serial_number = Column(String(255), unique=True, nullable=False) # Unique across all machines
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="machines")
    part_usage_records = relationship("PartUsage", back_populates="machine", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Machine(id={self.id}, name='{self.name}', model_type='{self.model_type}', serial_number='{self.serial_number}')>"


class Part(Base):
    """
    SQLAlchemy model for the 'parts' table.
    """
    __tablename__ = "parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_number = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_proprietary = Column(Boolean, nullable=False, default=False)
    is_consumable = Column(Boolean, nullable=False, default=False)
    manufacturer_delivery_time_days = Column(Integer)
    local_supplier_delivery_time_days = Column(Integer)
    image_urls = Column(ARRAY(Text)) # Array of strings
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    inventory_items = relationship("Inventory", back_populates="part", cascade="all, delete-orphan")
    supplier_order_items = relationship("SupplierOrderItem", back_populates="part", cascade="all, delete-orphan")
    customer_order_items = relationship("CustomerOrderItem", back_populates="part", cascade="all, delete-orphan")
    part_usage_records = relationship("PartUsage", back_populates="part", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Part(id={self.id}, part_number='{self.part_number}', name='{self.name}')>"


class Inventory(Base):
    """
    SQLAlchemy model for the 'inventory' table.
    Tracks part stock levels for each organization.
    """
    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    current_stock = Column(Integer, nullable=False, default=0)
    minimum_stock_recommendation = Column(Integer, nullable=False, default=0)
    reorder_threshold_set_by = Column(String(50)) # e.g., 'system', 'user'
    last_recommendation_update = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('organization_id', 'part_id', name='_organization_part_uc'),
    )

    # Relationships
    organization = relationship("Organization", back_populates="inventory_items")
    part = relationship("Part", back_populates="inventory_items")

    def __repr__(self):
        return f"<Inventory(id={self.id}, org_id={self.organization_id}, part_id={self.part_id}, stock={self.current_stock})>"


class SupplierOrder(Base):
    """
    SQLAlchemy model for the 'supplier_orders' table.
    Records orders placed by Oraseas EE to external suppliers.
    """
    __tablename__ = "supplier_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ordering_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False) # Should be Oraseas EE
    supplier_name = Column(String(255), nullable=False)
    order_date = Column(DateTime(timezone=True), nullable=False)
    expected_delivery_date = Column(DateTime(timezone=True))
    actual_delivery_date = Column(DateTime(timezone=True))
    status = Column(String(50), nullable=False) # e.g., 'Pending', 'Shipped', 'Delivered'
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    ordering_organization = relationship("Organization", back_populates="supplier_orders")
    items = relationship("SupplierOrderItem", back_populates="supplier_order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SupplierOrder(id={self.id}, supplier='{self.supplier_name}', status='{self.status}')>"


class SupplierOrderItem(Base):
    """
    SQLAlchemy model for the 'supplier_order_items' table.
    Details parts within a supplier order.
    """
    __tablename__ = "supplier_order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_order_id = Column(UUID(as_uuid=True), ForeignKey("supplier_orders.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(DECIMAL(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    supplier_order = relationship("SupplierOrder", back_populates="items")
    part = relationship("Part", back_populates="supplier_order_items")

    def __repr__(self):
        return f"<SupplierOrderItem(id={self.id}, order_id={self.supplier_order_id}, part_id={self.part_id}, qty={self.quantity})>"


class CustomerOrder(Base):
    """
    SQLAlchemy model for the 'customer_orders' table.
    Records orders placed by customers to Oraseas EE.
    """
    __tablename__ = "customer_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    oraseas_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    order_date = Column(DateTime(timezone=True), nullable=False)
    expected_delivery_date = Column(DateTime(timezone=True))
    actual_delivery_date = Column(DateTime(timezone=True))
    status = Column(String(50), nullable=False) # e.g., 'Pending', 'Shipped', 'Delivered'
    ordered_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer_organization = relationship(
        "Organization",
        foreign_keys=[customer_organization_id],
        back_populates="customer_orders_placed"
    )
    oraseas_organization = relationship(
        "Organization",
        foreign_keys=[oraseas_organization_id],
        back_populates="customer_orders_received"
    )
    ordered_by_user = relationship("User", back_populates="customer_orders_placed") # FIX: Changed from "ordered_by_user"
    items = relationship("CustomerOrderItem", back_populates="customer_order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CustomerOrder(id={self.id}, customer_org_id={self.customer_organization_id}, status='{self.status}')>"


class CustomerOrderItem(Base):
    """
    SQLAlchemy model for the 'customer_order_items' table.
    Details parts within a customer order.
    """
    __tablename__ = "customer_order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_order_id = Column(UUID(as_uuid=True), ForeignKey("customer_orders.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(DECIMAL(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer_order = relationship("CustomerOrder", back_populates="items")
    part = relationship("Part", back_populates="customer_order_items")

    def __repr__(self):
        return f"<CustomerOrderItem(id={self.id}, customer_order_id={self.customer_order_id}, part_id={self.part_id}, qty={self.quantity})>"


class PartUsage(Base):
    """
    SQLAlchemy model for the 'part_usage' table.
    Records when and which parts are consumed by customers.
    """
    __tablename__ = "part_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    usage_date = Column(DateTime(timezone=True), nullable=False)
    quantity_used = Column(Integer, nullable=False, default=1)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=True) # Updated: Foreign Key to machines.id
    recorded_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer_organization = relationship("Organization", back_populates="part_usage_records")
    part = relationship("Part", back_populates="part_usage_records")
    machine = relationship("Machine", back_populates="part_usage_records") # New: Relationship to Machine
    recorded_by_user = relationship("User", back_populates="part_usage_records")

    def __repr__(self):
        return f"<PartUsage(id={self.id}, customer_org_id={self.customer_organization_id}, part_id={self.part_id}, qty={self.quantity_used})>"

