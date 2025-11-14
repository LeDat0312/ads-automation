-- Add currency column to accounts table if not exists
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'USD';

-- Update existing accounts to have USD as default currency if NULL
UPDATE accounts SET currency = 'USD' WHERE currency IS NULL;
