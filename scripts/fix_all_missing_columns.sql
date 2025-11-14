-- Script SQL tổng hợp để thêm tất cả các cột còn thiếu
-- Chạy: psql -U adsuser -d ads_automation -f scripts/fix_all_missing_columns.sql

-- ==================== ACCOUNTS TABLE ====================
-- Thêm các cột còn thiếu vào bảng accounts
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS account_type VARCHAR DEFAULT 'UNKNOWN';
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS timezone VARCHAR DEFAULT 'Asia/Ho_Chi_Minh';
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS enabled BOOLEAN DEFAULT TRUE;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'ACTIVE';
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS last_30_days_spend DOUBLE PRECISION DEFAULT 0.0;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- Tạo index cho user_id
CREATE INDEX IF NOT EXISTS ix_accounts_user_id ON accounts(user_id);

-- Thêm foreign key constraint cho user_id
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

-- ==================== PREFIXES TABLE ====================
-- Thêm các cột còn thiếu vào bảng prefixes
ALTER TABLE prefixes ADD COLUMN IF NOT EXISTS prefix_name VARCHAR;
ALTER TABLE prefixes ADD COLUMN IF NOT EXISTS enabled BOOLEAN DEFAULT TRUE;
ALTER TABLE prefixes ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE prefixes ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- Tạo index cho user_id
CREATE INDEX IF NOT EXISTS ix_prefixes_user_id ON prefixes(user_id);

-- Thêm foreign key constraint cho user_id
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_prefixes_user_id'
    ) THEN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
            ALTER TABLE prefixes ADD CONSTRAINT fk_prefixes_user_id 
                FOREIGN KEY (user_id) REFERENCES users(id);
        END IF;
    END IF;
END $$;

-- ==================== ACCOUNT_PREFIXES TABLE ====================
-- Thêm cột user_id nếu chưa có
ALTER TABLE account_prefixes ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- Tạo index cho user_id
CREATE INDEX IF NOT EXISTS ix_account_prefixes_user_id ON account_prefixes(user_id);

-- Thêm foreign key constraint cho user_id
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_account_prefixes_user_id'
    ) THEN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
            ALTER TABLE account_prefixes ADD CONSTRAINT fk_account_prefixes_user_id 
                FOREIGN KEY (user_id) REFERENCES users(id);
        END IF;
    END IF;
END $$;

-- ==================== KIỂM TRA KẾT QUẢ ====================
-- Hiển thị cấu trúc bảng accounts
SELECT '=== ACCOUNTS TABLE ===' AS info;
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'accounts'
ORDER BY ordinal_position;

-- Hiển thị cấu trúc bảng prefixes
SELECT '=== PREFIXES TABLE ===' AS info;
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'prefixes'
ORDER BY ordinal_position;

-- Hiển thị cấu trúc bảng account_prefixes
SELECT '=== ACCOUNT_PREFIXES TABLE ===' AS info;
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'account_prefixes'
ORDER BY ordinal_position;

