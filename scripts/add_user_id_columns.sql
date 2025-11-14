-- Script SQL để thêm cột user_id vào các bảng accounts, prefixes, account_prefixes
-- Chạy script này nếu bảng đã tồn tại nhưng thiếu cột user_id

-- 1. Thêm cột user_id vào bảng accounts (nếu chưa có)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'accounts' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE accounts ADD COLUMN user_id INTEGER;
        CREATE INDEX IF NOT EXISTS ix_accounts_user_id ON accounts(user_id);
        -- Thêm foreign key constraint (nếu bảng users đã tồn tại)
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
            ALTER TABLE accounts ADD CONSTRAINT fk_accounts_user_id 
                FOREIGN KEY (user_id) REFERENCES users(id);
        END IF;
        RAISE NOTICE 'Đã thêm cột user_id vào bảng accounts';
    ELSE
        RAISE NOTICE 'Cột user_id đã tồn tại trong bảng accounts';
    END IF;
END $$;

-- 2. Thêm cột user_id vào bảng prefixes (nếu chưa có)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'prefixes' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE prefixes ADD COLUMN user_id INTEGER;
        CREATE INDEX IF NOT EXISTS ix_prefixes_user_id ON prefixes(user_id);
        -- Thêm foreign key constraint (nếu bảng users đã tồn tại)
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
            ALTER TABLE prefixes ADD CONSTRAINT fk_prefixes_user_id 
                FOREIGN KEY (user_id) REFERENCES users(id);
        END IF;
        RAISE NOTICE 'Đã thêm cột user_id vào bảng prefixes';
    ELSE
        RAISE NOTICE 'Cột user_id đã tồn tại trong bảng prefixes';
    END IF;
END $$;

-- 3. Thêm cột user_id vào bảng account_prefixes (nếu chưa có)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'account_prefixes' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE account_prefixes ADD COLUMN user_id INTEGER;
        CREATE INDEX IF NOT EXISTS ix_account_prefixes_user_id ON account_prefixes(user_id);
        -- Thêm foreign key constraint (nếu bảng users đã tồn tại)
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
            ALTER TABLE account_prefixes ADD CONSTRAINT fk_account_prefixes_user_id 
                FOREIGN KEY (user_id) REFERENCES users(id);
        END IF;
        RAISE NOTICE 'Đã thêm cột user_id vào bảng account_prefixes';
    ELSE
        RAISE NOTICE 'Cột user_id đã tồn tại trong bảng account_prefixes';
    END IF;
END $$;

-- 4. Kiểm tra kết quả
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name IN ('accounts', 'prefixes', 'account_prefixes')
    AND column_name = 'user_id'
ORDER BY table_name;

