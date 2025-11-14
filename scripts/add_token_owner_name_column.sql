-- Add token_owner_name column to user_settings table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'user_settings' 
        AND column_name = 'token_owner_name'
    ) THEN
        ALTER TABLE user_settings 
        ADD COLUMN token_owner_name VARCHAR(255);
        
        RAISE NOTICE 'Added token_owner_name column to user_settings table';
    ELSE
        RAISE NOTICE 'Column token_owner_name already exists in user_settings table';
    END IF;
END $$;

