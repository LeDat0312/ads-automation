-- Script SQL để thêm các cột còn thiếu vào bảng accounts
-- Chạy: psql -U adsuser -d ads_automation -f scripts/add_missing_account_columns.sql

-- Thêm cột account_type nếu chưa có
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS account_type VARCHAR DEFAULT 'UNKNOWN';

-- Thêm cột timezone nếu chưa có
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS timezone VARCHAR DEFAULT 'Asia/Ho_Chi_Minh';

-- Thêm cột enabled nếu chưa có
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS enabled BOOLEAN DEFAULT TRUE;

-- Thêm cột status nếu chưa có
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'ACTIVE';

-- Thêm cột last_30_days_spend nếu chưa có
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS last_30_days_spend DOUBLE PRECISION DEFAULT 0.0;

-- Thêm cột description nếu chưa có
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS description TEXT;

-- Thêm cột user_id nếu chưa có
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS user_id INTEGER;
CREATE INDEX IF NOT EXISTS ix_accounts_user_id ON accounts(user_id);

-- Thêm foreign key constraint cho user_id nếu chưa có
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_accounts_user_id'
    ) THEN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
            ALTER TABLE accounts ADD CONSTRAINT fk_accounts_user_id 
                FOREIGN KEY (user_id) REFERENCES users(id);
        END IF;
    END IF;
END $$;

-- Kiểm tra kết quả
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'accounts'
ORDER BY ordinal_position;

