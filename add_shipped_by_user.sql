-- Add shipped_by_user_id column to customer_orders table
ALTER TABLE customer_orders 
ADD COLUMN IF NOT EXISTS shipped_by_user_id UUID REFERENCES users(id);

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_customer_orders_shipped_by_user 
ON customer_orders(shipped_by_user_id);

-- Display success message
SELECT 'shipped_by_user_id column added successfully!' as status;
