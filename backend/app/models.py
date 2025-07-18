# backend/app/models.py

import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Text, ARRAY, DECIMAL, UniqueConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property

from .database import Base


# Enums for the new business model
class OrganizationType(enum.Enum):
    ORASEAS_EE = "oraseas_ee"
    BOSSAQUA = "bossaqua"
    CUSTOMER = "customer"
    SUPPLIER = "supplier"


class PartType(enum.Enum):
    CONSUMABLE = "consumable"
    BULK_MATERIAL = "bulk_material"


class UserRole(enum.Enum):
    user = "user"
    admin = "admin"
    super_admin = "super_admin"


class UserStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    pending_invitation = "pending_invitation"
    locked = "locked"


class TransactionType(enum.Enum):
    CREATION = "creation"
    TRANSFER = "transfer"
    CONSUMPTION = "consumption"
    ADJUSTMENT = "adjustment"


class StockAdjustmentReason(enum.Enum):
    STOCKTAKE_DISCREPANCY = "Stocktake Discrepancy"
    DAMAGED_GOODS = "Damaged Goods"
    FOUND_STOCK = "Found Stock"
    INITIAL_STOCK_ENTRY = "Initial Stock Entry"
    RETURN_TO_VENDOR = "Return to Vendor"
    CUSTOMER_RETURN_RESALABLE = "Customer Return - Resalable"
    CUSTOMER_RETURN_DAMAGED = "Customer Return - Damaged"
    OTHER = "Other"

class Organization(Base):
    """
    SQLAlchemy model for the 'organizations' table.
    Represents Oraseas EE and its customer organizations with proper business model hierarchy.
    """
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    organization_type = Column(Enum(OrganizationType), nullable=False)
    parent_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    address = Column(Text)
    contact_info = Column(Text)
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Self-referential relationship for organization hierarchy
    parent_organization = relationship("Organization", remote_side=[id], back_populates="child_organizations")
    child_organizations = relationship("Organization", back_populates="parent_organization", cascade="all, delete-orphan")

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    warehouses = relationship("Warehouse", back_populates="organization", cascade="all, delete-orphan")
    machines = relationship("Machine", foreign_keys="[Machine.customer_organization_id]", back_populates="customer_organization", cascade="all, delete-orphan")
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


    @hybrid_property
    def is_oraseas_ee(self):
        """Check if this organization is Oraseas EE."""
        return self.organization_type == OrganizationType.ORASEAS_EE

    @hybrid_property
    def is_customer(self):
        """Check if this organization is a customer."""
        return self.organization_type == OrganizationType.CUSTOMER

    @hybrid_property
    def is_supplier(self):
        """Check if this organization is a supplier."""
        return self.organization_type == OrganizationType.SUPPLIER

    @hybrid_property
    def is_bossaqua(self):
        """Check if this organization is BossAqua."""
        return self.organization_type == OrganizationType.BOSSAQUA

    def validate_business_rules(self):
        """Validate business rules for organization types."""
        if self.organization_type == OrganizationType.SUPPLIER and not self.parent_organization_id:
            raise ValueError("Supplier organizations must have a parent organization")
        
        # Additional validation can be added here
        return True

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', type='{self.organization_type.value}')>"


class User(Base):
    """
    SQLAlchemy model for the 'users' table.
    Enhanced with new authentication and security features.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    role = Column(ENUM(UserRole, name='userrole'), nullable=False)
    user_status = Column(ENUM(UserStatus, name='userstatus'), nullable=False, server_default='active')
    failed_login_attempts = Column(Integer, nullable=False, server_default='0')
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    invitation_token = Column(String(255), nullable=True)
    invitation_expires_at = Column(DateTime(timezone=True), nullable=True)
    invited_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires_at = Column(DateTime(timezone=True), nullable=True)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires_at = Column(DateTime(timezone=True), nullable=True)
    pending_email = Column(String(255), nullable=True)
    is_active = Column(Boolean, server_default='true', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    part_usage_records = relationship("PartUsage", back_populates="recorded_by_user")
    customer_orders_placed = relationship("CustomerOrder", back_populates="ordered_by_user")
    stock_adjustments = relationship("StockAdjustment", back_populates="user")
    transactions_performed = relationship("Transaction", back_populates="performed_by_user")
    invitation_audit_logs = relationship("InvitationAuditLog", foreign_keys="[InvitationAuditLog.user_id]", back_populates="user")
    invited_by_user = relationship("User", remote_side=[id])

    @hybrid_property
    def is_super_admin(self):
        """Check if this user is a super admin."""
        return self.role == UserRole.super_admin

    @hybrid_property
    def is_admin(self):
        """Check if this user is an admin."""
        return self.role == UserRole.admin

    @hybrid_property
    def is_locked(self):
        """Check if this user account is currently locked."""
        return self.user_status == UserStatus.locked or (
            self.locked_until and self.locked_until > func.now()
        )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}', organization_id={self.organization_id})>"


class Machine(Base):
    """
    SQLAlchemy model for the 'machines' table. (New!)
    Represents AutoBoss machines owned by customer organizations.
    """
    __tablename__ = "machines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    model_type = Column(String(100), nullable=False) # e.g., 'V3.1B', 'V4.0'
    name = Column(String(255), nullable=False)
    serial_number = Column(String(255), unique=True, nullable=False) # Unique across all machines
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer_organization = relationship("Organization", back_populates="machines")
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
    part_type = Column(Enum(PartType), nullable=False, server_default='consumable')
    is_proprietary = Column(Boolean, nullable=False, server_default='false')
    unit_of_measure = Column(String(50), nullable=False, server_default='pieces')
    manufacturer_part_number = Column(String(255), nullable=True)
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


class Warehouse(Base):
    """
    SQLAlchemy model for the 'warehouses' table.
    Represents physical storage locations within organizations.
    """
    __tablename__ = "warehouses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='_org_warehouse_name_uc'),
    )

    # Relationships
    organization = relationship("Organization", back_populates="warehouses")
    inventory_items = relationship("Inventory", back_populates="warehouse", cascade="all, delete-orphan")
    transactions_from = relationship("Transaction", foreign_keys="[Transaction.from_warehouse_id]", back_populates="from_warehouse")
    transactions_to = relationship("Transaction", foreign_keys="[Transaction.to_warehouse_id]", back_populates="to_warehouse")

    def __repr__(self):
        return f"<Warehouse(id={self.id}, name='{self.name}', organization_id={self.organization_id})>"


class Inventory(Base):
    """
    SQLAlchemy model for the 'inventory' table.
    Tracks part stock levels for each warehouse.
    """
    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    current_stock = Column(DECIMAL(precision=10, scale=3), nullable=False, server_default='0')
    minimum_stock_recommendation = Column(DECIMAL(precision=10, scale=3), nullable=False, server_default='0')
    unit_of_measure = Column(String(50), nullable=False)
    reorder_threshold_set_by = Column(String(50), nullable=True)
    last_recommendation_update = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('warehouse_id', 'part_id', name='_warehouse_part_uc'),
    )

    # Relationships
    warehouse = relationship("Warehouse", back_populates="inventory_items")
    part = relationship("Part", back_populates="inventory_items")
    adjustments = relationship("StockAdjustment", order_by="StockAdjustment.adjustment_date", back_populates="inventory_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Inventory(id={self.id}, warehouse_id={self.warehouse_id}, part_id={self.part_id}, stock={self.current_stock})>"


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
    quantity = Column(DECIMAL(precision=10, scale=3), nullable=False, server_default='1')
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
    quantity = Column(DECIMAL(precision=10, scale=3), nullable=False, server_default='1')
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
    quantity = Column(DECIMAL(precision=10, scale=3), nullable=False, server_default='1')
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=True)
    recorded_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer_organization = relationship("Organization", back_populates="part_usage_records")
    part = relationship("Part", back_populates="part_usage_records")
    machine = relationship("Machine", back_populates="part_usage_records")
    recorded_by_user = relationship("User", back_populates="part_usage_records")
    warehouse = relationship("Warehouse")

    def __repr__(self):
        return f"<PartUsage(id={self.id}, customer_org_id={self.customer_organization_id}, part_id={self.part_id}, qty={self.quantity})>"


class Transaction(Base):
    """
    SQLAlchemy model for the 'transactions' table.
    Records all parts movements for comprehensive audit trail.
    """
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    from_warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True)
    to_warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=True)
    quantity = Column(DECIMAL(precision=10, scale=3), nullable=False)
    unit_of_measure = Column(String(50), nullable=False)
    performed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    part = relationship("Part")
    from_warehouse = relationship("Warehouse", foreign_keys=[from_warehouse_id], back_populates="transactions_from")
    to_warehouse = relationship("Warehouse", foreign_keys=[to_warehouse_id], back_populates="transactions_to")
    machine = relationship("Machine")
    performed_by_user = relationship("User", back_populates="transactions_performed")

    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.transaction_type.value}', part_id={self.part_id}, qty={self.quantity})>"





class StockAdjustment(Base):
    """
    SQLAlchemy model for the 'stock_adjustments' table.
    Logs changes to inventory levels.
    """
    __tablename__ = "stock_adjustments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey("inventory.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False) # User who performed the adjustment
    adjustment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    quantity_adjusted = Column(DECIMAL(precision=10, scale=3), nullable=False) # Positive for increase, negative for decrease
    reason_code = Column(String(100), nullable=False) # From StockAdjustmentReason enum
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    inventory_item = relationship("Inventory", back_populates="adjustments")
    user = relationship("User", back_populates="stock_adjustments")

    def __repr__(self):
        return f"<StockAdjustment(id={self.id}, inventory_id={self.inventory_id}, qty_adj={self.quantity_adjusted}, reason='{self.reason_code}')>"


class InvitationAuditLog(Base):
    """
    SQLAlchemy model for the 'invitation_audit_logs' table.
    Tracks invitation-related actions for audit trail.
    """
    __tablename__ = "invitation_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # 'invited', 'resent', 'accepted', 'expired'
    performed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    details = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="invitation_audit_logs")
    performed_by_user = relationship("User", foreign_keys=[performed_by_user_id])

    def __repr__(self):
        return f"<InvitationAuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}')>"


class UserManagementAuditLog(Base):
    """
    SQLAlchemy model for the 'user_management_audit_logs' table.
    Tracks user management actions for comprehensive audit trail.
    """
    __tablename__ = "user_management_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # 'deactivated', 'reactivated', 'soft_deleted', 'role_changed', 'status_changed'
    performed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    details = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    performed_by_user = relationship("User", foreign_keys=[performed_by_user_id])

    def __repr__(self):
        return f"<UserManagementAuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}')>"


class SecurityEvent(Base):
    """
    SQLAlchemy model for the 'security_events' table.
    Tracks security-related events for monitoring and audit purposes.
    """
    __tablename__ = "security_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Nullable for failed login attempts
    event_type = Column(String(50), nullable=False)  # 'login_success', 'login_failed', 'account_locked', 'suspicious_activity', 'session_terminated'
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    risk_level = Column(String(20), nullable=False, server_default='low')  # 'low', 'medium', 'high', 'critical'

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, event_type='{self.event_type}', risk_level='{self.risk_level}')>"


class UserSession(Base):
    """
    SQLAlchemy model for the 'user_sessions' table.
    Tracks active user sessions for management and security purposes.
    """
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default='true')
    terminated_reason = Column(String(100), nullable=True)  # 'logout', 'timeout', 'admin_terminated', 'password_changed'

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    @hybrid_property
    def is_expired(self):
        """Check if this session is expired."""
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"

