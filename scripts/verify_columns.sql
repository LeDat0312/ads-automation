-- Script để kiểm tra các cột trong bảng accounts, prefixes, account_prefixes
-- Chạy: psql -U adsuser -d ads_automation -f scripts/verify_columns.sql

-- Kiểm tra bảng accounts
SELECT '=== ACCOUNTS TABLE COLUMNS ===' AS info;
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'accounts'
ORDER BY ordinal_position;

-- Kiểm tra bảng prefixes
SELECT '=== PREFIXES TABLE COLUMNS ===' AS info;
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'prefixes'
ORDER BY ordinal_position;

-- Kiểm tra bảng account_prefixes
SELECT '=== ACCOUNT_PREFIXES TABLE COLUMNS ===' AS info;
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'account_prefixes'
ORDER BY ordinal_position;

-- Kiểm tra các index
SELECT '=== INDEXES ===' AS info;
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('accounts', 'prefixes', 'account_prefixes')
ORDER BY tablename, indexname;

-- Kiểm tra foreign keys
SELECT '=== FOREIGN KEYS ===' AS info;
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
  AND tc.table_name IN ('accounts', 'prefixes', 'account_prefixes');

