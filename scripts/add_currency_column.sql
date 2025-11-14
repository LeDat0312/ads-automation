-- Script SQL để thêm cột currency vào bảng accounts
-- Chạy: psql -U adsuser -d ads_automation -f scripts/add_currency_column.sql

-- Thêm cột currency nếu chưa có
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS currency VARCHAR DEFAULT 'USD';

-- Cập nhật currency cho các accounts hiện có (nếu cần)
-- UPDATE accounts SET currency = 'USD' WHERE currency IS NULL;

-- Kiểm tra kết quả
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'accounts' AND column_name = 'currency';

