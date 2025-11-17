-- SQL script to create tables for stock holdings
-- Run this script in your PostgreSQL database: demo_db

-- Table for holdings import sessions
-- Using UNIQUE on source_file to enable idempotent upserts
CREATE TABLE IF NOT EXISTS holdings_imports (
    id SERIAL PRIMARY KEY,
    source_file VARCHAR(500) NOT NULL UNIQUE,
    parse_date TIMESTAMP NOT NULL,
    total_value NUMERIC(15, 2),
    total_holdings INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on source_file for faster lookups
CREATE INDEX IF NOT EXISTS idx_holdings_imports_source_file ON holdings_imports(source_file);

-- Table for individual holdings
CREATE TABLE IF NOT EXISTS holdings (
    id SERIAL PRIMARY KEY,
    import_id INTEGER REFERENCES holdings_imports(id) ON DELETE CASCADE,
    symbol VARCHAR(100) NOT NULL,
    company_name VARCHAR(500),
    quantity NUMERIC(15, 4),
    price NUMERIC(15, 4),
    value NUMERIC(15, 2),
    sector VARCHAR(200),
    exchange VARCHAR(100),
    currency VARCHAR(10),
    holding_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(import_id, symbol)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_holdings_symbol ON holdings(symbol);
CREATE INDEX IF NOT EXISTS idx_holdings_import_id ON holdings(import_id);
CREATE INDEX IF NOT EXISTS idx_holdings_sector ON holdings(sector);
CREATE INDEX IF NOT EXISTS idx_holdings_value ON holdings(value);

-- View for latest holdings summary
CREATE OR REPLACE VIEW latest_holdings_summary AS
SELECT 
    h.symbol,
    h.company_name,
    h.quantity,
    h.price,
    h.value,
    h.sector,
    h.exchange,
    h.holding_date,
    hi.parse_date as import_date,
    hi.source_file
FROM holdings h
JOIN holdings_imports hi ON h.import_id = hi.id
WHERE hi.parse_date = (
    SELECT MAX(parse_date) FROM holdings_imports
)
ORDER BY h.value DESC NULLS LAST;

