# -*- coding: utf-8 -*-
"""
User Profile Routes - Quản lý thông tin cá nhân
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging
import os
import shutil
import base64

from app.core.database import get_db
from app.models.user import User
from app.core.security import verify_password, get_password_hash, get_current_user
from app.api.routes.auth import get_current_user_optional

router = APIRouter(prefix="/profile", tags=["profile"])
change_password_router = APIRouter(tags=["profile"])  # Router riêng cho change-password không có prefix
logger = logging.getLogger(__name__)

# Schemas
class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


def _get_profile_css():
    """CSS cho trang profile"""
    return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .profile-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        .profile-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            text-align: center;
            color: white;
        }
        
        .profile-header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .profile-header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .profile-content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .section:last-child {
            border-bottom: none;
        }
        
        .section-title {
            font-size: 20px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-title .icon {
            font-size: 24px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            font-weight: 500;
            color: #374151;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-group input:disabled {
            background: #f3f4f6;
            cursor: not-allowed;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
        }
        
        .btn-secondary {
            background: #6b7280;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #4b5563;
        }
        
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        
        .btn-danger:hover {
            background: #dc2626;
        }
        
        .avatar-section {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .avatar-preview {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid #667eea;
        }
        
        .avatar-placeholder {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 36px;
            font-weight: 600;
            border: 4px solid #667eea;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f3f4f6;
        }
        
        .info-item:last-child {
            border-bottom: none;
        }
        
        .info-label {
            font-weight: 500;
            color: #6b7280;
        }
        
        .info-value {
            color: #1f2937;
            font-weight: 500;
        }
        
        .back-link {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: #667eea;
            text-decoration: none;
            margin-bottom: 20px;
            font-weight: 500;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        }
        
        .toast.success {
            background: #10b981;
        }
        
        .toast.error {
            background: #ef4444;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    </style>
    """


@router.get("/", response_class=HTMLResponse)
def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user_optional)
):
    """Trang profile của user"""
    if not current_user:
        return HTMLResponse(content="""
        <script>
            window.location.href = '/auth/login';
        </script>
        """)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Thông Tin Tài Khoản - {current_user.display_name}</title>
        {_get_profile_css()}
    </head>
    <body>
        <div class="profile-container">
            <div class="profile-header">
                <h1>👤 Thông Tin Tài Khoản</h1>
                <p>Quản lý thông tin cá nhân và cài đặt</p>
            </div>
            
            <div class="profile-content">
                <a href="/" class="back-link">← Về Trang Chủ</a>
                
                <!-- Section 1: Thông Tin Cơ Bản -->
                <div class="section">
                    <div class="section-title">
                        <span class="icon">📋</span>
                        <span>Thông Tin Cơ Bản</span>
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">Tên đăng nhập:</span>
                        <span class="info-value">{current_user.username}</span>
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">Email:</span>
                        <span class="info-value">{current_user.email}</span>
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">Tên hiển thị:</span>
                        <span class="info-value" id="displayNameValue">{current_user.display_name or current_user.username}</span>
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">Vai trò:</span>
                        <span class="info-value">{'👑 Quản trị viên' if current_user.role == 'admin' else '👤 Người dùng'}</span>
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">Ngày tạo tài khoản:</span>
                        <span class="info-value">{current_user.created_at.strftime('%d/%m/%Y %H:%M') if current_user.created_at else 'N/A'}</span>
                    </div>
                </div>
                
                <!-- Section 2: Avatar -->
                <div class="section">
                    <div class="section-title">
                        <span class="icon">🖼️</span>
                        <span>Ảnh Đại Diện</span>
                    </div>
                    
                    <div class="avatar-section">
                        <div id="avatarPreview">
                            {('<img src="/static/avatars/' + current_user.avatar + '" class="avatar-preview" alt="Avatar" onerror="handleAvatarError(this)">') if current_user.avatar and current_user.avatar != 'default_avatar.png' else ''}
                            <div class="avatar-placeholder" style="display: {'none' if current_user.avatar and current_user.avatar != 'default_avatar.png' else 'flex'}">
                                {(current_user.display_name or current_user.username)[0].upper()}
                            </div>
                        </div>
                        <div>
                            <input type="file" id="avatarInput" accept="image/*" style="display: none;" onchange="handleAvatarChange(event)">
                            <button class="btn btn-primary" onclick="document.getElementById('avatarInput').click()">
                                📤 Chọn Ảnh
                            </button>
                            <button class="btn btn-secondary" onclick="removeAvatar()" style="margin-top: 10px;">
                                🗑️ Xóa Ảnh
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Section 3: Chỉnh Sửa Thông Tin -->
                <div class="section">
                    <div class="section-title">
                        <span class="icon">✏️</span>
                        <span>Chỉnh Sửa Thông Tin</span>
                    </div>
                    
                    <div class="form-group">
                        <label for="editDisplayName">Tên hiển thị:</label>
                        <input type="text" id="editDisplayName" value="{current_user.display_name or ''}" placeholder="Nhập tên hiển thị">
                    </div>
                    
                    <div class="form-group">
                        <label for="editEmail">Email:</label>
                        <input type="email" id="editEmail" value="{current_user.email}" placeholder="Nhập email">
                    </div>
                    
                    <button class="btn btn-primary" onclick="updateProfile()">
                        💾 Lưu Thay Đổi
                    </button>
                </div>
                
            </div>
        </div>
        
        <script>
            function getAuthHeaders() {{
                const token = localStorage.getItem('access_token') || getCookie('access_token');
                return {{
                    'Authorization': `Bearer ${{token}}`,
                    'Content-Type': 'application/json'
                }};
            }}
            
            function getCookie(name) {{
                const value = `; ${{document.cookie}}`;
                const parts = value.split(`; ${{name}}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }}
            
            function showToast(message, type = 'success') {{
                const toast = document.createElement('div');
                toast.className = `toast ${{type}}`;
                toast.textContent = message;
                document.body.appendChild(toast);
                
                setTimeout(() => {{
                    toast.remove();
                }}, 3000);
            }}
            
            function handleAvatarError(img) {{
                img.style.display = 'none';
                const placeholder = img.nextElementSibling;
                if (placeholder) {{
                    placeholder.style.display = 'flex';
                }}
            }}
            
            function handleAvatarChange(event) {{
                const file = event.target.files[0];
                if (!file) return;
                
                if (file.size > 5 * 1024 * 1024) {{
                    showToast('Ảnh không được vượt quá 5MB', 'error');
                    return;
                }}
                
                const reader = new FileReader();
                reader.onload = function(e) {{
                    const preview = document.getElementById('avatarPreview');
                    preview.innerHTML = `<img src="${{e.target.result}}" class="avatar-preview" alt="Avatar">`;
                }};
                reader.readAsDataURL(file);
                
                // Upload avatar
                const formData = new FormData();
                formData.append('avatar', file);
                
                fetch('/profile/avatar', {{
                    method: 'POST',
                    headers: {{
                        'Authorization': `Bearer ${{localStorage.getItem('access_token') || getCookie('access_token')}}`
                    }},
                    body: formData
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        showToast('Cập nhật ảnh đại diện thành công!');
                        // Reload page to show new avatar
                        setTimeout(() => {{
                            window.location.reload();
                        }}, 1000);
                    }} else {{
                        showToast(data.message || 'Lỗi khi cập nhật ảnh', 'error');
                    }}
                }})
                .catch(error => {{
                    console.error('Error uploading avatar:', error);
                    showToast('Lỗi khi cập nhật ảnh', 'error');
                }});
            }}
            
            function removeAvatar() {{
                if (!confirm('Bạn có chắc muốn xóa ảnh đại diện?')) return;
                
                fetch('/profile/avatar', {{
                    method: 'DELETE',
                    headers: getAuthHeaders()
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        const preview = document.getElementById('avatarPreview');
                        const displayName = '{current_user.display_name or current_user.username}';
                        preview.innerHTML = `<div class="avatar-placeholder" style="display: flex;">${{displayName[0].toUpperCase()}}</div>`;
                        showToast('Đã xóa ảnh đại diện');
                    }} else {{
                        showToast(data.message || 'Lỗi khi xóa ảnh', 'error');
                    }}
                }})
                .catch(error => {{
                    showToast('Lỗi khi xóa ảnh', 'error');
                }});
            }}
            
            function updateProfile() {{
                const displayName = document.getElementById('editDisplayName').value.trim();
                const email = document.getElementById('editEmail').value.trim();
                
                if (!displayName) {{
                    showToast('Vui lòng nhập tên hiển thị', 'error');
                    return;
                }}
                
                if (!email) {{
                    showToast('Vui lòng nhập email', 'error');
                    return;
                }}
                
                fetch('/profile/update', {{
                    method: 'PUT',
                    headers: getAuthHeaders(),
                    body: JSON.stringify({{
                        display_name: displayName,
                        email: email
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        document.getElementById('displayNameValue').textContent = displayName;
                        showToast('Cập nhật thông tin thành công!');
                    }} else {{
                        showToast(data.message || 'Lỗi khi cập nhật', 'error');
                    }}
                }})
                .catch(error => {{
                    showToast('Lỗi khi cập nhật', 'error');
                }});
            }}
            
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.put("/update")
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin profile"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Check email uniqueness if changed
    if profile_data.email and profile_data.email != current_user.email:
        existing = db.query(User).filter(User.email == profile_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email đã được sử dụng")
        current_user.email = profile_data.email
    
    if profile_data.display_name:
        current_user.display_name = profile_data.display_name
    
    current_user.updated_at = datetime.now()
    db.commit()
    
    return {"success": True, "message": "Cập nhật thông tin thành công"}


@router.put("/password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Đổi mật khẩu"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng")
    
    # Check new password match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(status_code=400, detail="Mật khẩu mới không khớp")
    
    # Check password length
    if len(password_data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải có ít nhất 6 ký tự")
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.now()
    db.commit()
    
    return {"success": True, "message": "Đổi mật khẩu thành công"}


@router.post("/avatar")
def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Upload avatar"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Check file type
    if not avatar.content_type or not avatar.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file ảnh")
    
    # Create avatars directory if not exists
    avatars_dir = "app/static/avatars"
    os.makedirs(avatars_dir, exist_ok=True)
    
    # Read file content to check size
    file_content = avatar.file.read()
    file_size = len(file_content)
    
    # Check file size (max 5MB)
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Ảnh không được vượt quá 5MB")
    
    # Reset file pointer
    avatar.file.seek(0)
    
    # Generate filename
    file_ext = avatar.filename.split('.')[-1] if '.' in avatar.filename else 'png'
    filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_ext}"
    filepath = os.path.join(avatars_dir, filename)
    
    # Save file
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
    except Exception as e:
        logger.error(f"Error saving avatar file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu file: {str(e)}")
    
    # Delete old avatar if exists
    if current_user.avatar and current_user.avatar != 'default_avatar.png':
        old_filepath = os.path.join(avatars_dir, current_user.avatar)
        if os.path.exists(old_filepath):
            try:
                os.remove(old_filepath)
            except Exception as e:
                logger.warning(f"Error deleting old avatar: {e}")
    
    # Update user
    try:
        current_user.avatar = filename
        current_user.updated_at = datetime.now()
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user avatar: {e}", exc_info=True)
        # Delete the uploaded file if database update fails
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật database: {str(e)}")
    
    return {"success": True, "message": "Cập nhật ảnh đại diện thành công", "avatar": filename}


@router.delete("/avatar")
def remove_avatar(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Xóa avatar"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Delete avatar file if exists
    if current_user.avatar and current_user.avatar != 'default_avatar.png':
        avatars_dir = "app/static/avatars"
        filepath = os.path.join(avatars_dir, current_user.avatar)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    # Reset to default
    current_user.avatar = 'default_avatar.png'
    current_user.updated_at = datetime.now()
    db.commit()
    
    return {"success": True, "message": "Đã xóa ảnh đại diện"}


@change_password_router.get("/change-password", response_class=HTMLResponse)
def change_password_page(
    request: Request,
    current_user: User = Depends(get_current_user_optional)
):
    """Trang thay đổi mật khẩu riêng biệt"""
    if not current_user:
        return HTMLResponse(content="""
        <script>
            window.location.href = '/auth/login';
        </script>
        """)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Thay Đổi Mật Khẩu - {current_user.display_name}</title>
        {_get_profile_css()}
    </head>
    <body>
        <div class="profile-container">
            <div class="profile-header">
                <h1>🔒 Thay Đổi Mật Khẩu</h1>
                <p>Bảo mật tài khoản của bạn</p>
            </div>
            
            <div class="profile-content">
                <a href="/" class="back-link">← Về Trang Chủ</a>
                
                <div class="section">
                    <div class="section-title">
                        <span class="icon">🔐</span>
                        <span>Đổi Mật Khẩu</span>
                    </div>
                    
                    <div class="form-group">
                        <label for="currentPassword">Mật khẩu hiện tại:</label>
                        <input type="password" id="currentPassword" placeholder="Nhập mật khẩu hiện tại">
                    </div>
                    
                    <div class="form-group">
                        <label for="newPassword">Mật khẩu mới:</label>
                        <input type="password" id="newPassword" placeholder="Nhập mật khẩu mới (tối thiểu 6 ký tự)">
                    </div>
                    
                    <div class="form-group">
                        <label for="confirmPassword">Xác nhận mật khẩu mới:</label>
                        <input type="password" id="confirmPassword" placeholder="Nhập lại mật khẩu mới">
                    </div>
                    
                    <button class="btn btn-primary" onclick="changePassword()">
                        🔄 Đổi Mật Khẩu
                    </button>
                </div>
            </div>
        </div>
        
        <script>
            function getAuthHeaders() {{
                const token = localStorage.getItem('access_token') || getCookie('access_token');
                return {{
                    'Authorization': 'Bearer ' + token,
                    'Content-Type': 'application/json'
                }};
            }}
            
            function getCookie(name) {{
                const value = '; ' + document.cookie;
                const parts = value.split('; ' + name + '=');
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }}
            
            function showToast(message, type = 'success') {{
                const toast = document.createElement('div');
                toast.className = 'toast ' + type;
                toast.textContent = message;
                document.body.appendChild(toast);
                
                setTimeout(() => {{
                    toast.remove();
                }}, 3000);
            }}
            
            function changePassword() {{
                const currentPassword = document.getElementById('currentPassword').value;
                const newPassword = document.getElementById('newPassword').value;
                const confirmPassword = document.getElementById('confirmPassword').value;
                
                if (!currentPassword || !newPassword || !confirmPassword) {{
                    showToast('Vui lòng điền đầy đủ thông tin', 'error');
                    return;
                }}
                
                if (newPassword !== confirmPassword) {{
                    showToast('Mật khẩu mới không khớp', 'error');
                    return;
                }}
                
                if (newPassword.length < 6) {{
                    showToast('Mật khẩu mới phải có ít nhất 6 ký tự', 'error');
                    return;
                }}
                
                fetch('/profile/password', {{
                    method: 'PUT',
                    headers: getAuthHeaders(),
                    body: JSON.stringify({{
                        current_password: currentPassword,
                        new_password: newPassword,
                        confirm_password: confirmPassword
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        document.getElementById('currentPassword').value = '';
                        document.getElementById('newPassword').value = '';
                        document.getElementById('confirmPassword').value = '';
                        showToast('Đổi mật khẩu thành công!');
                        setTimeout(() => {{
                            window.location.href = '/profile';
                        }}, 1500);
                    }} else {{
                        showToast(data.message || 'Lỗi khi đổi mật khẩu', 'error');
                    }}
                }})
                .catch(error => {{
                    showToast('Lỗi khi đổi mật khẩu', 'error');
                }});
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

