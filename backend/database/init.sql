-- Initialize DENSO Forecast Database
-- Alert Storage Schema

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('high', 'medium', 'low')),
    message TEXT NOT NULL,
    affected_products TEXT[], -- Array of product codes
    affected_categories TEXT[], -- Array of category names
    impact_description TEXT,
    action_required TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    read_by VARCHAR(100),
    dismissed BOOLEAN DEFAULT FALSE,
    dismissed_at TIMESTAMP WITH TIME ZONE,
    source VARCHAR(50) DEFAULT 'scheduled_job',
    metadata JSONB, -- Flexible field for extra data
    priority_score INTEGER DEFAULT 50 CHECK (priority_score >= 0 AND priority_score <= 100)
);

-- Create indexes for fast queries
CREATE INDEX idx_alerts_created_at ON alerts (created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts (severity);
CREATE INDEX idx_alerts_read ON alerts (read, severity);
CREATE INDEX idx_alerts_alert_type ON alerts (alert_type);
CREATE INDEX idx_alerts_affected_products ON alerts USING GIN (affected_products);
CREATE INDEX idx_alerts_metadata ON alerts USING GIN (metadata);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_alerts_updated_at 
    BEFORE UPDATE ON alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample alerts for testing
INSERT INTO alerts (
    alert_type, 
    severity, 
    message, 
    affected_products, 
    affected_categories,
    impact_description,
    action_required,
    source,
    metadata,
    priority_score
) VALUES 
(
    'logistics_delay',
    'high',
    'Port congestion at Yokohama causing 48-hour shipping delay',
    ARRAY['BUGI-IRIDIUM-VCH20', 'BUGI-PLATIN-PK16TT'],
    ARRAY['Spark_Plugs'],
    'Q1 2025 production schedule at risk due to delayed component delivery',
    'Contact alternative shipping routes and expedite customs clearance',
    'scheduled_job',
    '{"port": "Yokohama", "delay_hours": 48, "carrier": "Nippon Express", "estimated_arrival": "2025-01-20"}'::jsonb,
    90
),
(
    'capacity_warning',
    'high',
    'Production capacity utilization reaching 92% - potential bottleneck',
    ARRAY['AC-COMPRESSOR-6SEU14C', 'AC-EVAPORATOR-CORE', 'AC-CONDENSER-CORE'],
    ARRAY['AC_System'],
    'Q1 demand forecast exceeds current production capacity by 8%',
    'Schedule overtime shifts or contract third-party manufacturers',
    'scheduled_job',
    '{"utilization_rate": 0.92, "shortfall_units": 450, "affected_lines": ["Line A", "Line B"]}'::jsonb,
    85
),
(
    'supplier_risk',
    'medium',
    'Supplier quality audit score dropped to 72/100',
    ARRAY['BUGI-IRIDIUM-VCH20'],
    ARRAY['Spark_Plugs'],
    'Recent shipments show 3.5% defect rate, above acceptable threshold',
    'Schedule supplier quality review meeting and implement corrective actions',
    'manual_trigger',
    '{"supplier_name": "ABC Components Ltd", "audit_score": 72, "defect_rate": 0.035, "previous_score": 88}'::jsonb,
    65
),
(
    'demand_spike',
    'medium',
    'Unexpected 25% demand increase detected for AC System products',
    ARRAY['AC-COMPRESSOR-6SEU14C', 'AC-EVAPORATOR-CORE'],
    ARRAY['AC_System'],
    'Market analysis indicates early summer heat wave driving AC demand',
    'Increase production forecast and secure additional raw materials',
    'scheduled_job',
    '{"demand_increase": 0.25, "market_factor": "weather", "confidence": 0.88}'::jsonb,
    70
),
(
    'inventory_alert',
    'low',
    'Inventory levels for PK16TT spark plugs below safety stock',
    ARRAY['BUGI-PLATIN-PK16TT'],
    ARRAY['Spark_Plugs'],
    'Current inventory: 450 units, safety stock: 600 units',
    'Expedite next production batch or place emergency order',
    'scheduled_job',
    '{"current_inventory": 450, "safety_stock": 600, "days_until_stockout": 12}'::jsonb,
    50
);

-- Create view for unread alerts summary
CREATE OR REPLACE VIEW unread_alerts_summary AS
SELECT 
    severity,
    COUNT(*) as count,
    MAX(created_at) as latest_alert
FROM alerts
WHERE read = FALSE AND dismissed = FALSE
GROUP BY severity
ORDER BY 
    CASE severity
        WHEN 'high' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'low' THEN 3
    END;

-- Create view for alert statistics
CREATE OR REPLACE VIEW alert_statistics AS
SELECT 
    alert_type,
    severity,
    COUNT(*) as total_count,
    COUNT(*) FILTER (WHERE read = FALSE) as unread_count,
    AVG(priority_score) as avg_priority,
    MAX(created_at) as most_recent
FROM alerts
WHERE dismissed = FALSE
GROUP BY alert_type, severity
ORDER BY severity, alert_type;

COMMENT ON TABLE alerts IS 'Stores all system alerts for demand forecasting and supply chain risks';
COMMENT ON COLUMN alerts.metadata IS 'Flexible JSONB field for storing alert-specific data';
COMMENT ON VIEW unread_alerts_summary IS 'Quick summary of unread alerts by severity';
COMMENT ON VIEW alert_statistics IS 'Comprehensive alert statistics for dashboard';
