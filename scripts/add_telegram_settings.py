#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tự động thêm Telegram Bot Settings vào settings.py
"""
import os
import re
from pathlib import Path

# Đường dẫn file settings.py
settings_file = Path(__file__).parent.parent / "app" / "api" / "routes" / "settings.py"

def add_imports(content: str) -> str:
    """Thêm import cho telegram_token_service"""
    # Tìm dòng import facebook_token_service
    pattern = r'(from app\.services\.facebook_token_service import[^\n]+\n)'
    match = re.search(pattern, content)
    
    if match:
        # Thêm import sau dòng facebook_token_service
        import_line = match.group(0)
        new_import = "from app.services.telegram_token_service import test_telegram_bot_token\n"
        
        # Kiểm tra xem đã có import này chưa
        if "telegram_token_service" not in content:
            content = content.replace(import_line, import_line + new_import)
    
    return content

def add_schemas(content: str) -> str:
    """Thêm schemas cho Telegram Bot"""
    # Tìm dòng class AccountPrefixLink
    pattern = r'(class AccountPrefixLink\(BaseModel\):[^\n]+\n[^\n]+\n[^\n]+\n)'
    match = re.search(pattern, content)
    
    if match:
        schema_end = match.end()
        # Kiểm tra xem đã có schemas này chưa
        if "class TelegramBotSaveRequest" not in content:
            new_schemas = """
class TelegramBotSaveRequest(BaseModel):
    bot_token: str
    chat_id: str


class TelegramBotTestResponse(BaseModel):
    valid: bool
    status: str
    message: str
    bot_info: Optional[Dict[str, Any]] = None
    chat_info: Optional[Dict[str, Any]] = None


"""
            content = content[:schema_end] + new_schemas + content[schema_end:]
    
    return content

def add_endpoints(content: str) -> str:
    """Thêm endpoints cho Telegram Bot"""
    # Tìm dòng return trong delete_token function
    pattern = r'(\s+return \{"message": "Token đã được xóa thành công"\}\s+\n\s+\n\s+# ==================== ACCOUNTS ENDPOINTS)'
    match = re.search(pattern, content)
    
    if match:
        endpoint_start = match.end() - len("# ==================== ACCOUNTS ENDPOINTS")
        # Kiểm tra xem đã có endpoints này chưa
        if "@router.post(\"/telegram/save\")" not in content:
            new_endpoints = """
# ==================== TELEGRAM BOT ENDPOINTS ====================

@router.post("/telegram/save")
def save_telegram_bot(
    telegram_request: TelegramBotSaveRequest,
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    \"\"\"Lưu Telegram Bot Token và Chat ID cho user (encrypted)\"\"\"
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Test token và chat ID trước khi lưu
    test_result = test_telegram_bot_token(telegram_request.bot_token, telegram_request.chat_id)
    if not test_result["valid"]:
        raise HTTPException(status_code=400, detail=test_result["message"])
    
    # Get or create user settings
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id)
        db.add(user_settings)
    
    # Encrypt và lưu bot token
    user_settings.telegram_bot_token_encrypted = encrypt_token(telegram_request.bot_token)
    user_settings.telegram_chat_id = telegram_request.chat_id
    user_settings.telegram_bot_status = "VALID"
    user_settings.telegram_bot_last_checked = datetime.now()
    user_settings.updated_at = datetime.now()
    
    db.commit()
    db.refresh(user_settings)
    
    return {
        "success": True,
        "message": "Đã lưu Telegram Bot Token và Chat ID thành công",
        "bot_info": test_result.get("bot_info"),
        "chat_info": test_result.get("chat_info")
    }


@router.post("/telegram/test", response_model=TelegramBotTestResponse)
def test_telegram_bot(
    telegram_request: TelegramBotSaveRequest,
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    \"\"\"Test Telegram Bot Token và Chat ID\"\"\"
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    test_result = test_telegram_bot_token(telegram_request.bot_token, telegram_request.chat_id)
    
    return TelegramBotTestResponse(**test_result)


@router.get("/telegram/status")
def get_telegram_bot_status(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    \"\"\"Lấy trạng thái Telegram Bot Token và Chat ID\"\"\"
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not user_settings or not user_settings.telegram_bot_token_encrypted:
        return {
            "status": "NOT_SET",
            "message": "Chưa cấu hình Telegram Bot",
            "bot_token_set": False,
            "chat_id_set": False,
            "last_checked": None
        }
    
    try:
        bot_token = decrypt_token(user_settings.telegram_bot_token_encrypted)
        bot_token_masked = bot_token[:10] + "..." + bot_token[-5:] if len(bot_token) > 15 else "***"
    except Exception as e:
        logger.error(f"Error decrypting Telegram bot token: {e}")
        return {
            "status": "ERROR",
            "message": "Lỗi khi giải mã Bot Token",
            "bot_token_set": True,
            "chat_id_set": bool(user_settings.telegram_chat_id),
            "last_checked": user_settings.telegram_bot_last_checked.isoformat() if user_settings.telegram_bot_last_checked else None
        }
    
    # Format last checked time in Ho Chi Minh timezone
    last_checked_str = None
    if user_settings.telegram_bot_last_checked:
        import pytz
        hcm_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        last_checked_utc = user_settings.telegram_bot_last_checked
        if last_checked_utc.tzinfo is None:
            last_checked_utc = pytz.UTC.localize(last_checked_utc)
        last_checked_hcm = last_checked_utc.astimezone(hcm_tz)
        last_checked_str = last_checked_hcm.strftime("%H:%M:%S %d/%m/%Y")
    
    return {
        "status": user_settings.telegram_bot_status,
        "message": f"Bot Token đã được cấu hình (Kiểm tra lần cuối: {last_checked_str})" if last_checked_str else "Bot Token đã được cấu hình",
        "bot_token_set": True,
        "bot_token_masked": bot_token_masked,
        "chat_id_set": bool(user_settings.telegram_chat_id),
        "chat_id": user_settings.telegram_chat_id if user_settings.telegram_chat_id else None,
        "last_checked": last_checked_str
    }


@router.delete("/telegram/delete")
def delete_telegram_bot(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    \"\"\"Xóa Telegram Bot Token và Chat ID\"\"\"
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not user_settings or not user_settings.telegram_bot_token_encrypted:
        raise HTTPException(status_code=404, detail="Chưa có Telegram Bot Token để xóa")
    
    user_settings.telegram_bot_token_encrypted = None
    user_settings.telegram_chat_id = None
    user_settings.telegram_bot_status = "NOT_SET"
    user_settings.telegram_bot_last_checked = None
    db.commit()
    
    return {"message": "Telegram Bot Token và Chat ID đã được xóa thành công"}


"""
            content = content[:endpoint_start] + new_endpoints + content[endpoint_start:]
    
    return content

def add_ui_section(content: str) -> str:
    """Thêm section UI cho Telegram Bot vào HTML"""
    # Tìm section Quản Lý Prefixes
    pattern = r'(<!-- Section 3: Quản Lý Prefixes -->)'
    match = re.search(pattern, content)
    
    if match:
        section_start = match.start()
        # Kiểm tra xem đã có section này chưa
        if "<!-- Section 4: Telegram Bot -->" not in content:
            new_section = """
            <!-- Section 4: Telegram Bot -->
            <div class="section">
                <div class="section-title">
                    <span class="icon">📱</span>
                    <span>Telegram Bot</span>
                </div>
                
                <div id="telegramStatus" class="token-status not-set">
                    Đang kiểm tra trạng thái...
                </div>
                
                <div id="telegramInfo" style="display: none; margin-bottom: 20px; padding: 16px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>Bot Token đã lưu:</strong>
                            <span id="telegramTokenMasked" style="font-family: monospace; color: #64748b; margin-left: 8px;"></span>
                            <br>
                            <strong>Chat ID:</strong>
                            <span id="telegramChatId" style="font-family: monospace; color: #64748b; margin-left: 8px;"></span>
                        </div>
                        <button class="btn btn-danger" onclick="deleteTelegramBot()" style="padding: 6px 12px; font-size: 12px;">🗑️ Xóa Cấu Hình</button>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Bot Token *</label>
                    <input type="password" id="telegramBotToken" placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz" />
                    <small style="color: #64748b; margin-top: 4px; display: block;">Lấy Bot Token từ @BotFather trên Telegram</small>
                </div>
                
                <div class="form-group">
                    <label>Chat ID (Group ID) *</label>
                    <input type="text" id="telegramChatIdInput" placeholder="-1001234567890" />
                    <small style="color: #64748b; margin-top: 4px; display: block;">Chat ID phải là số âm (Group ID). Lấy Chat ID bằng cách thêm bot vào nhóm và gửi message, sau đó dùng getUpdates API.</small>
                </div>
                
                <div style="display: flex; gap: 12px;">
                    <button class="btn btn-primary" onclick="saveTelegramBot()">💾 Lưu Cấu Hình</button>
                    <button class="btn btn-secondary" onclick="testTelegramBot()">✅ Kiểm Tra</button>
                </div>
                
                <div id="telegramTestResult" style="margin-top: 20px;"></div>
            </div>
            
"""
            content = content[:section_start] + new_section + content[section_start:]
    
    return content

def add_javascript_functions(content: str) -> str:
    """Thêm JavaScript functions cho Telegram Bot"""
    # Tìm function loadPrefixes
    pattern = r'(async function loadPrefixes\(\)[^}]+})'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        js_end = match.end()
        # Kiểm tra xem đã có functions này chưa
        if "async function loadTelegramStatus()" not in content:
            new_js = """
            // Telegram Bot Functions
            async function loadTelegramStatus() {
                try {
                    const response = await fetch('/settings/telegram/status', {
                        headers: getAuthHeaders()
                    });
                    
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                    }
                    
                    const data = await response.json();
                    const statusDiv = document.getElementById('telegramStatus');
                    const infoDiv = document.getElementById('telegramInfo');
                    
                    if (data.status === 'NOT_SET') {
                        statusDiv.className = 'token-status not-set';
                        statusDiv.textContent = '❌ Chưa cấu hình Telegram Bot';
                        infoDiv.style.display = 'none';
                    } else if (data.status === 'VALID') {
                        statusDiv.className = 'token-status valid';
                        statusDiv.innerHTML = '✅ ' + data.message;
                        infoDiv.style.display = 'block';
                        document.getElementById('telegramTokenMasked').textContent = data.bot_token_masked || '***';
                        document.getElementById('telegramChatId').textContent = data.chat_id || 'Chưa có';
                    } else {
                        statusDiv.className = 'token-status invalid';
                        statusDiv.innerHTML = '❌ ' + data.message;
                        infoDiv.style.display = 'none';
                    }
                } catch (error) {
                    console.error('Error loading Telegram status:', error);
                    const statusDiv = document.getElementById('telegramStatus');
                    statusDiv.className = 'token-status invalid';
                    statusDiv.textContent = '❌ Lỗi khi tải trạng thái: ' + error.message;
                }
            }
            
            async function saveTelegramBot() {
                const botToken = document.getElementById('telegramBotToken').value.trim();
                const chatId = document.getElementById('telegramChatIdInput').value.trim();
                
                if (!botToken) {
                    showToast('Vui lòng nhập Bot Token', 'error');
                    return;
                }
                
                if (!chatId) {
                    showToast('Vui lòng nhập Chat ID', 'error');
                    return;
                }
                
                try {
                    const response = await fetch('/settings/telegram/save', {
                        method: 'POST',
                        headers: {
                            ...getAuthHeaders(),
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            bot_token: botToken,
                            chat_id: chatId
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok && data.success) {
                        showToast('Đã lưu cấu hình Telegram Bot thành công!');
                        document.getElementById('telegramBotToken').value = '';
                        document.getElementById('telegramChatIdInput').value = '';
                        loadTelegramStatus();
                    } else {
                        showToast(data.message || data.detail || 'Lỗi khi lưu cấu hình', 'error');
                    }
                } catch (error) {
                    console.error('Error saving Telegram bot:', error);
                    showToast('Lỗi khi lưu cấu hình: ' + error.message, 'error');
                }
            }
            
            async function testTelegramBot() {
                const botToken = document.getElementById('telegramBotToken').value.trim();
                const chatId = document.getElementById('telegramChatIdInput').value.trim();
                
                if (!botToken) {
                    showToast('Vui lòng nhập Bot Token', 'error');
                    return;
                }
                
                if (!chatId) {
                    showToast('Vui lòng nhập Chat ID', 'error');
                    return;
                }
                
                const resultDiv = document.getElementById('telegramTestResult');
                resultDiv.innerHTML = '<div class="loading">Đang kiểm tra...</div>';
                
                try {
                    const response = await fetch('/settings/telegram/test', {
                        method: 'POST',
                        headers: {
                            ...getAuthHeaders(),
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            bot_token: botToken,
                            chat_id: chatId
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.valid) {
                        let html = '<div style="padding: 16px; background: #d1fae5; border-radius: 8px; border: 1px solid #10b981;">';
                        html += '<strong>✅ ' + data.message + '</strong><br>';
                        if (data.bot_info) {
                            html += '<br><strong>Thông tin Bot:</strong><br>';
                            html += 'Username: @' + (data.bot_info.username || 'N/A') + '<br>';
                            html += 'Tên: ' + (data.bot_info.first_name || 'N/A') + '<br>';
                        }
                        if (data.chat_info) {
                            html += '<br><strong>Thông tin Chat:</strong><br>';
                            html += 'Tên: ' + (data.chat_info.title || data.chat_info.first_name || 'N/A') + '<br>';
                            html += 'Loại: ' + (data.chat_info.type || 'N/A') + '<br>';
                        }
                        html += '</div>';
                        resultDiv.innerHTML = html;
                    } else {
                        resultDiv.innerHTML = '<div style="padding: 16px; background: #fee2e2; border-radius: 8px; border: 1px solid #ef4444;"><strong>❌ ' + data.message + '</strong></div>';
                    }
                } catch (error) {
                    console.error('Error testing Telegram bot:', error);
                    resultDiv.innerHTML = '<div style="padding: 16px; background: #fee2e2; border-radius: 8px; border: 1px solid #ef4444;"><strong>❌ Lỗi khi kiểm tra: ' + error.message + '</strong></div>';
                }
            }
            
            async function deleteTelegramBot() {
                if (!confirm('Bạn có chắc muốn xóa cấu hình Telegram Bot?')) {
                    return;
                }
                
                try {
                    const response = await fetch('/settings/telegram/delete', {
                        method: 'DELETE',
                        headers: getAuthHeaders()
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        showToast('Đã xóa cấu hình Telegram Bot thành công!');
                        loadTelegramStatus();
                    } else {
                        showToast(data.message || data.detail || 'Lỗi khi xóa cấu hình', 'error');
                    }
                } catch (error) {
                    console.error('Error deleting Telegram bot:', error);
                    showToast('Lỗi khi xóa cấu hình: ' + error.message, 'error');
                }
            }
            
"""
            # Tìm vị trí cuối cùng của script tag
            script_end_pattern = r'(</script>\s*</body>\s*</html>)'
            script_end_match = re.search(script_end_pattern, content)
            
            if script_end_match:
                script_end = script_end_match.start()
                content = content[:script_end] + new_js + content[script_end:]
    
    return content

def add_initialize_call(content: str) -> str:
    """Thêm lời gọi loadTelegramStatus vào initializePage"""
    # Tìm initializePage function
    pattern = r'(async function initializePage\(\)[^}]+loadPrefixes\(\)[^}]+})'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Thêm loadTelegramStatus() sau loadPrefixes()
        if "loadTelegramStatus()" not in match.group(0):
            new_content = match.group(0).replace(
                "await loadPrefixes();",
                "await loadPrefixes();\n                await loadTelegramStatus();"
            )
            content = content.replace(match.group(0), new_content)
    
    return content

def main():
    """Main function"""
    print("🔧 Đang thêm Telegram Bot Settings vào settings.py...")
    
    if not settings_file.exists():
        print(f"❌ Không tìm thấy file: {settings_file}")
        return
    
    # Đọc file
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Thêm các phần
    print("1. Thêm imports...")
    content = add_imports(content)
    
    print("2. Thêm schemas...")
    content = add_schemas(content)
    
    print("3. Thêm endpoints...")
    content = add_endpoints(content)
    
    print("4. Thêm UI section...")
    content = add_ui_section(content)
    
    print("5. Thêm JavaScript functions...")
    content = add_javascript_functions(content)
    
    print("6. Thêm initialize call...")
    content = add_initialize_call(content)
    
    # Backup file cũ
    backup_file = settings_file.with_suffix('.py.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Đã backup file cũ: {backup_file}")
    
    # Ghi file mới
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Đã thêm Telegram Bot Settings thành công!")
    print(f"📁 File: {settings_file}")

if __name__ == "__main__":
    main()

