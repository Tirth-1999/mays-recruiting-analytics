-- Marketing Data Schema for Edulytix
-- This schema is ready for when Ologie marketing spend data arrives

-- Marketing Campaigns Table
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_name TEXT NOT NULL,
    campaign_type TEXT,  -- e.g., 'Google Ads', 'Facebook', 'LinkedIn', 'Email', 'Direct Mail'
    start_date TEXT,
    end_date TEXT,
    target_program TEXT,  -- Which program this campaign targets
    target_cohort INTEGER,  -- Which cohort year
    status TEXT DEFAULT 'active',  -- 'active', 'paused', 'completed'
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Marketing Spend Table
CREATE TABLE IF NOT EXISTS marketing_spend (
    spend_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER,
    spend_date TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    channel TEXT,  -- 'Google Ads', 'Facebook', 'LinkedIn', 'Email', etc.
    program TEXT,
    cohort_year INTEGER,
    FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns(campaign_id)
);

-- Inquiry Sources Table
CREATE TABLE IF NOT EXISTS inquiry_sources (
    inquiry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    inquiry_date TEXT NOT NULL,
    source TEXT NOT NULL,  -- 'Google Ads', 'Facebook', 'LinkedIn', 'Referral', 'Direct', 'Email', etc.
    campaign_id INTEGER,
    program TEXT,
    cohort_year INTEGER,
    converted_to_application INTEGER DEFAULT 0,  -- 0 or 1
    application_date TEXT,
    FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns(campaign_id)
);

-- Marketing Metrics Summary Table (aggregated data)
CREATE TABLE IF NOT EXISTS marketing_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date TEXT NOT NULL,
    program TEXT,
    cohort_year INTEGER,
    channel TEXT,
    campaign_id INTEGER,
    impressions INTEGER,
    clicks INTEGER,
    inquiries INTEGER,
    applications INTEGER,
    spend REAL,
    cost_per_click REAL,
    cost_per_inquiry REAL,
    cost_per_application REAL,
    conversion_rate REAL,  -- inquiry to application %
    FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns(campaign_id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_marketing_spend_date ON marketing_spend(spend_date);
CREATE INDEX IF NOT EXISTS idx_marketing_spend_program ON marketing_spend(program);
CREATE INDEX IF NOT EXISTS idx_marketing_spend_channel ON marketing_spend(channel);
CREATE INDEX IF NOT EXISTS idx_inquiry_sources_date ON inquiry_sources(inquiry_date);
CREATE INDEX IF NOT EXISTS idx_inquiry_sources_source ON inquiry_sources(source);
CREATE INDEX IF NOT EXISTS idx_inquiry_sources_program ON inquiry_sources(program);
CREATE INDEX IF NOT EXISTS idx_marketing_metrics_date ON marketing_metrics(report_date);
CREATE INDEX IF NOT EXISTS idx_marketing_metrics_program ON marketing_metrics(program);
CREATE INDEX IF NOT EXISTS idx_marketing_metrics_channel ON marketing_metrics(channel);

-- Sample data structure (commented out - for reference)
/*
-- Example Campaign
INSERT INTO marketing_campaigns (campaign_name, campaign_type, start_date, target_program, target_cohort)
VALUES ('MBA Fall 2026 Google Search', 'Google Ads', '2025-01-01', 'MBA', 2026);

-- Example Spend
INSERT INTO marketing_spend (campaign_id, spend_date, amount, channel, program, cohort_year)
VALUES (1, '2025-01-15', 5000.00, 'Google Ads', 'MBA', 2026);

-- Example Inquiry
INSERT INTO inquiry_sources (inquiry_date, source, campaign_id, program, cohort_year, converted_to_application)
VALUES ('2025-01-16', 'Google Ads', 1, 'MBA', 2026, 1);

-- Example Metrics
INSERT INTO marketing_metrics (report_date, program, cohort_year, channel, impressions, clicks, inquiries, applications, spend, cost_per_inquiry)
VALUES ('2025-01-31', 'MBA', 2026, 'Google Ads', 50000, 2500, 150, 45, 5000.00, 33.33);
*/
