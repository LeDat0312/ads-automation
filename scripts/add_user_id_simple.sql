-- Script SQL đơn giản để thêm cột user_id
-- Chạy: psql -U adsuser -d ads_automation -f scripts/add_user_id_simple.sql

-- Thêm cột user_id vào bảng accounts
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS user_id INTEGER;
CREATE INDEX IF NOT EXISTS ix_accounts_user_id ON accounts(user_id);
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_accounts_user_id'
    ) THEN
        ALTER TABLE accounts ADD CONSTRAINT fk_accounts_user_id 
            FOREIGN KEY (user_id) REFERENCES users(id);
    END IF;
END $$;

-- Thêm cột user_id vào bảng prefixes
ALTER TABLE prefixes ADD COLUMN IF NOT EXISTS user_id INTEGER;
CREATE INDEX IF NOT EXISTS ix_prefixes_user_id ON prefixes(user_id);
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_prefixes_user_id'
    ) THEN
        ALTER TABLE prefixes ADD CONSTRAINT fk_prefixes_user_id 
            FOREIGN KEY (user_id) REFERENCES users(id);
    END IF;
END $$;

-- Thêm cột user_id vào bảng account_prefixes
ALTER TABLE account_prefixes ADD COLUMN IF NOT EXISTS user_id INTEGER;
CREATE INDEX IF NOT EXISTS ix_account_prefixes_user_id ON account_prefixes(user_id);
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_account_prefixes_user_id'
    ) THEN
        ALTER TABLE account_prefixes ADD CONSTRAINT fk_account_prefixes_user_id 
            FOREIGN KEY (user_id) REFERENCES users(id);
    END IF;
END $$;

-- Kiểm tra kết quả
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name IN ('accounts', 'prefixes', 'account_prefixes')
    AND column_name = 'user_id'
ORDER BY table_name;

