-- Force create stocktake tables for production
-- This SQL is extracted from the inventory_workflow_001 migration

-- Create stocktake_status enum if it doesn't exist
DO $$ BEGIN
    CREATE TYPE stocktakestatus AS ENUM ('planned', 'in_progress', 'completed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create inventory_alert_type enum if it doesn't exist
DO $$ BEGIN
    CREATE TYPE inventoryalerttype AS ENUM ('low_stock', 'stockout', 'expiring', 'expired', 'excess', 'discrepancy');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create inventory_alert_severity enum if it doesn't exist
DO $$ BEGIN
    CREATE TYPE inventoryalertseverity AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create stocktakes table if it doesn't exist
CREATE TABLE IF NOT EXISTS stocktakes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_id UUID NOT NULL REFERENCES warehouses(id),
    scheduled_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status stocktakestatus NOT NULL DEFAULT 'planned',
    notes TEXT,
    scheduled_by_user_id UUID NOT NULL REFERENCES users(id),
    completed_date TIMESTAMP WITH TIME ZONE,
    completed_by_user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create indexes for stocktakes if they don't exist
CREATE INDEX IF NOT EXISTS ix_stocktakes_warehouse_id ON stocktakes(warehouse_id);
CREATE INDEX IF NOT EXISTS ix_stocktakes_status ON stocktakes(status);
CREATE INDEX IF NOT EXISTS ix_stocktakes_scheduled_date ON stocktakes(scheduled_date);

-- Create stocktake_items table if it doesn't exist
CREATE TABLE IF NOT EXISTS stocktake_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stocktake_id UUID NOT NULL REFERENCES stocktakes(id) ON DELETE CASCADE,
    part_id UUID NOT NULL REFERENCES parts(id),
    expected_quantity DECIMAL(10,3) NOT NULL,
    actual_quantity DECIMAL(10,3),
    counted_at TIMESTAMP WITH TIME ZONE,
    counted_by_user_id UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create indexes for stocktake_items if they don't exist
CREATE INDEX IF NOT EXISTS ix_stocktake_items_stocktake_id ON stocktake_items(stocktake_id);
CREATE INDEX IF NOT EXISTS ix_stocktake_items_part_id ON stocktake_items(part_id);

-- Create inventory_alerts table if it doesn't exist
CREATE TABLE IF NOT EXISTS inventory_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_id UUID NOT NULL REFERENCES warehouses(id),
    part_id UUID NOT NULL REFERENCES parts(id),
    alert_type inventoryalerttype NOT NULL,
    severity inventoryalertseverity NOT NULL,
    threshold_value DECIMAL(10,3),
    current_value DECIMAL(10,3) NOT NULL,
    message TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by_user_id UUID REFERENCES users(id),
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create indexes for inventory_alerts if they don't exist
CREATE INDEX IF NOT EXISTS ix_inventory_alerts_warehouse_id ON inventory_alerts(warehouse_id);
CREATE INDEX IF NOT EXISTS ix_inventory_alerts_part_id ON inventory_alerts(part_id);
CREATE INDEX IF NOT EXISTS ix_inventory_alerts_alert_type ON inventory_alerts(alert_type);
CREATE INDEX IF NOT EXISTS ix_inventory_alerts_severity ON inventory_alerts(severity);
CREATE INDEX IF NOT EXISTS ix_inventory_alerts_is_active ON inventory_alerts(is_active);

-- Create inventory_adjustments table if it doesn't exist
CREATE TABLE IF NOT EXISTS inventory_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_id UUID NOT NULL REFERENCES warehouses(id),
    part_id UUID NOT NULL REFERENCES parts(id),
    quantity_change DECIMAL(10,3) NOT NULL,
    previous_quantity DECIMAL(10,3) NOT NULL,
    new_quantity DECIMAL(10,3) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    notes TEXT,
    adjusted_by_user_id UUID NOT NULL REFERENCES users(id),
    adjustment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    stocktake_id UUID REFERENCES stocktakes(id),
    transaction_id UUID REFERENCES transactions(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create indexes for inventory_adjustments if they don't exist
CREATE INDEX IF NOT EXISTS ix_inventory_adjustments_warehouse_id ON inventory_adjustments(warehouse_id);
CREATE INDEX IF NOT EXISTS ix_inventory_adjustments_part_id ON inventory_adjustments(part_id);
CREATE INDEX IF NOT EXISTS ix_inventory_adjustments_adjustment_date ON inventory_adjustments(adjustment_date);
CREATE INDEX IF NOT EXISTS ix_inventory_adjustments_stocktake_id ON inventory_adjustments(stocktake_id);

-- Verify tables were created
SELECT 'Tables created successfully' as status;
SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%stocktake%' OR table_name LIKE '%inventory_a%' ORDER BY table_name;