"""
Load testing script for ABParts using Locust.
Tests system performance under various load conditions.
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from locust import HttpUser, task, between


class AdminUser(HttpUser):
    """Simulates an admin user with authentication."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Log in when the user starts."""
        response = self.client.post("/token", data={
            "username": "oraseas_admin",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.environment.runner.quit()
    
    @task(3)
    def view_dashboard(self):
        """View dashboard summary."""
        self.client.get("/dashboard/summary", headers=self.headers)
    
    @task(5)
    def view_inventory(self):
        """View inventory listing."""
        self.client.get("/inventory/", headers=self.headers)
    
    @task(2)
    def view_transactions(self):
        """View recent transactions."""
        self.client.get("/transactions/", headers=self.headers)
    
    @task(1)
    def create_transaction(self):
        """Create a new transaction."""
        # Get parts and warehouses first
        parts_response = self.client.get("/parts/", headers=self.headers)
        warehouses_response = self.client.get("/warehouses/", headers=self.headers)
        
        if parts_response.status_code != 200 or warehouses_response.status_code != 200:
            return
        
        parts = parts_response.json()
        warehouses = warehouses_response.json()
        
        if not parts or not warehouses:
            return
        
        # Select random part and warehouses
        part = random.choice(parts)
        from_warehouse = random.choice(warehouses)
        to_warehouse = random.choice([w for w in warehouses if w["id"] != from_warehouse["id"]])
        
        # Create transaction
        transaction_data = {
            "transaction_type": "transfer",
            "part_id": part["id"],
            "from_warehouse_id": from_warehouse["id"],
            "to_warehouse_id": to_warehouse["id"],
            "quantity": str(random.randint(1, 10)),
            "unit_of_measure": part.get("unit_of_measure", "pieces"),
            "transaction_date": datetime.utcnow().isoformat(),
            "notes": "Load test transaction"
        }
        
        self.client.post("/transactions/", json=transaction_data, headers=self.headers)


class CustomerUser(HttpUser):
    """Simulates a customer user with authentication."""
    
    wait_time = between(2, 5)  # Wait 2-5 seconds between tasks
    
    def on_start(self):
        """Log in when the user starts."""
        response = self.client.post("/token", data={
            "username": "customer_user",
            "password": "user123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            
            # Get user's organization and machines
            user_response = self.client.get("/users/me/", headers=self.headers)
            if user_response.status_code == 200:
                self.user = user_response.json()
                
                # Get machines
                machines_response = self.client.get("/machines/", headers=self.headers)
                if machines_response.status_code == 200:
                    self.machines = machines_response.json()
                else:
                    self.machines = []
                
                # Get warehouses
                warehouses_response = self.client.get("/warehouses/", headers=self.headers)
                if warehouses_response.status_code == 200:
                    self.warehouses = warehouses_response.json()
                else:
                    self.warehouses = []
        else:
            self.environment.runner.quit()
    
    @task(5)
    def view_inventory(self):
        """View inventory listing."""
        self.client.get("/inventory/", headers=self.headers)
    
    @task(3)
    def view_machines(self):
        """View machines listing."""
        self.client.get("/machines/", headers=self.headers)
    
    @task(2)
    def view_machine_details(self):
        """View details of a specific machine."""
        if hasattr(self, "machines") and self.machines:
            machine = random.choice(self.machines)
            self.client.get(f"/machines/{machine['id']}", headers=self.headers)
    
    @task(1)
    def record_part_usage(self):
        """Record part usage for a machine."""
        if not hasattr(self, "machines") or not self.machines or not hasattr(self, "warehouses") or not self.warehouses:
            return
        
        # Get parts first
        parts_response = self.client.get("/parts/", headers=self.headers)
        if parts_response.status_code != 200:
            return
        
        parts = parts_response.json()
        if not parts:
            return
        
        # Select random machine, part, and warehouse
        machine = random.choice(self.machines)
        part = random.choice(parts)
        warehouse = random.choice(self.warehouses)
        
        # Record part usage
        usage_data = {
            "part_id": part["id"],
            "machine_id": machine["id"],
            "quantity": str(random.randint(1, 5)),
            "usage_date": datetime.utcnow().isoformat(),
            "warehouse_id": warehouse["id"],
            "notes": "Load test part usage"
        }
        
        self.client.post("/part_usage/", json=usage_data, headers=self.headers)


class AnonymousUser(HttpUser):
    """Simulates an unauthenticated user."""
    
    wait_time = between(1, 2)  # Wait 1-2 seconds between tasks
    
    @task(10)
    def health_check(self):
        """Check system health."""
        self.client.get("/health")
    
    @task(5)
    def monitoring_health(self):
        """Check monitoring health."""
        self.client.get("/monitoring/health")
    
    @task(1)
    def try_protected_endpoint(self):
        """Try to access a protected endpoint (should fail)."""
        self.client.get("/users/")
    
    @task(2)
    def view_api_docs(self):
        """View API documentation."""
        self.client.get("/docs")