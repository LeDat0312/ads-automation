# -*- coding: utf-8 -*-
"""
Home Page - Trang chủ với navigation buttons
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.routes.auth import get_current_user_optional
from app.models.user import User
from app.core.ui_helpers import get_user_dropdown_menu, get_account_locked_message
from typing import Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def home_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Trang chủ với các nút điều hướng"""
    
    # Check if user is locked (even if authenticated)
    if current_user and not current_user.is_active:
        return HTMLResponse(content=get_account_locked_message())
    
    # Don't redirect on server-side - let client-side handle it
    # This prevents redirect loops
    
    user_info = get_user_dropdown_menu(current_user) if current_user else ""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trang Chủ - Facebook Ads Automation</title>
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
            
            .home-container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 80px 32px;
                position: relative;
                z-index: 1;
                text-align: center;
            }}
            
            .logo-section {{
                margin-bottom: 60px;
                animation: fadeInUp 0.8s ease;
            }}
            
            @keyframes fadeInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .logo-section img {{
                width: 120px;
                height: 120px;
                margin-bottom: 24px;
                filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.2));
            }}
            
            .logo-section h1 {{
                font-size: 56px;
                font-weight: 800;
                color: white;
                margin-bottom: 20px;
                text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                line-height: 1.2;
            }}
            
            .logo-section p {{
                font-size: 20px;
                color: rgba(255, 255, 255, 0.9);
                max-width: 700px;
                margin: 0 auto;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}
            
            .button-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 32px;
                margin-top: 60px;
                animation: fadeInUp 1s ease 0.2s both;
            }}
            
            .nav-button {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 24px;
                padding: 40px 32px;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                text-decoration: none;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 16px;
            }}
            
            .nav-button:hover {{
                transform: translateY(-12px) scale(1.02);
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            }}
            
            .nav-button .icon {{
                font-size: 48px;
                margin-bottom: 8px;
            }}
            
            .nav-button .text {{
                font-size: 18px;
                font-weight: 600;
                color: #1e293b;
            }}
        </style>
    </head>
    <body>
        {user_info}
        
        <div class="home-container">
            <div class="logo-section">
                <img src="/static/favicon.png" alt="Logo" onerror="this.style.display='none'">
                <h1>🚀 Facebook Ads Automation</h1>
                <p>Hệ thống tự động hóa quảng cáo Facebook thông minh.<br>Tối ưu hóa ngân sách và hiệu suất quảng cáo tự động.</p>
            </div>
            
            <div class="button-grid">
                <a href="/rules/" class="nav-button">
                    <span class="icon">⚡</span>
                    <span class="text">Chọn Chiến Thuật</span>
                    <span style="font-size: 14px; color: #64748b; margin-top: 8px;">Chọn chiến thuật automation phù hợp với nhu cầu của bạn</span>
                </a>
                
                <a href="/rules/" class="nav-button">
                    <span class="icon">📋</span>
                    <span class="text">Quản Lý Rules</span>
                    <span style="font-size: 14px; color: #64748b; margin-top: 8px;">Xem và quản lý tất cả các automation rules</span>
                </a>
                
                <a href="/settings" class="nav-button">
                    <span class="icon">⚙️</span>
                    <span class="text">Cài Đặt</span>
                    <span style="font-size: 14px; color: #64748b; margin-top: 8px;">Quản lý token Facebook, accounts và prefixes</span>
                </a>
                
                {f'<a href="/admin/users" class="nav-button"><span class="icon">👥</span><span class="text">Quản Lý Người Dùng</span><span style="font-size: 14px; color: #64748b; margin-top: 8px;">Quản lý tài khoản người dùng (Admin)</span></a>' if current_user and current_user.role == 'admin' else ''}
                
                <a href="/api/dashboard/" class="nav-button">
                    <span class="icon">📊</span>
                    <span class="text">Dashboard</span>
                    <span style="font-size: 14px; color: #64748b; margin-top: 8px;">Xem tổng quan hiệu suất và thống kê quảng cáo</span>
                </a>
            </div>
        </div>
        
        <script>
            // Helper function to get cookie
            function getCookie(name) {{
                const value = `; ${{document.cookie}}`;
                const parts = value.split(`; ${{name}}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }}
            
            // Check authentication on page load - only redirect once
            (function() {{
                const token = localStorage.getItem('access_token') || getCookie('access_token');
                
                if (!token) {{
                    // Only redirect if we're not already on login page
                    if (!window.location.pathname.includes('/auth/login')) {{
                        window.location.href = '/auth/login';
                    }}
                    return;
                }}
                
                // Sync token from localStorage to cookie if needed
                if (localStorage.getItem('access_token') && !getCookie('access_token')) {{
                    document.cookie = `access_token=${{localStorage.getItem('access_token')}}; path=/; max-age=${{30 * 24 * 60 * 60}}`;
                }}
            }})();
            
            function logout() {{
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                // Clear cookie
                document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
                window.location.href = '/auth/login';
            }}
            
            // Check if account is locked on page load
            async function checkAccountStatus() {{
                const token = localStorage.getItem('access_token') || getCookie('access_token');
                if (!token) return;
                
                try {{
                    const response = await fetch('/auth/me', {{
                        headers: {{
                            'Authorization': `Bearer ${{token}}`
                        }}
                    }});
                    
                    if (response.status === 401) {{
                        // Token invalid or account locked
                        logout();
                    }} else if (response.ok) {{
                        const user = await response.json();
                        // Check if account is locked (this should be handled server-side, but double-check)
                        if (!user.is_active) {{
                            window.location.reload(); // Will show locked message
                        }}
                    }}
                }} catch (error) {{
                    console.error('Error checking account status:', error);
                }}
            }}
            
            // Run check on page load
            checkAccountStatus();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

