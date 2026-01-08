"""
ABParts Integration Service

This service provides integration with the ABParts database to retrieve
machine context, maintenance history, and user preferences for the AI Assistant.
"""

import logging
import sys
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

# Add the backend directory to the Python path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from ..database import get_db_session
from ..config import settings

logger = logging.getLogger(__name__)


class ABPartsIntegration:
    """Service for integrating with ABParts database."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def get_machine_details(self, machine_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve detailed information about a specific machine.
        
        Args:
            machine_id: UUID of the machine
            
        Returns:
            Dictionary containing machine details or None if not found
        """
        try:
            with get_db_session() as db:
                # Import models here to avoid circular imports
                from app.models import Machine, Organization
                
                machine = db.query(Machine).filter(Machine.id == machine_id).first()
                if not machine:
                    self.logger.warning(f"Machine not found: {machine_id}")
                    return None
                
                # Get organization details
                organization = db.query(Organization).filter(
                    Organization.id == machine.customer_organization_id
                ).first()
                
                machine_data = {
                    "id": str(machine.id),
                    "name": machine.name,
                    "model_type": machine.model_type,
                    "serial_number": machine.serial_number,
                    "customer_organization": {
                        "id": str(organization.id) if organization else None,
                        "name": organization.name if organization else None,
                        "organization_type": organization.organization_type.value if organization else None,
                        "country": organization.country.value if organization and organization.country else None
                    },
                    "created_at": machine.created_at.isoformat() if machine.created_at else None,
                    "updated_at": machine.updated_at.isoformat() if machine.updated_at else None
                }
                
                # Get latest machine hours
                latest_hours = machine.get_latest_hours(db)
                machine_data["latest_hours"] = float(latest_hours) if latest_hours else 0
                
                # Get total hours records count
                total_records = machine.get_total_hours_recorded(db)
                machine_data["total_hours_records"] = total_records
                
                self.logger.info(f"Retrieved machine details for {machine_id}")
                return machine_data
                
        except Exception as e:
            self.logger.error(f"Error retrieving machine details for {machine_id}: {e}")
            return None
    
    async def get_maintenance_history(self, machine_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve maintenance history for a specific machine.
        
        Args:
            machine_id: UUID of the machine
            limit: Maximum number of records to return
            
        Returns:
            List of maintenance records
        """
        try:
            with get_db_session() as db:
                from app.models import MachineMaintenance, User, MaintenancePartUsage, Part
                
                maintenance_records = db.query(MachineMaintenance)\
                    .filter(MachineMaintenance.machine_id == machine_id)\
                    .order_by(desc(MachineMaintenance.maintenance_date))\
                    .limit(limit)\
                    .all()
                
                history = []
                for record in maintenance_records:
                    # Get user who performed maintenance
                    user = db.query(User).filter(User.id == record.performed_by_user_id).first()
                    
                    # Get parts used in this maintenance
                    parts_used = db.query(MaintenancePartUsage, Part)\
                        .join(Part, MaintenancePartUsage.part_id == Part.id)\
                        .filter(MaintenancePartUsage.maintenance_id == record.id)\
                        .all()
                    
                    parts_list = []
                    for part_usage, part in parts_used:
                        parts_list.append({
                            "part_id": str(part.id),
                            "part_name": part.name,
                            "part_number": part.part_number,
                            "quantity": float(part_usage.quantity),
                            "notes": part_usage.notes
                        })
                    
                    maintenance_data = {
                        "id": str(record.id),
                        "maintenance_date": record.maintenance_date.isoformat(),
                        "maintenance_type": record.maintenance_type.value,
                        "description": record.description,
                        "hours_spent": float(record.hours_spent) if record.hours_spent else None,
                        "cost": float(record.cost) if record.cost else None,
                        "next_maintenance_date": record.next_maintenance_date.isoformat() if record.next_maintenance_date else None,
                        "notes": record.notes,
                        "performed_by": {
                            "id": str(user.id) if user else None,
                            "name": user.name if user else None,
                            "username": user.username if user else None
                        },
                        "parts_used": parts_list,
                        "created_at": record.created_at.isoformat() if record.created_at else None
                    }
                    history.append(maintenance_data)
                
                self.logger.info(f"Retrieved {len(history)} maintenance records for machine {machine_id}")
                return history
                
        except Exception as e:
            self.logger.error(f"Error retrieving maintenance history for {machine_id}: {e}")
            return []
    
    async def get_parts_usage_data(self, machine_id: str, days: int = 90) -> List[Dict[str, Any]]:
        """
        Retrieve parts usage data for a specific machine.
        
        Args:
            machine_id: UUID of the machine
            days: Number of days to look back
            
        Returns:
            List of parts usage records
        """
        try:
            with get_db_session() as db:
                from app.models import PartUsage, Part, User, Warehouse
                
                cutoff_date = datetime.now() - timedelta(days=days)
                
                usage_records = db.query(PartUsage, Part, User, Warehouse)\
                    .join(Part, PartUsage.part_id == Part.id)\
                    .join(User, PartUsage.recorded_by_user_id == User.id)\
                    .join(Warehouse, PartUsage.warehouse_id == Warehouse.id)\
                    .filter(
                        PartUsage.machine_id == machine_id,
                        PartUsage.usage_date >= cutoff_date
                    )\
                    .order_by(desc(PartUsage.usage_date))\
                    .all()
                
                usage_data = []
                for usage, part, user, warehouse in usage_records:
                    usage_record = {
                        "id": str(usage.id),
                        "usage_date": usage.usage_date.isoformat(),
                        "quantity": float(usage.quantity),
                        "notes": usage.notes,
                        "part": {
                            "id": str(part.id),
                            "name": part.name,
                            "part_number": part.part_number,
                            "part_type": part.part_type.value,
                            "is_proprietary": part.is_proprietary
                        },
                        "recorded_by": {
                            "id": str(user.id),
                            "name": user.name,
                            "username": user.username
                        },
                        "warehouse": {
                            "id": str(warehouse.id),
                            "name": warehouse.name,
                            "location": warehouse.location
                        },
                        "created_at": usage.created_at.isoformat() if usage.created_at else None
                    }
                    usage_data.append(usage_record)
                
                self.logger.info(f"Retrieved {len(usage_data)} parts usage records for machine {machine_id}")
                return usage_data
                
        except Exception as e:
            self.logger.error(f"Error retrieving parts usage data for {machine_id}: {e}")
            return []
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user preferences including language settings.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Dictionary containing user preferences or None if not found
        """
        try:
            with get_db_session() as db:
                from app.models import User, Organization
                
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    self.logger.warning(f"User not found: {user_id}")
                    return None
                
                # Get organization details
                organization = db.query(Organization).filter(
                    Organization.id == user.organization_id
                ).first()
                
                preferences = {
                    "user_id": str(user.id),
                    "username": user.username,
                    "name": user.name,
                    "email": user.email,
                    "preferred_language": user.preferred_language or "en",
                    "role": user.role.value,
                    "organization": {
                        "id": str(organization.id) if organization else None,
                        "name": organization.name if organization else None,
                        "organization_type": organization.organization_type.value if organization else None,
                        "country": organization.country.value if organization and organization.country else None
                    },
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                
                self.logger.info(f"Retrieved user preferences for {user_id}")
                return preferences
                
        except Exception as e:
            self.logger.error(f"Error retrieving user preferences for {user_id}: {e}")
            return None
    
    async def get_user_machines(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all machines accessible to a user based on their organization.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of machines accessible to the user
        """
        try:
            with get_db_session() as db:
                from app.models import User, Machine, Organization
                
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    self.logger.warning(f"User not found: {user_id}")
                    return []
                
                # Get machines based on user's organization
                # Super admins can see all machines, others only their organization's machines
                if user.role.value == "super_admin":
                    machines = db.query(Machine).all()
                else:
                    machines = db.query(Machine)\
                        .filter(Machine.customer_organization_id == user.organization_id)\
                        .all()
                
                machines_data = []
                for machine in machines:
                    # Get organization details
                    organization = db.query(Organization).filter(
                        Organization.id == machine.customer_organization_id
                    ).first()
                    
                    # Get latest hours
                    latest_hours = machine.get_latest_hours(db)
                    
                    machine_data = {
                        "id": str(machine.id),
                        "name": machine.name,
                        "model_type": machine.model_type,
                        "serial_number": machine.serial_number,
                        "latest_hours": float(latest_hours) if latest_hours else 0,
                        "organization": {
                            "id": str(organization.id) if organization else None,
                            "name": organization.name if organization else None
                        },
                        "created_at": machine.created_at.isoformat() if machine.created_at else None
                    }
                    machines_data.append(machine_data)
                
                self.logger.info(f"Retrieved {len(machines_data)} machines for user {user_id}")
                return machines_data
                
        except Exception as e:
            self.logger.error(f"Error retrieving machines for user {user_id}: {e}")
            return []
    
    async def get_machine_hours_history(self, machine_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve machine hours history for trend analysis.
        
        Args:
            machine_id: UUID of the machine
            limit: Maximum number of records to return
            
        Returns:
            List of machine hours records
        """
        try:
            with get_db_session() as db:
                from app.models import MachineHours, User
                
                hours_records = db.query(MachineHours)\
                    .filter(MachineHours.machine_id == machine_id)\
                    .order_by(desc(MachineHours.recorded_date))\
                    .limit(limit)\
                    .all()
                
                hours_data = []
                for record in hours_records:
                    # Get user who recorded the hours
                    user = db.query(User).filter(User.id == record.recorded_by_user_id).first()
                    
                    hours_record = {
                        "id": str(record.id),
                        "hours_value": float(record.hours_value),
                        "recorded_date": record.recorded_date.isoformat(),
                        "notes": record.notes,
                        "recorded_by": {
                            "id": str(user.id) if user else None,
                            "name": user.name if user else None,
                            "username": user.username if user else None
                        },
                        "created_at": record.created_at.isoformat() if record.created_at else None
                    }
                    hours_data.append(hours_record)
                
                self.logger.info(f"Retrieved {len(hours_data)} hours records for machine {machine_id}")
                return hours_data
                
        except Exception as e:
            self.logger.error(f"Error retrieving machine hours history for {machine_id}: {e}")
            return []
    
    async def get_preventive_maintenance_suggestions(self, machine_id: str) -> List[Dict[str, Any]]:
        """
        Generate preventive maintenance suggestions based on machine usage patterns.
        
        Args:
            machine_id: UUID of the machine
            
        Returns:
            List of maintenance suggestions
        """
        try:
            machine_details = await self.get_machine_details(machine_id)
            if not machine_details:
                return []
            
            maintenance_history = await self.get_maintenance_history(machine_id, limit=5)
            hours_history = await self.get_machine_hours_history(machine_id, limit=10)
            
            suggestions = []
            current_hours = machine_details.get("latest_hours", 0)
            
            # Basic maintenance interval suggestions based on AutoBoss standards
            maintenance_intervals = {
                "50h": {"hours": 50, "description": "Basic cleaning and inspection"},
                "250h": {"hours": 250, "description": "Comprehensive service and part replacement"},
                "500h": {"hours": 500, "description": "Major service and system check"},
                "1000h": {"hours": 1000, "description": "Complete overhaul and inspection"}
            }
            
            # Find the last maintenance for each type
            last_maintenance_hours = {}
            for record in maintenance_history:
                maintenance_type = record.get("maintenance_type", "")
                if maintenance_type not in last_maintenance_hours:
                    # Estimate hours at maintenance time (simplified)
                    last_maintenance_hours[maintenance_type] = current_hours - 100  # Rough estimate
            
            # Generate suggestions based on intervals
            for interval_name, interval_data in maintenance_intervals.items():
                interval_hours = interval_data["hours"]
                description = interval_data["description"]
                
                # Calculate hours since last maintenance of this type
                last_hours = last_maintenance_hours.get(interval_name, 0)
                hours_since_last = current_hours - last_hours
                
                if hours_since_last >= interval_hours:
                    priority = "high" if hours_since_last > interval_hours * 1.2 else "medium"
                    suggestions.append({
                        "type": interval_name,
                        "description": description,
                        "priority": priority,
                        "current_hours": current_hours,
                        "hours_since_last": hours_since_last,
                        "recommended_hours": interval_hours,
                        "overdue_hours": max(0, hours_since_last - interval_hours)
                    })
            
            # Sort by priority and overdue hours
            priority_order = {"high": 3, "medium": 2, "low": 1}
            suggestions.sort(key=lambda x: (priority_order.get(x["priority"], 0), x["overdue_hours"]), reverse=True)
            
            self.logger.info(f"Generated {len(suggestions)} maintenance suggestions for machine {machine_id}")
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Error generating maintenance suggestions for {machine_id}: {e}")
            return []


# Global instance
abparts_integration = ABPartsIntegration()