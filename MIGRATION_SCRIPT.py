"""
Migration Script
Migrate dữ liệu từ Google Sheets sang PostgreSQL
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from app.core.database import get_db_session, LogicRule, RuleTemplate
from app.services.rule_template_service import initialize_default_templates
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_logic_rules_from_sheets():
    """
    Migrate Logic Rules từ Google Sheets sang PostgreSQL
    Cần setup Google Sheets API credentials trước
    """
    # Setup Google Sheets API
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Cần file credentials.json từ Google Cloud Console
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json', scope
    )
    client = gspread.authorize(creds)
    
    # Mở spreadsheet (cần share với service account email)
    spreadsheet_id = 'YOUR_SPREADSHEET_ID'
    sheet = client.open_by_key(spreadsheet_id)
    
    # Đọc LogicRules sheet
    logic_sheet = sheet.worksheet('LogicRules')
    data = logic_sheet.get_all_values()
    
    if len(data) < 2:
        logger.error("LogicRules sheet không có dữ liệu")
        return
    
    headers = data[0]  # Hàng 1: Headers
    rows = data[1:]    # Hàng 2 trở đi: Data
    
    db = get_db_session()
    try:
        # Parse headers (format: "act_xxx|PREFIX")
        account_prefix_map = {}
        for col_idx, header in enumerate(headers):
            if col_idx < 2:  # Bỏ qua cột A (KEY) và B (Ghi chú)
                continue
            
            if '|' in header:
                parts = header.split('|')
                if len(parts) >= 2:
                    account_id = parts[0].strip()
                    prefix = parts[1].strip()
                    account_prefix_map[col_idx] = {
                        'account_id': account_id,
                        'prefix': prefix
                    }
        
        # Parse rows
        for row_idx, row in enumerate(rows):
            logic_name = row[0] if len(row) > 0 else ''
            if not logic_name or logic_name.startswith('LOGIC'):
                continue
            
            # Parse logic type
            logic_type = None
            if 'SL_1' in logic_name:
                logic_type = 'logic1'
            elif 'SL_2' in logic_name:
                logic_type = 'logic2'
            elif 'SL_3' in logic_name:
                logic_type = 'logic3'
            
            if not logic_type:
                continue
            
            # Tạo rules cho từng account/prefix
            for col_idx, ap_info in account_prefix_map.items():
                if col_idx >= len(row):
                    continue
                
                value = row[col_idx]
                if not value or value == '':
                    continue
                
                try:
                    num_value = float(str(value).replace(',', '.'))
                except:
                    continue
                
                # Tạo LogicRule
                rule = LogicRule(
                    account_id=ap_info['account_id'],
                    prefix=ap_info['prefix'],
                    giai_doan='GĐ1',  # Có thể parse từ logic_name
                    logic_type=logic_type,
                    enabled=True
                )
                
                # Set conditions dựa trên logic type
                if logic_type == 'logic1':
                    if 'SPEND' in logic_name:
                        rule.condition_spend = num_value
                    elif 'KET_QUA' in logic_name:
                        rule.condition_results = int(num_value)
                elif logic_type == 'logic2':
                    if 'SPEND' in logic_name:
                        rule.condition_spend = num_value
                    elif 'GIA_DATA' in logic_name:
                        rule.condition_gia_data = num_value
                elif logic_type == 'logic3':
                    if 'SPEND' in logic_name:
                        rule.condition_spend = num_value
                    elif 'KET_QUA' in logic_name:
                        rule.condition_results = int(num_value)
                
                db.add(rule)
        
        db.commit()
        logger.info("✅ Đã migrate Logic Rules từ Google Sheets")
        
    except Exception as e:
        db.rollback()
        logger.error(f"🚨 Lỗi migrate: {e}")
    finally:
        db.close()


def migrate_settings_from_sheets():
    """
    Migrate Settings từ CaiDat sheet sang .env hoặc database
    """
    # Tương tự migrate_logic_rules_from_sheets()
    # Đọc CaiDat sheet và update .env hoặc system_settings table
    pass


if __name__ == "__main__":
    print("🚀 Bắt đầu migration...")
    
    # Initialize default templates trước
    print("📋 Initializing default templates...")
    initialize_default_templates()
    
    # Migrate logic rules (nếu có Google Sheets API setup)
    # print("📋 Migrating Logic Rules from Google Sheets...")
    # migrate_logic_rules_from_sheets()
    
    print("✅ Migration completed!")

