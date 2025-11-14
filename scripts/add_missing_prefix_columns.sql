-- Script SQL để thêm các cột còn thiếu vào bảng prefixes
-- Chạy: psql -U adsuser -d ads_automation -f scripts/add_missing_prefix_columns.sql

-- Thêm cột prefix_name nếu chưa có
ALTER TABLE prefixes ADD COLUMN IF NOT EXISTS prefix_name VARCHAR;

-- Thêm cột enabled nếu chưa có
ALTER TABLE prefixes ADD COLUMN IF NOT EXISTS enabled BOOLEAN DEFAULT TRUE;

-- Thêm cột description nếu chưa có
ALTER TABLE prefixes ADD COLUMN IF NOT EXISTS description TEXT;

-- Thêm cột user_id nếu chưa có
ALTER TABLE prefixes ADD COLUMN IF NOT EXISTS user_id INTEGER;
CREATE INDEX IF NOT EXISTS ix_prefixes_user_id ON prefixes(user_id);

-- Thêm foreign key constraint cho user_id nếu chưa có
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

-- Kiểm tra kết quả
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'prefixes'
ORDER BY ordinal_position;

