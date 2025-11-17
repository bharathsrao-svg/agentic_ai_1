-- SQL script to alter existing tables to increase column sizes
-- Run this script in your PostgreSQL database: demo_db
-- This fixes the "value too long" error

-- Alter symbol column to allow longer values
ALTER TABLE holdings ALTER COLUMN symbol TYPE VARCHAR(500);

-- Alter exchange column to allow longer values
ALTER TABLE holdings ALTER COLUMN exchange TYPE VARCHAR(200);

-- Note: If you get an error about the column not existing, 
-- the table might not have been created yet. Run create_tables.sql first.

