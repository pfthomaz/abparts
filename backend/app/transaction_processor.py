# backend/app/transaction_processor.py

import uuid
import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException

from . import models, schemas, crud

logger = logging.getLogger(__name__)

class TransactionProcessor:
    """
    Handles automated transaction processing, including inventory updates,
    transaction batching, approval workflows, and analytics.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def process_transaction(self, transaction: schemas.TransactionCreate) -> models.Transaction:
        """
        Process a single transaction, including validation and inventory updates.
        """
        try:
            # Validate transaction data
            self._validate_transaction(transaction)
            
            # Check if transaction requires approval
            requires_approval = self._requires_approval(transaction)
            
            # Create the transaction
            db_transaction = models.Transaction(**transaction.dict())
            db_transaction.requires_approval = requires_approval
            
            # Set approval status if required
            if requires_approval:
                db_transaction.approval_status = 'pending'
                self.db.add(db_transaction)
                self.db.commit()
                self.db.refresh(db_transaction)
                
                # Log that transaction requires approval
                logger.info(f"Transaction {db_transaction.id} requires approval and is pending")
                
                return db_transaction
            else:
                # If no approval required, process immediately
                self.db.add(db_transaction)
                
                # Update inventory based on transaction type
                self._update_inventory(db_transaction)
                
                # Commit the transaction
                self.db.commit()
                self.db.refresh(db_transaction)
                
                # Log the transaction
                logger.info(f"Transaction {db_transaction.id} processed successfully")
                
                return db_transaction
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing transaction: {e}")
            raise HTTPException(status_code=400, detail=f"Error processing transaction: {str(e)}")
    
    def process_transaction_batch(self, transactions: List[schemas.TransactionCreate]) -> List[models.Transaction]:
        """
        Process a batch of transactions in a single database transaction.
        """
        try:
            # Validate all transactions first
            for transaction in transactions:
                self._validate_transaction(transaction)
            
            # Create and process all transactions
            db_transactions = []
            transactions_requiring_approval = []
            transactions_for_immediate_processing = []
            
            # First pass: create all transaction records and check which ones need approval
            for transaction in transactions:
                requires_approval = self._requires_approval(transaction)
                
                db_transaction = models.Transaction(**transaction.dict())
                db_transaction.requires_approval = requires_approval
                
                if requires_approval:
                    db_transaction.approval_status = 'pending'
                    transactions_requiring_approval.append(db_transaction)
                else:
                    transactions_for_immediate_processing.append(db_transaction)
                
                self.db.add(db_transaction)
                db_transactions.append(db_transaction)
            
            # Flush to get IDs assigned
            self.db.flush()
            
            # Second pass: update inventory only for transactions that don't require approval
            for db_transaction in transactions_for_immediate_processing:
                self._update_inventory(db_transaction)
            
            # Commit all transactions
            self.db.commit()
            
            # Refresh all transactions
            for db_transaction in db_transactions:
                self.db.refresh(db_transaction)
            
            # Log the batch processing
            logger.info(f"Batch of {len(db_transactions)} transactions processed successfully")
            if transactions_requiring_approval:
                logger.info(f"{len(transactions_requiring_approval)} transactions require approval")
            
            return db_transactions
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing transaction batch: {e}")
            raise HTTPException(status_code=400, detail=f"Error processing transaction batch: {str(e)}")
    
    def _validate_transaction(self, transaction: schemas.TransactionCreate):
        """
        Validate transaction data based on transaction type and business rules.
        """
        # Validate based on transaction type
        if transaction.transaction_type == schemas.TransactionTypeEnum.CREATION:
            # Creation requires to_warehouse_id
            if not transaction.to_warehouse_id:
                raise ValueError("Creation transaction requires to_warehouse_id")
            # Creation should not have from_warehouse_id
            if transaction.from_warehouse_id:
                raise ValueError("Creation transaction should not have from_warehouse_id")
        
        elif transaction.transaction_type == schemas.TransactionTypeEnum.TRANSFER:
            # Transfer requires both from_warehouse_id and to_warehouse_id
            if not transaction.from_warehouse_id or not transaction.to_warehouse_id:
                raise ValueError("Transfer transaction requires both from_warehouse_id and to_warehouse_id")
            # Transfer should not have machine_id
            if transaction.machine_id:
                raise ValueError("Transfer transaction should not have machine_id")
            # From and to warehouses should be different
            if transaction.from_warehouse_id == transaction.to_warehouse_id:
                raise ValueError("Transfer transaction cannot have the same from_warehouse_id and to_warehouse_id")
        
        elif transaction.transaction_type == schemas.TransactionTypeEnum.CONSUMPTION:
            # Consumption requires from_warehouse_id
            if not transaction.from_warehouse_id:
                raise ValueError("Consumption transaction requires from_warehouse_id")
            # Consumption should not have to_warehouse_id
            if transaction.to_warehouse_id:
                raise ValueError("Consumption transaction should not have to_warehouse_id")
        
        elif transaction.transaction_type == schemas.TransactionTypeEnum.ADJUSTMENT:
            # Adjustment requires from_warehouse_id
            if not transaction.from_warehouse_id:
                raise ValueError("Adjustment transaction requires from_warehouse_id")
            # Adjustment should not have to_warehouse_id or machine_id
            if transaction.to_warehouse_id:
                raise ValueError("Adjustment transaction should not have to_warehouse_id")
            if transaction.machine_id:
                raise ValueError("Adjustment transaction should not have machine_id")
        
        # Quantity must be positive
        if transaction.quantity <= 0:
            raise ValueError("Transaction quantity must be positive")
        
        # Validate that part exists
        part = self.db.query(models.Part).filter(models.Part.id == transaction.part_id).first()
        if not part:
            raise ValueError(f"Part {transaction.part_id} not found")
        
        # Validate that warehouses exist
        if transaction.from_warehouse_id:
            from_warehouse = self.db.query(models.Warehouse).filter(models.Warehouse.id == transaction.from_warehouse_id).first()
            if not from_warehouse:
                raise ValueError(f"From warehouse {transaction.from_warehouse_id} not found")
        
        if transaction.to_warehouse_id:
            to_warehouse = self.db.query(models.Warehouse).filter(models.Warehouse.id == transaction.to_warehouse_id).first()
            if not to_warehouse:
                raise ValueError(f"To warehouse {transaction.to_warehouse_id} not found")
        
        # Validate that machine exists if provided
        if transaction.machine_id:
            machine = self.db.query(models.Machine).filter(models.Machine.id == transaction.machine_id).first()
            if not machine:
                raise ValueError(f"Machine {transaction.machine_id} not found")
        
        # Validate that user exists
        user = self.db.query(models.User).filter(models.User.id == transaction.performed_by_user_id).first()
        if not user:
            raise ValueError(f"User {transaction.performed_by_user_id} not found")
        
        # Check if transaction requires approval (high-value)
        if self._requires_approval(transaction):
            # For now, we'll just log this. In a real system, we might set a status flag
            # and implement an approval workflow.
            logger.info(f"High-value transaction requires approval: {transaction.dict()}")
    
    def _update_inventory(self, transaction: models.Transaction):
        """
        Update inventory based on transaction type.
        """
        if transaction.transaction_type == models.TransactionType.CREATION:
            # Increase inventory in to_warehouse
            self._update_warehouse_inventory(transaction.to_warehouse_id, transaction.part_id, transaction.quantity)
        
        elif transaction.transaction_type == models.TransactionType.TRANSFER:
            # Decrease inventory in from_warehouse
            self._update_warehouse_inventory(transaction.from_warehouse_id, transaction.part_id, -transaction.quantity)
            # Increase inventory in to_warehouse
            self._update_warehouse_inventory(transaction.to_warehouse_id, transaction.part_id, transaction.quantity)
        
        elif transaction.transaction_type == models.TransactionType.CONSUMPTION:
            # Decrease inventory in from_warehouse
            self._update_warehouse_inventory(transaction.from_warehouse_id, transaction.part_id, -transaction.quantity)
        
        elif transaction.transaction_type == models.TransactionType.ADJUSTMENT:
            # Adjust inventory in from_warehouse (can be positive or negative)
            self._update_warehouse_inventory(transaction.from_warehouse_id, transaction.part_id, transaction.quantity)
    
    def _update_warehouse_inventory(self, warehouse_id: uuid.UUID, part_id: uuid.UUID, quantity: Decimal):
        """
        Update inventory for a part in a warehouse.
        """
        # Get the inventory item
        inventory_item = self.db.query(models.Inventory).filter(
            models.Inventory.warehouse_id == warehouse_id,
            models.Inventory.part_id == part_id
        ).first()
        
        if inventory_item:
            # Update existing inventory
            inventory_item.current_stock += quantity
            inventory_item.last_updated = datetime.now()
            
            # Ensure stock doesn't go below zero
            if inventory_item.current_stock < 0:
                raise ValueError(f"Insufficient stock for part {part_id} in warehouse {warehouse_id}")
        else:
            # Create new inventory item if it doesn't exist (only for positive quantities)
            if quantity <= 0:
                raise ValueError(f"Cannot create inventory with negative quantity for part {part_id} in warehouse {warehouse_id}")
            
            # Get part details for unit_of_measure
            part = self.db.query(models.Part).filter(models.Part.id == part_id).first()
            if not part:
                raise ValueError(f"Part {part_id} not found")
            
            # Create new inventory item
            inventory_item = models.Inventory(
                warehouse_id=warehouse_id,
                part_id=part_id,
                current_stock=quantity,
                unit_of_measure=part.unit_of_measure
            )
            self.db.add(inventory_item)
    
    def _requires_approval(self, transaction: schemas.TransactionCreate) -> bool:
        """
        Check if a transaction requires approval based on business rules.
        """
        # Rule 1: Transactions with quantity > 100 require approval
        if transaction.quantity > 100:
            return True
        
        # Rule 2: All ADJUSTMENT transactions with quantity > 50 require approval
        if transaction.transaction_type == schemas.TransactionTypeEnum.ADJUSTMENT and transaction.quantity > 50:
            return True
        
        # Rule 3: Transfers between organizations require approval
        if transaction.transaction_type == schemas.TransactionTypeEnum.TRANSFER:
            if transaction.from_warehouse_id and transaction.to_warehouse_id:
                from_warehouse = self.db.query(models.Warehouse).filter(models.Warehouse.id == transaction.from_warehouse_id).first()
                to_warehouse = self.db.query(models.Warehouse).filter(models.Warehouse.id == transaction.to_warehouse_id).first()
                
                if from_warehouse and to_warehouse and from_warehouse.organization_id != to_warehouse.organization_id:
                    return True
        
        # Rule 4: Check if part is high-value (based on recent supplier orders)
        if transaction.part_id:
            # Get the most recent supplier order item for this part
            supplier_order_item = self.db.query(
                models.SupplierOrderItem
            ).join(
                models.SupplierOrder, models.SupplierOrderItem.supplier_order_id == models.SupplierOrder.id
            ).filter(
                models.SupplierOrderItem.part_id == transaction.part_id
            ).order_by(
                models.SupplierOrder.order_date.desc()
            ).first()
            
            # If the part has a unit price > 1000, require approval
            if supplier_order_item and supplier_order_item.unit_price and supplier_order_item.unit_price > 1000:
                return True
        
        return False
    
    def calculate_inventory_balance(self, warehouse_id: uuid.UUID, part_id: uuid.UUID) -> Decimal:
        """
        Calculate inventory balance for a part in a warehouse based on transaction history.
        """
        # Get all transactions involving this part and warehouse
        creation_transactions = self.db.query(
            models.Transaction
        ).filter(
            models.Transaction.transaction_type == models.TransactionType.CREATION,
            models.Transaction.part_id == part_id,
            models.Transaction.to_warehouse_id == warehouse_id
        ).all()
        
        transfer_in_transactions = self.db.query(
            models.Transaction
        ).filter(
            models.Transaction.transaction_type == models.TransactionType.TRANSFER,
            models.Transaction.part_id == part_id,
            models.Transaction.to_warehouse_id == warehouse_id
        ).all()
        
        transfer_out_transactions = self.db.query(
            models.Transaction
        ).filter(
            models.Transaction.transaction_type == models.TransactionType.TRANSFER,
            models.Transaction.part_id == part_id,
            models.Transaction.from_warehouse_id == warehouse_id
        ).all()
        
        consumption_transactions = self.db.query(
            models.Transaction
        ).filter(
            models.Transaction.transaction_type == models.TransactionType.CONSUMPTION,
            models.Transaction.part_id == part_id,
            models.Transaction.from_warehouse_id == warehouse_id
        ).all()
        
        adjustment_transactions = self.db.query(
            models.Transaction
        ).filter(
            models.Transaction.transaction_type == models.TransactionType.ADJUSTMENT,
            models.Transaction.part_id == part_id,
            models.Transaction.from_warehouse_id == warehouse_id
        ).all()
        
        # Calculate balance
        balance = Decimal('0')
        
        # Add creations
        for transaction in creation_transactions:
            balance += transaction.quantity
        
        # Add transfers in
        for transaction in transfer_in_transactions:
            balance += transaction.quantity
        
        # Subtract transfers out
        for transaction in transfer_out_transactions:
            balance -= transaction.quantity
        
        # Subtract consumptions
        for transaction in consumption_transactions:
            balance -= transaction.quantity
        
        # Add/subtract adjustments
        for transaction in adjustment_transactions:
            balance += transaction.quantity
        
        return balance
    
    def reconcile_inventory(self, warehouse_id: uuid.UUID, part_id: uuid.UUID) -> Dict[str, Any]:
        """
        Reconcile inventory for a part in a warehouse by comparing calculated balance with current stock.
        """
        # Get current inventory
        inventory_item = self.db.query(models.Inventory).filter(
            models.Inventory.warehouse_id == warehouse_id,
            models.Inventory.part_id == part_id
        ).first()
        
        if not inventory_item:
            return {
                "warehouse_id": warehouse_id,
                "part_id": part_id,
                "current_stock": Decimal('0'),
                "calculated_balance": Decimal('0'),
                "discrepancy": Decimal('0'),
                "reconciled": True
            }
        
        # Calculate balance from transactions
        calculated_balance = self.calculate_inventory_balance(warehouse_id, part_id)
        
        # Calculate discrepancy
        discrepancy = inventory_item.current_stock - calculated_balance
        
        # Determine if reconciliation is needed
        reconciled = discrepancy == 0
        
        return {
            "warehouse_id": warehouse_id,
            "part_id": part_id,
            "current_stock": inventory_item.current_stock,
            "calculated_balance": calculated_balance,
            "discrepancy": discrepancy,
            "reconciled": reconciled
        }
    
    def process_approved_transaction(self, transaction_id: uuid.UUID) -> models.Transaction:
        """
        Process a transaction that was previously pending approval and has now been approved.
        """
        try:
            # Get the transaction
            db_transaction = self.db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
            if not db_transaction:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            # Check if transaction is pending approval
            if not db_transaction.requires_approval or db_transaction.approval_status != 'pending':
                raise ValueError(f"Transaction {transaction_id} is not pending approval")
            
            # Update inventory based on transaction type
            self._update_inventory(db_transaction)
            
            # Update transaction status
            db_transaction.approval_status = 'approved'
            
            # Commit the changes
            self.db.commit()
            self.db.refresh(db_transaction)
            
            # Log the transaction
            logger.info(f"Approved transaction {db_transaction.id} processed successfully")
            
            return db_transaction
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing approved transaction: {e}")
            raise HTTPException(status_code=400, detail=f"Error processing approved transaction: {str(e)}")
    
    def get_transaction_analytics(self, days: int = 30, organization_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """
        Generate transaction analytics for reporting.
        """
        from datetime import timedelta
        from sqlalchemy import func, desc
        
        # Calculate the start date for the analytics period
        start_date = datetime.now() - timedelta(days=days)
        
        # Base query for transaction counts by type
        type_counts_query = self.db.query(
            models.Transaction.transaction_type,
            func.count(models.Transaction.id).label("count")
        ).filter(
            models.Transaction.transaction_date >= start_date
        ).group_by(
            models.Transaction.transaction_type
        )
        
        # Base query for transaction quantities by type
        type_quantities_query = self.db.query(
            models.Transaction.transaction_type,
            func.sum(models.Transaction.quantity).label("total_quantity")
        ).filter(
            models.Transaction.transaction_date >= start_date
        ).group_by(
            models.Transaction.transaction_type
        )
        
        # Base query for top parts by transaction count
        top_parts_query = self.db.query(
            models.Part.id,
            models.Part.name,
            models.Part.part_number,
            func.count(models.Transaction.id).label("transaction_count")
        ).join(
            models.Transaction, models.Transaction.part_id == models.Part.id
        ).filter(
            models.Transaction.transaction_date >= start_date
        ).group_by(
            models.Part.id, models.Part.name, models.Part.part_number
        ).order_by(
            desc("transaction_count")
        ).limit(10)
        
        # Base query for top warehouses by transaction count
        top_warehouses_query = self.db.query(
            models.Warehouse.id,
            models.Warehouse.name,
            func.count(models.Transaction.id).label("transaction_count")
        ).join(
            models.Transaction, 
            (models.Transaction.from_warehouse_id == models.Warehouse.id) | 
            (models.Transaction.to_warehouse_id == models.Warehouse.id)
        ).filter(
            models.Transaction.transaction_date >= start_date
        ).group_by(
            models.Warehouse.id, models.Warehouse.name
        ).order_by(
            desc("transaction_count")
        ).limit(10)
        
        # Filter by organization if provided
        if organization_id:
            # Get all warehouses for the organization
            warehouses = self.db.query(models.Warehouse).filter(models.Warehouse.organization_id == organization_id).all()
            warehouse_ids = [w.id for w in warehouses]
            
            # Filter transactions where from_warehouse_id or to_warehouse_id is in the organization's warehouses
            type_counts_query = type_counts_query.filter(
                (models.Transaction.from_warehouse_id.in_(warehouse_ids)) | 
                (models.Transaction.to_warehouse_id.in_(warehouse_ids))
            )
            
            type_quantities_query = type_quantities_query.filter(
                (models.Transaction.from_warehouse_id.in_(warehouse_ids)) | 
                (models.Transaction.to_warehouse_id.in_(warehouse_ids))
            )
            
            top_parts_query = top_parts_query.filter(
                (models.Transaction.from_warehouse_id.in_(warehouse_ids)) | 
                (models.Transaction.to_warehouse_id.in_(warehouse_ids))
            )
            
            top_warehouses_query = top_warehouses_query.filter(models.Warehouse.organization_id == organization_id)
        
        # Execute queries
        type_counts = type_counts_query.all()
        type_quantities = type_quantities_query.all()
        top_parts = top_parts_query.all()
        top_warehouses = top_warehouses_query.all()
        
        # Format results
        type_counts_dict = {t.transaction_type.value: t.count for t in type_counts}
        type_quantities_dict = {t.transaction_type.value: float(t.total_quantity) for t in type_quantities}
        
        top_parts_list = [
            {
                "part_id": str(p.id),
                "part_name": p.name,
                "part_number": p.part_number,
                "transaction_count": p.transaction_count
            }
            for p in top_parts
        ]
        
        top_warehouses_list = [
            {
                "warehouse_id": str(w.id),
                "warehouse_name": w.name,
                "transaction_count": w.transaction_count
            }
            for w in top_warehouses
        ]
        
        # Calculate total transactions
        total_transactions = sum(t.count for t in type_counts)
        
        # Calculate daily average
        daily_average = total_transactions / days if days > 0 else 0
        
        return {
            "period_days": days,
            "total_transactions": total_transactions,
            "daily_average": daily_average,
            "transactions_by_type": type_counts_dict,
            "quantities_by_type": type_quantities_dict,
            "top_parts": top_parts_list,
            "top_warehouses": top_warehouses_list
        }


# Create a function to get a TransactionProcessor instance
def get_transaction_processor(db: Session) -> TransactionProcessor:
    """
    Get a TransactionProcessor instance.
    """
    return TransactionProcessor(db)