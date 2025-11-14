# -*- coding: utf-8 -*-
"""
User Management Routes - Quản lý người dùng (Admin only)
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash, get_current_user
from app.api.routes.auth import get_current_user_optional

router = APIRouter(prefix="/admin/users", tags=["user_management"])
logger = logging.getLogger(__name__)


def require_admin(current_user: User = Depends(get_current_user_optional)):
    """Dependency để yêu cầu quyền admin"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên mới có quyền truy cập")
    return current_user


# Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    display_name: Optional[str] = None
    role: str = "user"

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


def _get_user_management_css():
    """CSS cho trang quản lý người dùng"""
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
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            color: white;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .content {
            padding: 40px;
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
        
        .section {
            margin-bottom: 40px;
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
        
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        
        .btn-danger:hover {
            background: #dc2626;
        }
        
        .btn-success {
            background: #10b981;
            color: white;
        }
        
        .btn-success:hover {
            background: #059669;
        }
        
        .btn-warning {
            background: #f59e0b;
            color: white;
        }
        
        .btn-warning:hover {
            background: #d97706;
        }
        
        .table-container {
            overflow-x: auto;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        
        th {
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
        }
        
        tr:hover {
            background: #f9fafb;
        }
        
        .badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .badge-admin {
            background: #fef3c7;
            color: #92400e;
        }
        
        .badge-user {
            background: #dbeafe;
            color: #1e40af;
        }
        
        .badge-active {
            background: #d1fae5;
            color: #065f46;
        }
        
        .badge-inactive {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: white;
            border-radius: 16px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .modal-header {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
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
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .modal-actions {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            margin-top: 20px;
        }
        
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 2000;
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
def user_management_page(
    request: Request,
    admin_user: User = Depends(require_admin)
):
    """Trang quản lý người dùng (Admin only)"""
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quản Lý Người Dùng - Admin</title>
        {_get_user_management_css()}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>👥 Quản Lý Người Dùng</h1>
                <p>Thêm, sửa, xóa và khóa tài khoản người dùng</p>
            </div>
            
            <div class="content">
                <a href="/" class="back-link">← Về Trang Chủ</a>
                
                <div class="section">
                    <div class="section-title">
                        <span>📋 Danh Sách Người Dùng</span>
                        <button class="btn btn-primary" onclick="showAddUserModal()" style="margin-left: auto;">
                            ➕ Thêm Người Dùng
                        </button>
                    </div>
                    
                    <div class="table-container">
                        <table id="usersTable">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Tên đăng nhập</th>
                                    <th>Email</th>
                                    <th>Tên hiển thị</th>
                                    <th>Vai trò</th>
                                    <th>Trạng thái</th>
                                    <th>Ngày tạo</th>
                                    <th>Thao tác</th>
                                </tr>
                            </thead>
                            <tbody id="usersTableBody">
                                <tr>
                                    <td colspan="8" style="text-align: center; padding: 40px;">
                                        <div class="loading">Đang tải...</div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Add/Edit User Modal -->
        <div id="userModal" class="modal">
            <div class="modal-content">
                <div class="modal-header" id="modalTitle">Thêm Người Dùng</div>
                <form id="userForm" onsubmit="event.preventDefault(); saveUser();">
                    <input type="hidden" id="userId" value="">
                    
                    <div class="form-group">
                        <label for="username">Tên đăng nhập *</label>
                        <input type="text" id="username" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email *</label>
                        <input type="email" id="email" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password" id="passwordLabel">Mật khẩu *</label>
                        <input type="password" id="password">
                    </div>
                    
                    <div class="form-group">
                        <label for="displayName">Tên hiển thị</label>
                        <input type="text" id="displayName">
                    </div>
                    
                    <div class="form-group">
                        <label for="role">Vai trò *</label>
                        <select id="role" required>
                            <option value="user">Người dùng</option>
                            <option value="admin">Quản trị viên</option>
                        </select>
                    </div>
                    
                    <div class="form-group" id="isActiveGroup" style="display: none;">
                        <label>
                            <input type="checkbox" id="isActive" checked>
                            Tài khoản hoạt động
                        </label>
                    </div>
                    
                    <div class="modal-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeUserModal()">Hủy</button>
                        <button type="submit" class="btn btn-primary">Lưu</button>
                    </div>
                </form>
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
            
            function loadUsers() {{
                fetch('/admin/users/list', {{
                    headers: getAuthHeaders()
                }})
                .then(response => response.json())
                .then(data => {{
                    const tbody = document.getElementById('usersTableBody');
                    if (data.length === 0) {{
                        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px;">Không có người dùng nào</td></tr>';
                        return;
                    }}
                    
                    tbody.innerHTML = data.map(user => `
                        <tr>
                            <td>${{user.id}}</td>
                            <td>${{user.username}}</td>
                            <td>${{user.email}}</td>
                            <td>${{user.display_name || user.username}}</td>
                            <td><span class="badge badge-${{user.role}}">${{user.role === 'admin' ? '👑 Admin' : '👤 User'}}</span></td>
                            <td><span class="badge badge-${{user.is_active ? 'active' : 'inactive'}}">${{user.is_active ? 'Hoạt động' : 'Đã khóa'}}</span></td>
                            <td>${{new Date(user.created_at).toLocaleDateString('vi-VN')}}</td>
                            <td>
                                <button class="btn btn-primary" onclick="editUser(${{user.id}})" style="padding: 6px 12px; font-size: 12px;">✏️ Sửa</button>
                                <button class="btn btn-${{user.is_active ? 'warning' : 'success'}}" onclick="toggleUserStatus(${{user.id}}, ${{!user.is_active}})" style="padding: 6px 12px; font-size: 12px;">
                                    ${{user.is_active ? '🔒 Khóa' : '🔓 Mở khóa'}}
                                </button>
                                <button class="btn btn-danger" onclick="deleteUser(${{user.id}})" style="padding: 6px 12px; font-size: 12px;">🗑️ Xóa</button>
                            </td>
                        </tr>
                    `).join('');
                }})
                .catch(error => {{
                    showToast('Lỗi khi tải danh sách người dùng', 'error');
                }});
            }}
            
            function showAddUserModal() {{
                document.getElementById('modalTitle').textContent = 'Thêm Người Dùng';
                document.getElementById('userId').value = '';
                document.getElementById('username').value = '';
                document.getElementById('email').value = '';
                document.getElementById('password').value = '';
                document.getElementById('passwordLabel').innerHTML = 'Mật khẩu *';
                document.getElementById('password').required = true;
                document.getElementById('displayName').value = '';
                document.getElementById('role').value = 'user';
                document.getElementById('isActiveGroup').style.display = 'none';
                document.getElementById('userModal').classList.add('active');
            }}
            
            function editUser(userId) {{
                fetch(`/admin/users/${{userId}}`, {{
                    headers: getAuthHeaders()
                }})
                .then(response => response.json())
                .then(user => {{
                    document.getElementById('modalTitle').textContent = 'Sửa Người Dùng';
                    document.getElementById('userId').value = user.id;
                    document.getElementById('username').value = user.username;
                    document.getElementById('username').disabled = true;
                    document.getElementById('email').value = user.email;
                    document.getElementById('password').value = '';
                    document.getElementById('passwordLabel').innerHTML = 'Mật khẩu mới (để trống nếu không đổi)';
                    document.getElementById('password').required = false;
                    document.getElementById('displayName').value = user.display_name || '';
                    document.getElementById('role').value = user.role;
                    document.getElementById('isActive').checked = user.is_active;
                    document.getElementById('isActiveGroup').style.display = 'block';
                    document.getElementById('userModal').classList.add('active');
                }})
                .catch(error => {{
                    showToast('Lỗi khi tải thông tin người dùng', 'error');
                }});
            }}
            
            function closeUserModal() {{
                document.getElementById('userModal').classList.remove('active');
                document.getElementById('username').disabled = false;
            }}
            
            function saveUser() {{
                const userId = document.getElementById('userId').value;
                const data = {{
                    username: document.getElementById('username').value,
                    email: document.getElementById('email').value,
                    display_name: document.getElementById('displayName').value || null,
                    role: document.getElementById('role').value,
                    is_active: document.getElementById('isActive').checked
                }};
                
                const password = document.getElementById('password').value;
                if (password) {{
                    data.password = password;
                }}
                
                const url = userId ? `/admin/users/${{userId}}` : '/admin/users';
                const method = userId ? 'PUT' : 'POST';
                
                fetch(url, {{
                    method: method,
                    headers: getAuthHeaders(),
                    body: JSON.stringify(data)
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success || data.id) {{
                        showToast(userId ? 'Cập nhật người dùng thành công!' : 'Thêm người dùng thành công!');
                        closeUserModal();
                        loadUsers();
                    }} else {{
                        showToast(data.message || 'Lỗi khi lưu', 'error');
                    }}
                }})
                .catch(error => {{
                    showToast('Lỗi khi lưu', 'error');
                }});
            }}
            
            function toggleUserStatus(userId, isActive) {{
                fetch(`/admin/users/${{userId}}/toggle-status`, {{
                    method: 'PATCH',
                    headers: getAuthHeaders(),
                    body: JSON.stringify({{ is_active: isActive }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        showToast(isActive ? 'Đã mở khóa tài khoản' : 'Đã khóa tài khoản');
                        loadUsers();
                    }} else {{
                        showToast(data.message || 'Lỗi khi thay đổi trạng thái', 'error');
                    }}
                }})
                .catch(error => {{
                    showToast('Lỗi khi thay đổi trạng thái', 'error');
                }});
            }}
            
            function deleteUser(userId) {{
                if (!confirm('Bạn có chắc muốn xóa người dùng này? Hành động này không thể hoàn tác!')) {{
                    return;
                }}
                
                fetch(`/admin/users/${{userId}}`, {{
                    method: 'DELETE',
                    headers: getAuthHeaders()
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        showToast('Đã xóa người dùng thành công');
                        loadUsers();
                    }} else {{
                        showToast(data.message || 'Lỗi khi xóa', 'error');
                    }}
                }})
                .catch(error => {{
                    showToast('Lỗi khi xóa', 'error');
                }});
            }}
            
            // Load users on page load
            document.addEventListener('DOMContentLoaded', function() {{
                loadUsers();
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/list")
def list_users(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lấy danh sách tất cả users"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in users
    ]


@router.get("/{user_id}")
def get_user(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lấy thông tin một user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }


@router.post("/")
def create_user(
    user_data: UserCreate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Tạo user mới"""
    # Check username uniqueness
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
    
    # Check email uniqueness
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        display_name=user_data.display_name or user_data.username,
        role=user_data.role,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "id": user.id,
        "message": "Tạo người dùng thành công"
    }


@router.put("/{user_id}")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Cập nhật user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check email uniqueness if changed
    if user_data.email and user_data.email != user.email:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email đã được sử dụng")
        user.email = user_data.email
    
    if user_data.display_name is not None:
        user.display_name = user_data.display_name
    
    if user_data.role is not None:
        user.role = user_data.role
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    user.updated_at = datetime.now()
    db.commit()
    
    return {"success": True, "message": "Cập nhật người dùng thành công"}


@router.patch("/{user_id}/toggle-status")
def toggle_user_status(
    user_id: int,
    status_data: dict,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Khóa/Mở khóa user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Không cho phép khóa chính mình
    if user.id == admin_user.id:
        raise HTTPException(status_code=400, detail="Không thể khóa chính tài khoản của bạn")
    
    user.is_active = status_data.get("is_active", not user.is_active)
    user.updated_at = datetime.now()
    db.commit()
    
    return {"success": True, "message": f"Đã {'mở khóa' if user.is_active else 'khóa'} tài khoản"}


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xóa user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Không cho phép xóa chính mình
    if user.id == admin_user.id:
        raise HTTPException(status_code=400, detail="Không thể xóa chính tài khoản của bạn")
    
    db.delete(user)
    db.commit()
    
    return {"success": True, "message": "Đã xóa người dùng thành công"}

