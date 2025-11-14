-- Script để FORCE thêm các cột (xóa và thêm lại nếu cần)
-- Chạy: psql -U adsuser -d ads_automation -f scripts/force_add_columns.sql

BEGIN;

-- Xóa cột nếu tồn tại và thêm lại (chỉ dùng khi cần thiết)
-- KHÔNG chạy phần này trừ khi bạn chắc chắn muốn xóa dữ liệu!

-- Thay vào đó, chỉ thêm cột nếu chưa có (an toàn hơn)
DO $$ 
BEGIN
    -- Accounts table
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'accounts' AND column_name = 'account_type'
    ) THEN
        ALTER TABLE accounts ADD COLUMN account_type VARCHAR DEFAULT 'UNKNOWN';
        RAISE NOTICE 'Đã thêm cột account_type vào accounts';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'accounts' AND column_name = 'timezone'
    ) THEN
        ALTER TABLE accounts ADD COLUMN timezone VARCHAR DEFAULT 'Asia/Ho_Chi_Minh';
        RAISE NOTICE 'Đã thêm cột timezone vào accounts';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'accounts' AND column_name = 'enabled'
    ) THEN
        ALTER TABLE accounts ADD COLUMN enabled BOOLEAN DEFAULT TRUE;
        RAISE NOTICE 'Đã thêm cột enabled vào accounts';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'accounts' AND column_name = 'status'
    ) THEN
        ALTER TABLE accounts ADD COLUMN status VARCHAR DEFAULT 'ACTIVE';
        RAISE NOTICE 'Đã thêm cột status vào accounts';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'accounts' AND column_name = 'last_30_days_spend'
    ) THEN
        ALTER TABLE accounts ADD COLUMN last_30_days_spend DOUBLE PRECISION DEFAULT 0.0;
        RAISE NOTICE 'Đã thêm cột last_30_days_spend vào accounts';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'accounts' AND column_name = 'description'
    ) THEN
        ALTER TABLE accounts ADD COLUMN description TEXT;
        RAISE NOTICE 'Đã thêm cột description vào accounts';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'accounts' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE accounts ADD COLUMN user_id INTEGER;
        CREATE INDEX IF NOT EXISTS ix_accounts_user_id ON accounts(user_id);
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
            ALTER TABLE accounts ADD CONSTRAINT fk_accounts_user_id 
                FOREIGN KEY (user_id) REFERENCES users(id);
        END IF;
        RAISE NOTICE 'Đã thêm cột user_id vào accounts';
    END IF;
END $$;

COMMIT;

-- Kiểm tra lại
SELECT '=== VERIFICATION ===' AS info;
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'accounts' 
  AND column_name IN ('account_type', 'timezone', 'enabled', 'status', 'last_30_days_spend', 'description', 'user_id')
ORDER BY column_name;

