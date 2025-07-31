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

# Import configuration models
from .models_config import SystemConfiguration, OrganizationConfiguration


# Enums for the new business model
class OrganizationType(enum.Enum):
    oraseas_ee = "oraseas_ee"
    bossaqua = "bossaqua"
    customer = "customer"
    supplier = "supplier"


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
    country = Column(String(3), nullable=True)  # Added country field with enum constraint
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
        return self.organization_type == OrganizationType.oraseas_ee

    @hybrid_property
    def is_customer(self):
        """Check if this organization is a customer."""
        return self.organization_type == OrganizationType.customer

    @hybrid_property
    def is_supplier(self):
        """Check if this organization is a supplier."""
        return self.organization_type == OrganizationType.supplier

    @hybrid_property
    def is_bossaqua(self):
        """Check if this organization is BossAqua."""
        return self.organization_type == OrganizationType.bossaqua

    def validate_business_rules(self):
        """Validate business rules for organization types."""
        if self.organization_type == OrganizationType.supplier and not self.parent_organization_id:
            raise ValueError("Supplier organizations must have a parent organization")
        
        # Additional validation can be added here
        return True

    def get_active_suppliers(self, db_session):
        """Get all active suppliers belonging to this organization."""
        from sqlalchemy.orm import Session
        if not isinstance(db_session, Session):
            raise ValueError("db_session must be a SQLAlchemy Session")
        
        return db_session.query(Organization)\
            .filter(
                Organization.organization_type == OrganizationType.supplier,
                Organization.parent_organization_id == self.id,
                Organization.is_active == True
            )\
            .order_by(Organization.name)\
            .all()

    def can_have_suppliers(self):
        """Check if this organization type can have supplier organizations."""
        return self.organization_type in [OrganizationType.customer, OrganizationType.oraseas_ee]

    def get_supplier_count(self, db_session, include_inactive=False):
        """Get count of suppliers belonging to this organization."""
        from sqlalchemy.orm import Session
        if not isinstance(db_session, Session):
            raise ValueError("db_session must be a SQLAlchemy Session")
        
        query = db_session.query(Organization)\
            .filter(
                Organization.organization_type == OrganizationType.supplier,
                Organization.parent_organization_id == self.id
            )
        
        if not include_inactive:
            query = query.filter(Organization.is_active == True)
        
        return query.count()

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
    user_status = Column(ENUM(UserStatus, name='userstatus'), nullable=False)
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
    preferred_language = Column(String(5), nullable=True, server_default='en')  # Language preference (en, el, ar, es)
    preferred_country = Column(String(3), nullable=True)  # Country preference (GR, KSA, ES, CY, OM)
    localization_preferences = Column(Text, nullable=True)  # JSON string for advanced preferences
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
    machine_hours_recorded = relationship("MachineHours", back_populates="recorded_by_user")

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


class MachineStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"
    decommissioned = "decommissioned"


class MachineModelType(enum.Enum):
    V3_1B = "V3.1B"
    V4_0 = "V4.0"

class Machine(Base):
    """
    SQLAlchemy model for the 'machines' table.
    Represents AutoBoss machines owned by customer organizations.
    Enhanced with model type validation and ownership transfer capabilities.
    """
    __tablename__ = "machines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    model_type = Column(ENUM(MachineModelType, name='machinemodeltype'), nullable=False)
    name = Column(String(255), nullable=False)
    serial_number = Column(String(255), unique=True, nullable=False) # Unique across all machines
    purchase_date = Column(DateTime(timezone=True), nullable=True)
    warranty_expiry_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(ENUM(MachineStatus, name='machinestatus'), nullable=False, server_default='active')
    last_maintenance_date = Column(DateTime(timezone=True), nullable=True)
    next_maintenance_date = Column(DateTime(timezone=True), nullable=True)
    location = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer_organization = relationship("Organization", back_populates="machines")
    part_usage_records = relationship("PartUsage", back_populates="machine", cascade="all, delete-orphan")
    maintenance_records = relationship("MachineMaintenance", back_populates="machine", cascade="all, delete-orphan")
    compatible_parts = relationship("MachinePartCompatibility", back_populates="machine", cascade="all, delete-orphan")
    predictions = relationship("MachinePrediction", back_populates="machine", cascade="all, delete-orphan")
    maintenance_recommendations = relationship("MaintenanceRecommendation", back_populates="machine", cascade="all, delete-orphan")
    machine_hours = relationship("MachineHours", back_populates="machine", cascade="all, delete-orphan")

    def validate_model_type(self):
        """Validate that the machine model type is supported."""
        if self.model_type not in [MachineModelType.V3_1B, MachineModelType.V4_0]:
            raise ValueError(f"Unsupported machine model type: {self.model_type}")
        return True

    def can_transfer_ownership(self, from_org, to_org):
        """
        Validate if machine ownership can be transferred between organizations.
        Machines can only be transferred from Oraseas EE to customer organizations.
        """
        if not from_org or not to_org:
            raise ValueError("Both source and destination organizations must be specified")
        
        # Check if transfer is from Oraseas EE to customer
        if from_org.organization_type != OrganizationType.oraseas_ee:
            raise ValueError("Machines can only be transferred from Oraseas EE")
        
        if to_org.organization_type != OrganizationType.customer:
            raise ValueError("Machines can only be transferred to customer organizations")
        
        # Check if machine currently belongs to the source organization
        if self.customer_organization_id != from_org.id:
            raise ValueError("Machine does not belong to the source organization")
        
        return True

    def transfer_ownership(self, to_organization_id, performed_by_user_id, db_session):
        """
        Transfer machine ownership to another organization.
        This creates a transaction record and updates the machine's organization.
        """
        from sqlalchemy.orm import Session
        if not isinstance(db_session, Session):
            raise ValueError("db_session must be a SQLAlchemy Session")
        
        # Get the current and target organizations
        current_org = db_session.query(Organization).filter(Organization.id == self.customer_organization_id).first()
        target_org = db_session.query(Organization).filter(Organization.id == to_organization_id).first()
        
        if not current_org or not target_org:
            raise ValueError("Invalid organization IDs provided")
        
        # Validate the transfer
        self.can_transfer_ownership(current_org, target_org)
        
        # Update the machine's organization
        old_org_id = self.customer_organization_id
        self.customer_organization_id = to_organization_id
        self.updated_at = func.now()
        
        # Create a transaction record for the ownership transfer
        # Note: This would typically create a MachineTransfer record, but since we don't have that model yet,
        # we'll add a note to the machine for now
        transfer_note = f"Ownership transferred from {current_org.name} to {target_org.name} on {datetime.now().isoformat()}"
        if self.notes:
            self.notes += f"\n{transfer_note}"
        else:
            self.notes = transfer_note
        
        return True

    def can_edit_name(self, user, requesting_org):
        """
        Check if a user can edit the machine name.
        Superadmins can edit any machine name.
        Admins can only edit machine names within their own organization.
        """
        if not user or not requesting_org:
            raise ValueError("User and organization must be specified")
        
        # Superadmins can edit any machine name
        if user.role == UserRole.super_admin:
            return True
        
        # Admins can only edit machines in their own organization
        if user.role == UserRole.admin and self.customer_organization_id == requesting_org.id:
            return True
        
        return False

    def update_name(self, new_name, user, requesting_org):
        """
        Update the machine name with proper authorization checks.
        """
        if not self.can_edit_name(user, requesting_org):
            raise ValueError("User does not have permission to edit this machine name")
        
        if not new_name or not new_name.strip():
            raise ValueError("Machine name cannot be empty")
        
        old_name = self.name
        self.name = new_name.strip()
        self.updated_at = func.now()
        
        # Add a note about the name change
        name_change_note = f"Name changed from '{old_name}' to '{new_name}' by {user.username} on {datetime.now().isoformat()}"
        if self.notes:
            self.notes += f"\n{name_change_note}"
        else:
            self.notes = name_change_note
        
        return True

    def get_latest_hours(self, db_session):
        """Get the latest recorded hours for this machine."""
        from sqlalchemy.orm import Session
        if not isinstance(db_session, Session):
            raise ValueError("db_session must be a SQLAlchemy Session")
        
        latest_record = db_session.query(MachineHours)\
            .filter(MachineHours.machine_id == self.id)\
            .order_by(MachineHours.recorded_date.desc())\
            .first()
        
        return latest_record.hours_value if latest_record else 0

    def get_total_hours_recorded(self, db_session):
        """Get the total number of hours records for this machine."""
        from sqlalchemy.orm import Session
        if not isinstance(db_session, Session):
            raise ValueError("db_session must be a SQLAlchemy Session")
        
        return db_session.query(MachineHours)\
            .filter(MachineHours.machine_id == self.id)\
            .count()

    def __repr__(self):
        return f"<Machine(id={self.id}, name='{self.name}', model_type='{self.model_type.value}', serial_number='{self.serial_number}')>"


class MachineHours(Base):
    """
    SQLAlchemy model for the 'machine_hours' table.
    Records machine hours for service timing calculations.
    Enhanced with user tracking and validation.
    """
    __tablename__ = "machine_hours"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    recorded_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    hours_value = Column(DECIMAL(precision=10, scale=2), nullable=False)
    recorded_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    machine = relationship("Machine", back_populates="machine_hours")
    recorded_by_user = relationship("User", back_populates="machine_hours_recorded")

    def validate_hours_value(self):
        """Validate that the hours value is positive and reasonable."""
        if self.hours_value is None:
            raise ValueError("Hours value cannot be None")
        
        if self.hours_value < 0:
            raise ValueError("Hours value cannot be negative")
        
        if self.hours_value > 99999:  # Reasonable upper limit
            raise ValueError("Hours value seems unreasonably high (max 99,999)")
        
        return True

    def validate_recorded_date(self):
        """Validate that the recorded date is not in the future."""
        if self.recorded_date is None:
            raise ValueError("Recorded date cannot be None")
        
        if self.recorded_date > datetime.now():
            raise ValueError("Recorded date cannot be in the future")
        
        return True

    def can_record_hours(self, user, machine, db_session):
        """
        Check if a user can record hours for a specific machine.
        Users can only record hours for machines in their own organization.
        Superadmins can record hours for any machine.
        """
        from sqlalchemy.orm import Session
        if not isinstance(db_session, Session):
            raise ValueError("db_session must be a SQLAlchemy Session")
        
        if not user or not machine:
            raise ValueError("User and machine must be specified")
        
        # Superadmins can record hours for any machine
        if user.role == UserRole.super_admin:
            return True
        
        # Regular users and admins can only record hours for machines in their organization
        if user.organization_id == machine.customer_organization_id:
            return True
        
        return False

    def validate_against_previous_records(self, db_session):
        """
        Validate that this hours record is logical compared to previous records.
        Hours should generally increase over time.
        """
        from sqlalchemy.orm import Session
        if not isinstance(db_session, Session):
            raise ValueError("db_session must be a SQLAlchemy Session")
        
        # Get the most recent hours record for this machine before this date
        previous_record = db_session.query(MachineHours)\
            .filter(
                MachineHours.machine_id == self.machine_id,
                MachineHours.recorded_date < self.recorded_date,
                MachineHours.id != self.id  # Exclude this record if it's an update
            )\
            .order_by(MachineHours.recorded_date.desc())\
            .first()
        
        if previous_record:
            if self.hours_value < previous_record.hours_value:
                # Allow for reasonable decreases (e.g., machine reset, maintenance)
                decrease = previous_record.hours_value - self.hours_value
                if decrease > 100:  # More than 100 hours decrease might be suspicious
                    raise ValueError(f"Hours value ({self.hours_value}) is significantly lower than previous record ({previous_record.hours_value}). Please add a note explaining the decrease.")
        
        return True

    def get_hours_since_last_service(self, db_session):
        """Calculate hours accumulated since the last maintenance."""
        from sqlalchemy.orm import Session
        if not isinstance(db_session, Session):
            raise ValueError("db_session must be a SQLAlchemy Session")
        
        machine = db_session.query(Machine).filter(Machine.id == self.machine_id).first()
        if not machine or not machine.last_maintenance_date:
            return self.hours_value  # No maintenance recorded, return total hours
        
        # Get hours recorded at or after last maintenance
        hours_since_maintenance = db_session.query(MachineHours)\
            .filter(
                MachineHours.machine_id == self.machine_id,
                MachineHours.recorded_date >= machine.last_maintenance_date
            )\
            .order_by(MachineHours.recorded_date.desc())\
            .first()
        
        if hours_since_maintenance:
            # Get hours at maintenance time
            maintenance_hours = db_session.query(MachineHours)\
                .filter(
                    MachineHours.machine_id == self.machine_id,
                    MachineHours.recorded_date <= machine.last_maintenance_date
                )\
                .order_by(MachineHours.recorded_date.desc())\
                .first()
            
            if maintenance_hours:
                return hours_since_maintenance.hours_value - maintenance_hours.hours_value
        
        return 0

    def __repr__(self):
        return f"<MachineHours(id={self.id}, machine_id={self.machine_id}, hours={self.hours_value}, date={self.recorded_date})>"


class Part(Base):
    """
    SQLAlchemy model for the 'parts' table.
    """
    __tablename__ = "parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_number = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(Text, nullable=False)  # Updated to support longer multilingual strings
    description = Column(Text)
    part_type = Column(Enum(PartType, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    is_proprietary = Column(Boolean, nullable=False, server_default='false')
    unit_of_measure = Column(String(50), nullable=False, server_default='pieces')
    manufacturer = Column(String(255), nullable=True)  # Added manufacturer field
    part_code = Column(String(100), nullable=True)  # Added part_code field
    serial_number = Column(String(255), nullable=True)  # Added serial_number field
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
    transaction_type = Column(String(50), nullable=False)
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
    approvals = relationship("TransactionApproval", back_populates="transaction", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.transaction_type.value}', part_id={self.part_id}, qty={self.quantity})>"


class TransactionApprovalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TransactionApproval(Base):
    """
    SQLAlchemy model for the 'transaction_approvals' table.
    Records approvals for transactions that require approval.
    """
    __tablename__ = "transaction_approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)
    approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(TransactionApprovalStatus), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="approvals")
    approver = relationship("User")

    def __repr__(self):
        return f"<TransactionApproval(id={self.id}, transaction_id={self.transaction_id}, status='{self.status.value}')>"





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

class MaintenanceType(enum.Enum):
    scheduled = "scheduled"
    unscheduled = "unscheduled"
    repair = "repair"
    inspection = "inspection"
    cleaning = "cleaning"
    calibration = "calibration"
    other = "other"

class MachineMaintenance(Base):
    """
    SQLAlchemy model for the 'machine_maintenance' table.
    Records maintenance activities performed on machines.
    """
    __tablename__ = "machine_maintenance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    maintenance_date = Column(DateTime(timezone=True), nullable=False)
    maintenance_type = Column(Enum(MaintenanceType, name='maintenancetype'), nullable=False)
    performed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=False)
    hours_spent = Column(DECIMAL(precision=5, scale=2), nullable=True)
    cost = Column(DECIMAL(precision=10, scale=2), nullable=True)
    next_maintenance_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    machine = relationship("Machine", back_populates="maintenance_records")
    performed_by_user = relationship("User")
    parts_used = relationship("MaintenancePartUsage", back_populates="maintenance_record", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MachineMaintenance(id={self.id}, machine_id={self.machine_id}, type='{self.maintenance_type.value}')>"

class MaintenancePartUsage(Base):
    """
    SQLAlchemy model for the 'maintenance_part_usage' table.
    Records parts used during maintenance activities.
    """
    __tablename__ = "maintenance_part_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maintenance_id = Column(UUID(as_uuid=True), ForeignKey("machine_maintenance.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    quantity = Column(DECIMAL(precision=10, scale=3), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    maintenance_record = relationship("MachineMaintenance", back_populates="parts_used")
    part = relationship("Part")
    warehouse = relationship("Warehouse")

    def __repr__(self):
        return f"<MaintenancePartUsage(id={self.id}, maintenance_id={self.maintenance_id}, part_id={self.part_id}, qty={self.quantity})>"

class MachinePartCompatibility(Base):
    """
    SQLAlchemy model for the 'machine_part_compatibility' table.
    Records which parts are compatible with which machines.
    """
    __tablename__ = "machine_part_compatibility"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    is_recommended = Column(Boolean, nullable=False, server_default='false')
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('machine_id', 'part_id', name='_machine_part_uc'),
    )

    # Relationships
    machine = relationship("Machine", back_populates="compatible_parts")
    part = relationship("Part")

    def __repr__(self):
        return f"<MachinePartCompatibility(id={self.id}, machine_id={self.machine_id}, part_id={self.part_id})>"
# Predictive Maintenance Models
class MaintenanceRiskLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MaintenancePriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class MaintenanceStatus(enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PredictiveMaintenanceModel(Base):
    """
    SQLAlchemy model for the 'predictive_maintenance_models' table.
    Represents machine learning models for predictive maintenance.
    """
    __tablename__ = "predictive_maintenance_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    model_type = Column(String(100), nullable=False)  # e.g., 'regression', 'classification', 'time_series'
    target_metric = Column(String(100), nullable=False)  # e.g., 'failure_probability', 'remaining_useful_life'
    features = Column(Text, nullable=False)  # JSON array of feature names used by the model
    hyperparameters = Column(Text, nullable=True)  # JSON object of model hyperparameters
    performance_metrics = Column(Text, nullable=True)  # JSON object of model performance metrics
    version = Column(String(50), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    created_by_user = relationship("User")

    def __repr__(self):
        return f"<PredictiveMaintenanceModel(id={self.id}, name='{self.name}', version='{self.version}')>"

class MachinePrediction(Base):
    """
    SQLAlchemy model for the 'machine_predictions' table.
    Stores predictions made by predictive maintenance models for specific machines.
    """
    __tablename__ = "machine_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    predictive_model_id = Column(UUID(as_uuid=True), ForeignKey("predictive_maintenance_models.id"), nullable=False)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    failure_probability = Column(DECIMAL(precision=5, scale=4), nullable=True)
    remaining_useful_life = Column(Integer, nullable=True)  # in days
    predicted_failure_date = Column(DateTime(timezone=True), nullable=True)
    risk_level = Column(Enum(MaintenanceRiskLevel), nullable=False)
    prediction_details = Column(Text, nullable=True)  # JSON object with detailed prediction information
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    machine = relationship("Machine", back_populates="predictions")
    predictive_model = relationship("PredictiveMaintenanceModel")

    def __repr__(self):
        return f"<MachinePrediction(id={self.id}, machine_id={self.machine_id}, risk_level='{self.risk_level.value}')>"

class MaintenanceRecommendation(Base):
    """
    SQLAlchemy model for the 'maintenance_recommendations' table.
    Stores maintenance recommendations based on predictive model outputs.
    """
    __tablename__ = "maintenance_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("machine_predictions.id"), nullable=False)
    recommendation_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    recommended_maintenance_type = Column(String(50), nullable=False)  # Will store maintenance type as string
    priority = Column(Enum(MaintenancePriority), nullable=False)
    recommended_completion_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(MaintenanceStatus), nullable=False)
    resolved_by_maintenance_id = Column(UUID(as_uuid=True), ForeignKey("machine_maintenance.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    machine = relationship("Machine", back_populates="maintenance_recommendations")
    prediction = relationship("MachinePrediction")
    resolved_by_maintenance = relationship("MachineMaintenance")

    def __repr__(self):
        return f"<MaintenanceRecommendation(id={self.id}, machine_id={self.machine_id}, priority='{self.priority.value}')>"

# Part Order Models
class OrderStatus(enum.Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    ORDERED = "ordered"
    SHIPPED = "shipped"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class SupplierType(enum.Enum):
    ORASEAS_EE = "oraseas_ee"
    EXTERNAL_SUPPLIER = "external_supplier"

class OrderPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class PartOrderRequest(Base):
    """
    SQLAlchemy model for the 'part_order_requests' table.
    Represents part order requests from customers.
    """
    __tablename__ = "part_order_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    supplier_type = Column(Enum(SupplierType), nullable=False)
    supplier_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    supplier_name = Column(String(255), nullable=True)
    status = Column(Enum(OrderStatus), nullable=False)
    priority = Column(Enum(OrderPriority), nullable=False)
    requested_delivery_date = Column(DateTime(timezone=True), nullable=True)
    expected_delivery_date = Column(DateTime(timezone=True), nullable=True)
    actual_delivery_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    fulfillment_notes = Column(Text, nullable=True)
    requested_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    received_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer_organization = relationship("Organization", foreign_keys=[customer_organization_id])
    supplier_organization = relationship("Organization", foreign_keys=[supplier_organization_id])
    requested_by_user = relationship("User", foreign_keys=[requested_by_user_id])
    approved_by_user = relationship("User", foreign_keys=[approved_by_user_id])
    received_by_user = relationship("User", foreign_keys=[received_by_user_id])

    def __repr__(self):
        return f"<PartOrderRequest(id={self.id}, order_number='{self.order_number}', status='{self.status.value}')>"

class PartOrderItem(Base):
    """
    SQLAlchemy model for the 'part_order_items' table.
    Represents individual items within a part order request.
    """
    __tablename__ = "part_order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_request_id = Column(UUID(as_uuid=True), ForeignKey("part_order_requests.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    quantity = Column(DECIMAL(precision=10, scale=3), nullable=False)
    unit_price = Column(DECIMAL(precision=10, scale=2), nullable=True)
    destination_warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    received_quantity = Column(DECIMAL(precision=10, scale=3), nullable=True, server_default='0')
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    order_request = relationship("PartOrderRequest")
    part = relationship("Part")
    destination_warehouse = relationship("Warehouse")

    def __repr__(self):
        return f"<PartOrderItem(id={self.id}, order_request_id={self.order_request_id}, part_id={self.part_id}, quantity={self.quantity})>"


# Machine Sale Models
class MachineSale(Base):
    """
    SQLAlchemy model for the 'machine_sales' table.
    Records machine ownership transfers from Oraseas EE to customers.
    """
    __tablename__ = "machine_sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    from_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    to_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    sale_price = Column(DECIMAL(precision=10, scale=2), nullable=True)
    sale_date = Column(DateTime(timezone=True), nullable=False)
    performed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    machine = relationship("Machine")
    from_organization = relationship("Organization", foreign_keys=[from_organization_id])
    to_organization = relationship("Organization", foreign_keys=[to_organization_id])
    performed_by_user = relationship("User")

    def __repr__(self):
        return f"<MachineSale(id={self.id}, machine_id={self.machine_id}, from_org={self.from_organization_id}, to_org={self.to_organization_id})>"


# Enhanced Part Usage Models
class PartUsageRecord(Base):
    """
    SQLAlchemy model for the 'part_usage_records' table.
    Records part usage in machines with detailed tracking.
    """
    __tablename__ = "part_usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    from_warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    usage_date = Column(DateTime(timezone=True), nullable=False)
    performed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    service_type = Column(String(50), nullable=True)  # e.g., '50h', '250h', 'repair'
    machine_hours = Column(DECIMAL(precision=10, scale=2), nullable=True)
    notes = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    machine = relationship("Machine")
    from_warehouse = relationship("Warehouse")
    performed_by_user = relationship("User")
    usage_items = relationship("PartUsageItem", back_populates="usage_record", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PartUsageRecord(id={self.id}, machine_id={self.machine_id}, usage_date={self.usage_date})>"


class PartUsageItem(Base):
    """
    SQLAlchemy model for the 'part_usage_items' table.
    Individual parts used in a part usage record.
    """
    __tablename__ = "part_usage_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usage_record_id = Column(UUID(as_uuid=True), ForeignKey("part_usage_records.id"), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    quantity = Column(DECIMAL(precision=10, scale=3), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    usage_record = relationship("PartUsageRecord", back_populates="usage_items")
    part = relationship("Part")

    def __repr__(self):
        return f"<PartUsageItem(id={self.id}, usage_record_id={self.usage_record_id}, part_id={self.part_id}, quantity={self.quantity})>"