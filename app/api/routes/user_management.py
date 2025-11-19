# -*- coding: utf-8 -*-
"""
User Management Routes - Quản lý người dùng (Admin only)
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.account_prefix import Account, Prefix
from app.models.logic_rule import LogicRule
from app.core.security import get_password_hash, get_current_user
from app.api.routes.auth import get_current_user_optional
from app.core.ui_helpers import get_user_dropdown_menu, get_account_locked_message

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
    password: Optional[str] = None


@router.get("", response_class=HTMLResponse)
def user_management_page(
    request: Request,
    admin_user: User = Depends(require_admin)
):
    """Trang quản lý người dùng (Admin only)"""
    
    # Check if admin is locked
    if not admin_user.is_active:
        return HTMLResponse(content=get_account_locked_message())
    
    user_menu = get_user_dropdown_menu(admin_user)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quản Lý Người Dùng - Admin</title>
        <link rel="icon" type="image/png" href="/static/favicon.png">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
                color: #1e293b;
                line-height: 1.6;
                min-height: 100vh;
                position: relative;
                overflow-x: hidden;
            }}
            
            @keyframes gradientShift {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            
            body::before {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                    radial-gradient(circle at 40% 20%, rgba(120, 200, 255, 0.3) 0%, transparent 50%);
                pointer-events: none;
                z-index: 0;
            }}
            
            .header {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.3);
                padding: 16px 32px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                z-index: 100;
            }}
            
            .header h1 {{
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
            }}
            
            .header-actions {{
                display: flex;
                align-items: center;
                gap: 12px;
                position: relative;
                z-index: 101;
            }}
            
            .btn-back {{
                padding: 8px 16px;
                background: rgba(102, 126, 234, 0.1);
                border: 1px solid rgba(102, 126, 234, 0.3);
                border-radius: 8px;
                color: #667eea;
                cursor: pointer;
                text-decoration: none;
                font-weight: 500;
            }}
            
            .btn-back:hover {{
                background: rgba(102, 126, 234, 0.2);
            }}
            
            .container {{
                max-width: 1600px;
                margin: 0 auto;
                padding: 100px 32px 40px;
                position: relative;
                z-index: 1;
            }}
            
            .section {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 24px;
                padding: 32px;
                margin-bottom: 32px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }}
            
            .section-title {{
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 24px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 16px;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 32px;
            }}
            
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 24px;
                border-radius: 16px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
            
            .stat-card.secondary {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }}
            
            .stat-card.success {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            }}
            
            .stat-card.warning {{
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            }}
            
            .stat-card {{
                position: relative;
                cursor: help;
            }}
            
            .stat-card .label {{
                font-size: 14px;
                opacity: 0.9;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            
            .stat-card .label .info-icon {{
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 11px;
                cursor: help;
            }}
            
            .stat-card .value {{
                font-size: 32px;
                font-weight: 700;
            }}
            
            .stat-card .description {{
                font-size: 11px;
                opacity: 0.8;
                margin-top: 4px;
            }}
            
            .stat-card .tooltip {{
                position: absolute;
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 12px;
                white-space: nowrap;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.2s;
                margin-bottom: 8px;
                z-index: 10;
            }}
            
            .stat-card:hover .tooltip {{
                opacity: 1;
            }}
            
            .filters-bar {{
                display: flex;
                gap: 12px;
                margin-bottom: 24px;
                flex-wrap: wrap;
            }}
            
            .search-box {{
                flex: 1;
                min-width: 250px;
                position: relative;
            }}
            
            .search-box input {{
                width: 100%;
                padding: 12px 16px 12px 44px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 14px;
                transition: all 0.2s;
            }}
            
            .search-box input:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            
            .search-box::before {{
                content: '🔍';
                position: absolute;
                left: 14px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 18px;
            }}
            
            .filter-select {{
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 14px;
                background: white;
                cursor: pointer;
                transition: all 0.2s;
            }}
            
            .filter-select:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            
            .btn {{
                padding: 12px 24px;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            
            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }}
            
            .btn-danger {{
                background: #ef4444;
                color: white;
            }}
            
            .btn-danger:hover {{
                background: #dc2626;
            }}
            
            .btn-success {{
                background: #10b981;
                color: white;
            }}
            
            .btn-success:hover {{
                background: #059669;
            }}
            
            .btn-warning {{
                background: #f59e0b;
                color: white;
            }}
            
            .btn-warning:hover {{
                background: #d97706;
            }}
            
            .btn-secondary {{
                background: #64748b;
                color: white;
            }}
            
            .btn-secondary:hover {{
                background: #475569;
            }}
            
            .btn:disabled {{
                opacity: 0.6;
                cursor: not-allowed;
                transform: none !important;
            }}
            
            .table-container {{
                overflow-x: auto;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                background: white;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            th {{
                background: #f8fafc;
                padding: 16px;
                text-align: left;
                font-weight: 600;
                color: #475569;
                font-size: 12px;
                text-transform: uppercase;
                border-bottom: 2px solid #e2e8f0;
            }}
            
            th.sortable {{
                cursor: pointer;
                user-select: none;
            }}
            
            th.sortable:hover {{
                background: #f1f5f9;
            }}
            
            td {{
                padding: 16px;
                border-bottom: 1px solid #e2e8f0;
            }}
            
            tr:hover {{
                background: #f8fafc;
            }}
            
            .user-avatar-cell {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .user-avatar {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 600;
                font-size: 16px;
                flex-shrink: 0;
            }}
            
            .user-avatar img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                border-radius: 50%;
            }}
            
            .user-info {{
                display: flex;
                flex-direction: column;
            }}
            
            .user-name {{
                font-weight: 600;
                color: #1e293b;
            }}
            
            .user-username {{
                font-size: 12px;
                color: #64748b;
            }}
            
            .badge {{
                padding: 6px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                display: inline-block;
            }}
            
            .badge-admin {{
                background: #fef3c7;
                color: #92400e;
            }}
            
            .badge-user {{
                background: #dbeafe;
                color: #1e40af;
            }}
            
            .badge-active {{
                background: #d1fae5;
                color: #065f46;
            }}
            
            .badge-inactive {{
                background: #fee2e2;
                color: #991b1b;
            }}
            
            .action-buttons {{
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }}
            
            .btn-icon {{
                padding: 8px 12px;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s;
                font-weight: 500;
            }}
            
            .btn-icon:hover {{
                transform: translateY(-1px);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            }}
            
            .checkbox-cell {{
                text-align: center;
            }}
            
            .checkbox-cell input[type="checkbox"] {{
                width: 18px;
                height: 18px;
                cursor: pointer;
            }}
            
            .bulk-actions {{
                display: none;
                padding: 16px;
                background: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
                align-items: center;
                gap: 12px;
            }}
            
            .bulk-actions.active {{
                display: flex;
            }}
            
            .loading {{
                text-align: center;
                padding: 40px;
                color: #64748b;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 16px;
            }}
            
            .loading::before {{
                content: '';
                width: 40px;
                height: 40px;
                border: 4px solid #e2e8f0;
                border-top-color: #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }}
            
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
            
            .empty-state {{
                text-align: center;
                padding: 60px 20px;
                color: #64748b;
            }}
            
            .empty-state .icon {{
                font-size: 64px;
                margin-bottom: 16px;
                opacity: 0.5;
            }}
            
            .empty-state h3 {{
                font-size: 18px;
                font-weight: 600;
                color: #475569;
                margin-bottom: 8px;
            }}
            
            .pagination {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 8px;
                margin-top: 24px;
                padding: 16px;
            }}
            
            .pagination button {{
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                background: white;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s;
            }}
            
            .pagination button:hover:not(:disabled) {{
                background: #f8fafc;
            }}
            
            .pagination button.active {{
                background: #667eea;
                color: white;
                border-color: #667eea;
            }}
            
            .pagination button:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            
            .modal {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
                z-index: 1000;
                align-items: center;
                justify-content: center;
            }}
            
            .modal.active {{
                display: flex;
            }}
            
            .modal-content {{
                background: white;
                border-radius: 24px;
                padding: 32px;
                max-width: 600px;
                width: 90%;
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                animation: modalSlideIn 0.3s ease;
            }}
            
            @keyframes modalSlideIn {{
                from {{
                    opacity: 0;
                    transform: translateY(-20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .modal-header {{
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 24px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .modal-close {{
                background: none;
                border: none;
                font-size: 28px;
                color: #64748b;
                cursor: pointer;
                padding: 0;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 8px;
                transition: all 0.2s;
            }}
            
            .modal-close:hover {{
                background: #f1f5f9;
                color: #1e293b;
            }}
            
            .form-group {{
                margin-bottom: 20px;
            }}
            
            .form-group label {{
                display: block;
                font-weight: 500;
                color: #374151;
                margin-bottom: 8px;
                font-size: 14px;
            }}
            
            .form-group input, .form-group select {{
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 14px;
                transition: border-color 0.2s;
            }}
            
            .form-group input:focus, .form-group select:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            
            .form-group input:disabled {{
                background: #f8fafc;
                cursor: not-allowed;
            }}
            
            .modal-actions {{
                display: flex;
                gap: 12px;
                justify-content: flex-end;
                margin-top: 24px;
            }}
            
            .toast-container {{
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 2000;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }}
            
            .toast {{
                padding: 16px 24px;
                border-radius: 12px;
                color: white;
                font-weight: 500;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                animation: slideInRight 0.3s ease-out;
                min-width: 300px;
            }}
            
            .toast.success {{
                background: #10b981;
            }}
            
            .toast.error {{
                background: #ef4444;
            }}
            
            .toast.warning {{
                background: #f59e0b;
            }}
            
            @keyframes slideInRight {{
                from {{
                    transform: translateX(100%);
                    opacity: 0;
                }}
                to {{
                    transform: translateX(0);
                    opacity: 1;
                }}
            }}
            
            .confirm-dialog {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
                z-index: 2000;
                align-items: center;
                justify-content: center;
            }}
            
            .confirm-dialog.active {{
                display: flex;
            }}
            
            .confirm-content {{
                background: white;
                border-radius: 16px;
                padding: 32px;
                max-width: 400px;
                width: 90%;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }}
            
            .confirm-content h3 {{
                font-size: 20px;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 12px;
            }}
            
            .confirm-content p {{
                color: #64748b;
                margin-bottom: 24px;
            }}
            
            .confirm-actions {{
                display: flex;
                gap: 12px;
                justify-content: flex-end;
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 100px 16px 40px;
                }}
                
                .section {{
                    padding: 24px;
                }}
                
                .stats-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .filters-bar {{
                    flex-direction: column;
                }}
                
                table {{
                    font-size: 12px;
                }}
                
                th, td {{
                    padding: 8px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>👥 Quản Lý Người Dùng</h1>
            <div class="header-actions">
                {user_menu}
                <a href="/" class="btn-back">← Về Trang Chủ</a>
            </div>
        </div>
        
        <div class="container">
            <!-- Statistics Section -->
            <div class="section">
                <div class="stats-grid" id="statsGrid">
                    <div class="stat-card">
                        <div class="tooltip">Tổng số tài khoản người dùng trong hệ thống</div>
                        <div class="label">
                            👥 Tổng Người Dùng
                            <span class="info-icon">?</span>
                        </div>
                        <div class="value" id="totalUsers">0</div>
                        <div class="description">Tất cả tài khoản</div>
                    </div>
                    <div class="stat-card secondary">
                        <div class="tooltip">Tài khoản chưa bị khóa, có thể đăng nhập và sử dụng hệ thống</div>
                        <div class="label">
                            ✅ Tài Khoản Kích Hoạt
                            <span class="info-icon">?</span>
                        </div>
                        <div class="value" id="activeUsers">0</div>
                        <div class="description">Chưa bị khóa</div>
                    </div>
                    <div class="stat-card success">
                        <div class="tooltip">Số lượng tài khoản có quyền quản trị viên</div>
                        <div class="label">
                            👑 Quản Trị Viên
                            <span class="info-icon">?</span>
                        </div>
                        <div class="value" id="adminUsers">0</div>
                        <div class="description">Có quyền admin</div>
                    </div>
                    <div class="stat-card warning">
                        <div class="tooltip">Tài khoản đã bị khóa, không thể đăng nhập</div>
                        <div class="label">
                            🔒 Tài Khoản Đã Khóa
                            <span class="info-icon">?</span>
                        </div>
                        <div class="value" id="inactiveUsers">0</div>
                        <div class="description">Đã bị khóa</div>
                    </div>
                </div>
            </div>
            
            <!-- Users Table Section -->
            <div class="section">
                <div class="section-title">
                    <span>📋 Danh Sách Người Dùng</span>
                    <button class="btn btn-primary" onclick="showAddUserModal()">
                        ➕ Thêm Người Dùng
                    </button>
                </div>
                
                <!-- Filters -->
                <div class="filters-bar">
                    <div class="search-box">
                        <input type="text" id="searchInput" placeholder="Tìm kiếm theo tên, email, username..." oninput="filterUsers()">
                    </div>
                    <select class="filter-select" id="roleFilter" onchange="filterUsers()">
                        <option value="">Tất cả vai trò</option>
                        <option value="admin">Quản trị viên</option>
                        <option value="user">Người dùng</option>
                    </select>
                    <select class="filter-select" id="statusFilter" onchange="filterUsers()">
                        <option value="">Tất cả trạng thái</option>
                        <option value="active">Hoạt động</option>
                        <option value="inactive">Đã khóa</option>
                    </select>
                    <button class="btn btn-secondary" onclick="resetFilters()">🔄 Đặt lại</button>
                </div>
                
                <!-- Bulk Actions -->
                <div class="bulk-actions" id="bulkActions">
                    <span id="selectedCount">0 người dùng đã chọn</span>
                    <button class="btn btn-success" onclick="bulkToggleStatus(true)">🔓 Mở khóa</button>
                    <button class="btn btn-warning" onclick="bulkToggleStatus(false)">🔒 Khóa</button>
                    <button class="btn btn-danger" onclick="bulkDelete()">🗑️ Xóa</button>
                    <button class="btn btn-secondary" onclick="clearSelection()">✕ Bỏ chọn</button>
                </div>
                
                <!-- Table -->
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th class="checkbox-cell">
                                    <input type="checkbox" id="selectAll" onchange="toggleSelectAll()">
                                </th>
                                <th class="sortable" onclick="sortTable('id')">ID <span id="sort-id">↕</span></th>
                                <th class="sortable" onclick="sortTable('username')">Người Dùng <span id="sort-username">↕</span></th>
                                <th class="sortable" onclick="sortTable('email')">Email <span id="sort-email">↕</span></th>
                                <th>Vai Trò</th>
                                <th>Trạng Thái</th>
                                <th class="sortable" onclick="sortTable('accounts')">Accounts <span id="sort-accounts">↕</span></th>
                                <th class="sortable" onclick="sortTable('prefixes')">Prefixes <span id="sort-prefixes">↕</span></th>
                                <th class="sortable" onclick="sortTable('created_at')">Ngày Tạo <span id="sort-created_at">↕</span></th>
                                <th>Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody id="usersTableBody">
                            <tr>
                                <td colspan="10" style="text-align: center; padding: 40px;">
                                    <div class="loading">Đang tải...</div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- Pagination -->
                <div class="pagination" id="pagination"></div>
            </div>
        </div>
        
        <!-- Add/Edit User Modal -->
        <div id="userModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <span id="modalTitle">Thêm Người Dùng</span>
                    <button class="modal-close" onclick="closeUserModal()">×</button>
                </div>
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
                        <input type="text" id="displayName" placeholder="Để trống sẽ dùng tên đăng nhập">
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
                            <input type="checkbox" id="isActive" checked style="width: auto; margin-right: 8px;">
                            Tài khoản hoạt động
                        </label>
                    </div>
                    
                    <div class="modal-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeUserModal()">Hủy</button>
                        <button type="submit" class="btn btn-primary">💾 Lưu</button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Toast Container -->
        <div class="toast-container" id="toastContainer"></div>
        
        <!-- Confirm Dialog -->
        <div id="confirmDialog" class="confirm-dialog">
            <div class="confirm-content">
                <h3 id="confirmTitle">Xác nhận</h3>
                <p id="confirmMessage"></p>
                <div class="confirm-actions">
                    <button class="btn btn-secondary" onclick="closeConfirm()">Hủy</button>
                    <button class="btn btn-danger" id="confirmButton" onclick="executeConfirm()">Xác nhận</button>
                </div>
            </div>
        </div>
        
        <script>
            let allUsers = [];
            let filteredUsers = [];
            let currentPage = 1;
            const pageSize = 10;
            let sortColumn = 'id';
            let sortDirection = 'desc';
            let selectedUserIds = new Set();
            let confirmCallback = null;
            
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
                const container = document.getElementById('toastContainer');
                const toast = document.createElement('div');
                toast.className = `toast ${{type}}`;
                toast.textContent = message;
                container.appendChild(toast);
                
                setTimeout(() => {{
                    toast.style.animation = 'slideInRight 0.3s ease-out reverse';
                    setTimeout(() => toast.remove(), 300);
                }}, 3000);
            }}
            
            function showConfirm(title, message, callback) {{
                document.getElementById('confirmTitle').textContent = title;
                document.getElementById('confirmMessage').textContent = message;
                confirmCallback = callback;
                document.getElementById('confirmDialog').classList.add('active');
            }}
            
            function closeConfirm() {{
                document.getElementById('confirmDialog').classList.remove('active');
                confirmCallback = null;
            }}
            
            function executeConfirm() {{
                if (confirmCallback) {{
                    confirmCallback();
                }}
                closeConfirm();
            }}
            
            async function loadUsers() {{
                try {{
                    const response = await fetch('/admin/users/list', {{
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        throw new Error('Lỗi khi tải danh sách người dùng');
                    }}
                    
                    const data = await response.json();
                    allUsers = data.users || [];
                    updateStats(data.stats || {{}});
                    filterUsers();
                }} catch (error) {{
                    showToast('Lỗi khi tải danh sách người dùng: ' + error.message, 'error');
                    document.getElementById('usersTableBody').innerHTML = `
                        <tr>
                            <td colspan="10" style="text-align: center; padding: 40px; color: #ef4444;">
                                ❌ Lỗi khi tải dữ liệu
                            </td>
                        </tr>
                    `;
                }}
            }}
            
            function updateStats(stats) {{
                document.getElementById('totalUsers').textContent = stats.total || 0;
                document.getElementById('activeUsers').textContent = stats.active || 0;
                document.getElementById('adminUsers').textContent = stats.admin || 0;
                document.getElementById('inactiveUsers').textContent = stats.inactive || 0;
            }}
            
            function filterUsers() {{
                const search = document.getElementById('searchInput').value.toLowerCase();
                const roleFilter = document.getElementById('roleFilter').value;
                const statusFilter = document.getElementById('statusFilter').value;
                
                filteredUsers = allUsers.filter(user => {{
                    const matchSearch = !search || 
                        user.username.toLowerCase().includes(search) ||
                        user.email.toLowerCase().includes(search) ||
                        (user.display_name && user.display_name.toLowerCase().includes(search));
                    
                    const matchRole = !roleFilter || user.role === roleFilter;
                    const matchStatus = !statusFilter || 
                        (statusFilter === 'active' && user.is_active) ||
                        (statusFilter === 'inactive' && !user.is_active);
                    
                    return matchSearch && matchRole && matchStatus;
                }});
                
                sortTable(sortColumn, false);
            }}
            
            function resetFilters() {{
                document.getElementById('searchInput').value = '';
                document.getElementById('roleFilter').value = '';
                document.getElementById('statusFilter').value = '';
                filterUsers();
            }}
            
            function sortTable(column, updateDirection = true) {{
                if (updateDirection) {{
                    if (sortColumn === column) {{
                        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
                    }} else {{
                        sortColumn = column;
                        sortDirection = 'asc';
                    }}
                }}
                
                // Reset sort indicators
                document.querySelectorAll('th.sortable span').forEach(span => {{
                    span.textContent = '↕';
                }});
                
                // Update current sort indicator
                const indicator = document.getElementById(`sort-${{column}}`);
                if (indicator) {{
                    indicator.textContent = sortDirection === 'asc' ? '↑' : '↓';
                }}
                
                filteredUsers.sort((a, b) => {{
                    let aVal = a[column];
                    let bVal = b[column];
                    
                    if (column === 'created_at') {{
                        aVal = new Date(aVal);
                        bVal = new Date(bVal);
                    }}
                    
                    if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
                    if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
                    return 0;
                }});
                
                renderTable();
            }}
            
            function renderTable() {{
                const tbody = document.getElementById('usersTableBody');
                const start = (currentPage - 1) * pageSize;
                const end = start + pageSize;
                const pageUsers = filteredUsers.slice(start, end);
                
                if (pageUsers.length === 0) {{
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="10" style="text-align: center; padding: 40px;">
                                <div class="empty-state">
                                    <div class="icon">👤</div>
                                    <h3>Không tìm thấy người dùng</h3>
                                    <p>Thử thay đổi bộ lọc hoặc tìm kiếm</p>
                                </div>
                            </td>
                        </tr>
                    `;
                    document.getElementById('pagination').innerHTML = '';
                    return;
                }}
                
                tbody.innerHTML = pageUsers.map(user => {{
                    const avatarUrl = user.avatar && user.avatar !== 'default_avatar.png' 
                        ? `/static/avatars/${{user.avatar}}` 
                        : '';
                    const displayName = user.display_name || user.username;
                    const avatarInitial = displayName[0].toUpperCase();
                    const isSelected = selectedUserIds.has(user.id);
                    
                    return `
                        <tr>
                            <td class="checkbox-cell">
                                <input type="checkbox" ${{isSelected ? 'checked' : ''}} onchange="toggleUserSelection(${{user.id}})">
                            </td>
                            <td>${{user.id}}</td>
                            <td>
                                <div class="user-avatar-cell">
                                    <div class="user-avatar">
                                        ${{avatarUrl ? `<img src="${{avatarUrl}}" alt="Avatar" onerror="this.parentElement.innerHTML='${{avatarInitial}}'">` : avatarInitial}}
                                    </div>
                                    <div class="user-info">
                                        <div class="user-name">${{displayName}}</div>
                                        <div class="user-username">@${{user.username}}</div>
                                    </div>
                                </div>
                            </td>
                            <td>${{user.email}}</td>
                            <td><span class="badge badge-${{user.role}}">${{user.role === 'admin' ? '👑 Admin' : '👤 User'}}</span></td>
                            <td><span class="badge badge-${{user.is_active ? 'active' : 'inactive'}}">${{user.is_active ? 'Hoạt động' : 'Đã khóa'}}</span></td>
                            <td>${{user.accounts_count || 0}}</td>
                            <td>${{user.prefixes_count || 0}}</td>
                            <td>${{new Date(user.created_at).toLocaleDateString('vi-VN')}}</td>
                            <td>
                                <div class="action-buttons">
                                    <button class="btn-icon btn-primary" onclick="editUser(${{user.id}})" title="Sửa">✏️</button>
                                    <button class="btn-icon btn-${{user.is_active ? 'warning' : 'success'}}" onclick="toggleUserStatus(${{user.id}}, ${{!user.is_active}})" title="${{user.is_active ? 'Khóa' : 'Mở khóa'}}">
                                        ${{user.is_active ? '🔒' : '🔓'}}
                                    </button>
                                    <button class="btn-icon btn-danger" onclick="deleteUser(${{user.id}})" title="Xóa">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    `;
                }}).join('');
                
                renderPagination();
                updateBulkActions();
            }}
            
            function renderPagination() {{
                const totalPages = Math.ceil(filteredUsers.length / pageSize);
                const pagination = document.getElementById('pagination');
                
                if (totalPages <= 1) {{
                    pagination.innerHTML = '';
                    return;
                }}
                
                let html = `
                    <button onclick="goToPage(1)" ${{currentPage === 1 ? 'disabled' : ''}}>«</button>
                    <button onclick="goToPage(${{currentPage - 1}})" ${{currentPage === 1 ? 'disabled' : ''}}>‹</button>
                `;
                
                const startPage = Math.max(1, currentPage - 2);
                const endPage = Math.min(totalPages, currentPage + 2);
                
                if (startPage > 1) {{
                    html += `<button onclick="goToPage(1)">1</button>`;
                    if (startPage > 2) html += `<span>...</span>`;
                }}
                
                for (let i = startPage; i <= endPage; i++) {{
                    html += `<button class="${{i === currentPage ? 'active' : ''}}" onclick="goToPage(${{i}})">${{i}}</button>`;
                }}
                
                if (endPage < totalPages) {{
                    if (endPage < totalPages - 1) html += `<span>...</span>`;
                    html += `<button onclick="goToPage(${{totalPages}})">${{totalPages}}</button>`;
                }}
                
                html += `
                    <button onclick="goToPage(${{currentPage + 1}})" ${{currentPage === totalPages ? 'disabled' : ''}}>›</button>
                    <button onclick="goToPage(${{totalPages}})" ${{currentPage === totalPages ? 'disabled' : ''}}>»</button>
                `;
                
                pagination.innerHTML = html;
            }}
            
            function goToPage(page) {{
                const totalPages = Math.ceil(filteredUsers.length / pageSize);
                if (page < 1 || page > totalPages) return;
                currentPage = page;
                renderTable();
            }}
            
            function toggleUserSelection(userId) {{
                if (selectedUserIds.has(userId)) {{
                    selectedUserIds.delete(userId);
                }} else {{
                    selectedUserIds.add(userId);
                }}
                updateBulkActions();
                renderTable();
            }}
            
            function toggleSelectAll() {{
                const selectAll = document.getElementById('selectAll').checked;
                const start = (currentPage - 1) * pageSize;
                const end = start + pageSize;
                const pageUsers = filteredUsers.slice(start, end);
                
                if (selectAll) {{
                    pageUsers.forEach(user => selectedUserIds.add(user.id));
                }} else {{
                    pageUsers.forEach(user => selectedUserIds.delete(user.id));
                }}
                
                updateBulkActions();
                renderTable();
            }}
            
            function clearSelection() {{
                selectedUserIds.clear();
                document.getElementById('selectAll').checked = false;
                updateBulkActions();
                renderTable();
            }}
            
            function updateBulkActions() {{
                const bulkActions = document.getElementById('bulkActions');
                const selectedCount = document.getElementById('selectedCount');
                
                if (selectedUserIds.size > 0) {{
                    bulkActions.classList.add('active');
                    selectedCount.textContent = `${{selectedUserIds.size}} người dùng đã chọn`;
                }} else {{
                    bulkActions.classList.remove('active');
                }}
            }}
            
            async function bulkToggleStatus(isActive) {{
                if (selectedUserIds.size === 0) return;
                
                const action = isActive ? 'mở khóa' : 'khóa';
                showConfirm(
                    `Xác nhận ${{action}}`,
                    `Bạn có chắc muốn ${{action}} ${{selectedUserIds.size}} người dùng đã chọn?`,
                    async () => {{
                        try {{
                            const userIds = Array.from(selectedUserIds);
                            let successCount = 0;
                            let failCount = 0;
                            
                            for (const userId of userIds) {{
                                try {{
                                    const response = await fetch(`/admin/users/${{userId}}/toggle-status`, {{
                                        method: 'PATCH',
                                        headers: getAuthHeaders(),
                                        body: JSON.stringify({{ is_active: isActive }})
                                    }});
                                    
                                    if (response.ok) {{
                                        successCount++;
                                    }} else {{
                                        failCount++;
                                    }}
                                }} catch (error) {{
                                    failCount++;
                                }}
                            }}
                            
                            if (successCount > 0) {{
                                showToast(`Đã ${{action}} ${{successCount}} người dùng thành công`, 'success');
                            }}
                            if (failCount > 0) {{
                                showToast(`Không thể ${{action}} ${{failCount}} người dùng`, 'error');
                            }}
                            
                            clearSelection();
                            loadUsers();
                        }} catch (error) {{
                            showToast('Lỗi khi thực hiện thao tác: ' + error.message, 'error');
                        }}
                    }}
                );
            }}
            
            async function bulkDelete() {{
                if (selectedUserIds.size === 0) return;
                
                showConfirm(
                    'Xác nhận xóa',
                    `Bạn có chắc muốn xóa ${{selectedUserIds.size}} người dùng đã chọn? Hành động này không thể hoàn tác!`,
                    async () => {{
                        try {{
                            const userIds = Array.from(selectedUserIds);
                            let successCount = 0;
                            let failCount = 0;
                            
                            for (const userId of userIds) {{
                                try {{
                                    const response = await fetch(`/admin/users/${{userId}}`, {{
                                        method: 'DELETE',
                                        headers: getAuthHeaders()
                                    }});
                                    
                                    if (response.ok) {{
                                        successCount++;
                                    }} else {{
                                        failCount++;
                                    }}
                                }} catch (error) {{
                                    failCount++;
                                }}
                            }}
                            
                            if (successCount > 0) {{
                                showToast(`Đã xóa ${{successCount}} người dùng thành công`, 'success');
                            }}
                            if (failCount > 0) {{
                                showToast(`Không thể xóa ${{failCount}} người dùng`, 'error');
                            }}
                            
                            clearSelection();
                            loadUsers();
                        }} catch (error) {{
                            showToast('Lỗi khi xóa: ' + error.message, 'error');
                        }}
                    }}
                );
            }}
            
            function showAddUserModal() {{
                document.getElementById('modalTitle').textContent = 'Thêm Người Dùng';
                document.getElementById('userId').value = '';
                document.getElementById('username').value = '';
                document.getElementById('username').disabled = false;
                document.getElementById('email').value = '';
                document.getElementById('password').value = '';
                document.getElementById('passwordLabel').innerHTML = 'Mật khẩu *';
                document.getElementById('password').required = true;
                document.getElementById('displayName').value = '';
                document.getElementById('role').value = 'user';
                document.getElementById('isActiveGroup').style.display = 'none';
                document.getElementById('userModal').classList.add('active');
            }}
            
            async function editUser(userId) {{
                try {{
                    const response = await fetch(`/admin/users/${{userId}}`, {{
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        throw new Error('Lỗi khi tải thông tin người dùng');
                    }}
                    
                    const user = await response.json();
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
                }} catch (error) {{
                    showToast('Lỗi khi tải thông tin người dùng: ' + error.message, 'error');
                }}
            }}
            
            function closeUserModal() {{
                document.getElementById('userModal').classList.remove('active');
                document.getElementById('username').disabled = false;
            }}
            
            async function saveUser() {{
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
                
                try {{
                    const response = await fetch(url, {{
                        method: method,
                        headers: getAuthHeaders(),
                        body: JSON.stringify(data)
                    }});
                    
                    // Check content type before parsing
                    const contentType = response.headers.get('content-type');
                    let result;
                    
                    if (contentType && contentType.includes('application/json')) {{
                        result = await response.json();
                    }} else {{
                        const text = await response.text();
                        result = {{ detail: 'Lỗi server: ' + text.substring(0, 100) }};
                    }}
                    
                    if (!response.ok) {{
                        throw new Error(result.detail || result.message || 'Lỗi khi lưu');
                    }}
                    
                    showToast(userId ? 'Cập nhật người dùng thành công!' : 'Thêm người dùng thành công!');
                    closeUserModal();
                    loadUsers();
                }} catch (error) {{
                    showToast('Lỗi khi lưu: ' + error.message, 'error');
                }}
            }}
            
            async function toggleUserStatus(userId, isActive) {{
                const action = isActive ? 'mở khóa' : 'khóa';
                showConfirm(
                    `Xác nhận ${{action}}`,
                    `Bạn có chắc muốn ${{action}} tài khoản này?`,
                    async () => {{
                        try {{
                            const response = await fetch(`/admin/users/${{userId}}/toggle-status`, {{
                                method: 'PATCH',
                                headers: getAuthHeaders(),
                                body: JSON.stringify({{ is_active: isActive }})
                            }});
                            
                            // Check content type before parsing
                            const contentType = response.headers.get('content-type');
                            let result;
                            
                            if (contentType && contentType.includes('application/json')) {{
                                result = await response.json();
                            }} else {{
                                const text = await response.text();
                                result = {{ detail: 'Lỗi server: ' + text.substring(0, 100) }};
                            }}
                            
                            if (!response.ok) {{
                                throw new Error(result.detail || result.message || 'Lỗi khi thay đổi trạng thái');
                            }}
                            
                            showToast(`Đã ${{action}} tài khoản thành công`);
                            loadUsers();
                        }} catch (error) {{
                            showToast('Lỗi: ' + error.message, 'error');
                        }}
                    }}
                );
            }}
            
            async function deleteUser(userId) {{
                showConfirm(
                    'Xác nhận xóa',
                    'Bạn có chắc muốn xóa người dùng này? Hành động này không thể hoàn tác!',
                    async () => {{
                        try {{
                            const response = await fetch(`/admin/users/${{userId}}`, {{
                                method: 'DELETE',
                                headers: getAuthHeaders()
                            }});
                            
                            // Check content type before parsing
                            const contentType = response.headers.get('content-type');
                            let result;
                            
                            if (contentType && contentType.includes('application/json')) {{
                                result = await response.json();
                            }} else {{
                                // Handle non-JSON response (HTML error page)
                                const text = await response.text();
                                result = {{ detail: 'Lỗi server: ' + text.substring(0, 100) }};
                            }}
                            
                            if (!response.ok) {{
                                throw new Error(result.detail || result.message || 'Lỗi khi xóa');
                            }}
                            
                            showToast('Đã xóa người dùng thành công');
                            loadUsers();
                        }} catch (error) {{
                            showToast('Lỗi khi xóa: ' + error.message, 'error');
                        }}
                    }}
                );
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
    """Lấy danh sách tất cả users với thống kê"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    # Calculate statistics
    total = len(users)
    active = sum(1 for u in users if u.is_active)
    inactive = total - active
    admin = sum(1 for u in users if u.role == 'admin')
    
    # Get user statistics (accounts, prefixes)
    users_with_stats = []
    for user in users:
        accounts_count = db.query(func.count(Account.id)).filter(Account.user_id == user.id).scalar() or 0
        prefixes_count = db.query(func.count(Prefix.id)).filter(Prefix.user_id == user.id).scalar() or 0
        
        users_with_stats.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "avatar": user.avatar,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "accounts_count": accounts_count,
            "prefixes_count": prefixes_count
        })
    
    return {
        "users": users_with_stats,
        "stats": {
            "total": total,
            "active": active,
            "inactive": inactive,
            "admin": admin,
            "user": total - admin
        }
    }


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
    
    # Get statistics
    accounts_count = db.query(func.count(Account.id)).filter(Account.user_id == user.id).scalar() or 0
    prefixes_count = db.query(func.count(Prefix.id)).filter(Prefix.user_id == user.id).scalar() or 0
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "avatar": user.avatar,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "accounts_count": accounts_count,
        "prefixes_count": prefixes_count
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
    
    if user_data.password:
        user.hashed_password = get_password_hash(user_data.password)
    
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
