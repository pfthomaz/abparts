-- Create machine_hours table manually
CREATE TABLE IF NOT EXISTS machine_hours (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    machine_id UUID NOT NULL REFERENCES machines(id) ON DELETE CASCADE,
    recorded_by_user_id UUID NOT NULL REFERENCES users(id),
    hours_value DECIMAL(10, 2) NOT NULL,
    recorded_date TIMESTAMP WITH TIME ZONE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_machine_hours_machine_id ON machine_hours(machine_id);
CREATE INDEX IF NOT EXISTS idx_machine_hours_recorded_date ON machine_hours(recorded_date DESC);

-- Display success message
SELECT 'machine_hours table created successfully!' as status;
