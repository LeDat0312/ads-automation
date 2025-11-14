-- Migration script để thêm các cột Telegram Bot vào bảng user_settings
-- Chạy script này trên database để thêm các cột mới

DO $$
BEGIN
    -- Thêm cột telegram_bot_token_encrypted
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='user_settings' AND column_name='telegram_bot_token_encrypted') THEN
        ALTER TABLE user_settings ADD COLUMN telegram_bot_token_encrypted TEXT;
        RAISE NOTICE 'Đã thêm cột telegram_bot_token_encrypted';
    ELSE
        RAISE NOTICE 'Cột telegram_bot_token_encrypted đã tồn tại';
    END IF;
    
    -- Thêm cột telegram_chat_id
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='user_settings' AND column_name='telegram_chat_id') THEN
        ALTER TABLE user_settings ADD COLUMN telegram_chat_id VARCHAR(255);
        RAISE NOTICE 'Đã thêm cột telegram_chat_id';
    ELSE
        RAISE NOTICE 'Cột telegram_chat_id đã tồn tại';
    END IF;
    
    -- Thêm cột telegram_bot_status
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='user_settings' AND column_name='telegram_bot_status') THEN
        ALTER TABLE user_settings ADD COLUMN telegram_bot_status VARCHAR(50) DEFAULT 'NOT_SET';
        RAISE NOTICE 'Đã thêm cột telegram_bot_status';
    ELSE
        RAISE NOTICE 'Cột telegram_bot_status đã tồn tại';
    END IF;
    
    -- Thêm cột telegram_bot_last_checked
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='user_settings' AND column_name='telegram_bot_last_checked') THEN
        ALTER TABLE user_settings ADD COLUMN telegram_bot_last_checked TIMESTAMP;
        RAISE NOTICE 'Đã thêm cột telegram_bot_last_checked';
    ELSE
        RAISE NOTICE 'Cột telegram_bot_last_checked đã tồn tại';
    END IF;
END $$;

-- Kiểm tra kết quả
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'user_settings'
AND column_name LIKE 'telegram%'
ORDER BY column_name;

