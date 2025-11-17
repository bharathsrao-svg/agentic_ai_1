-- Migration script to update existing tables for idempotency support
-- Run this script if you already have tables created with the old schema

-- Step 1: Drop the old unique constraint if it exists
ALTER TABLE holdings_imports DROP CONSTRAINT IF EXISTS holdings_imports_source_file_parse_date_key;

-- Step 2: Add UNIQUE constraint on source_file only (for idempotency)
-- This will fail if there are duplicate source_files, so handle those first
DO $$
BEGIN
    -- Check if unique constraint already exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'holdings_imports_source_file_key'
    ) THEN
        -- Add unique constraint on source_file
        ALTER TABLE holdings_imports ADD CONSTRAINT holdings_imports_source_file_key UNIQUE (source_file);
    END IF;
END $$;

-- Step 3: Add updated_at column if it doesn't exist
ALTER TABLE holdings_imports ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Step 4: Create index on source_file for faster lookups
CREATE INDEX IF NOT EXISTS idx_holdings_imports_source_file ON holdings_imports(source_file);

-- Note: If you have duplicate source_files, you'll need to clean them up first:
-- SELECT source_file, COUNT(*) FROM holdings_imports GROUP BY source_file HAVING COUNT(*) > 1;

