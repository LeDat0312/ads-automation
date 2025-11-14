# -*- coding: utf-8 -*-
"""
UI Helper Functions - Shared components for HTML pages
"""
from typing import Optional
from app.models.user import User


def get_user_dropdown_menu(current_user: Optional[User]) -> str:
    """
    Generate user dropdown menu HTML (góc trên bên phải)
    Similar to the dropdown in the provided image
    """
    if not current_user:
        return ""
    
    avatar_url = f"/static/avatars/{current_user.avatar}" if current_user.avatar and current_user.avatar != 'default_avatar.png' else ""
    display_name = current_user.display_name or current_user.username
    username = current_user.username
    
    # Build avatar HTML separately to avoid backslash in f-string
    if avatar_url:
        avatar_html = f'<img src="{avatar_url}" alt="Avatar" onerror="handleAvatarError(this)">'
        placeholder_display = 'none'
    else:
        avatar_html = ''
        placeholder_display = 'flex'
    
    return f"""
    <div class="user-menu-container" id="userMenuContainer">
        <div class="user-menu-trigger" onclick="toggleUserMenu()">
            <div class="user-avatar">
                {avatar_html}
                <div class="avatar-placeholder" style="display: {placeholder_display}">
                    {display_name[0].upper()}
                </div>
            </div>
            <span class="username">{display_name}</span>
            <svg class="dropdown-arrow" width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2 4L6 8L10 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="user-menu-dropdown" id="userMenuDropdown" style="display: none;">
            <a href="/profile" class="menu-item">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M10 10C12.7614 10 15 7.76142 15 5C15 2.23858 12.7614 0 10 0C7.23858 0 5 2.23858 5 5C5 7.76142 7.23858 10 10 10Z" fill="currentColor"/>
                    <path d="M10 12C5.58172 12 2 13.7909 2 16V20H18V16C18 13.7909 14.4183 12 10 12Z" fill="currentColor"/>
                </svg>
                <span>Trang cá nhân</span>
            </a>
            <a href="/change-password" class="menu-item">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11.5 2.5L17.5 8.5M15.5 2.5L17.5 4.5M15.5 8.5L17.5 6.5M2.5 5.5V16.5C2.5 17.0523 2.94772 17.5 3.5 17.5H16.5C17.0523 17.5 17.5 17.0523 17.5 16.5V8.5M2.5 5.5C2.5 4.94772 2.94772 4.5 3.5 4.5H10.5M2.5 5.5L10.5 13.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>Thay đổi mật khẩu</span>
            </a>
            <div class="menu-divider"></div>
            <a href="#" class="menu-item" onclick="logout(); return false;">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7.5 15L12.5 10L7.5 5M12.5 10H2.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2.5 2.5H10.5C11.6046 2.5 12.5 3.39543 12.5 4.5V7.5M12.5 12.5V15.5C12.5 16.6046 11.6046 17.5 10.5 17.5H2.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>Đăng xuất</span>
            </a>
        </div>
    </div>
    
    <style>
        .user-menu-container {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }}
        
        .user-menu-trigger {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        .user-menu-trigger:hover {{
            background: rgba(255, 255, 255, 1);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }}
        
        .user-avatar {{
            width: 36px;
            height: 36px;
            border-radius: 50%;
            overflow: hidden;
            position: relative;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .user-avatar img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .avatar-placeholder {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 16px;
        }}
        
        .username {{
            font-weight: 500;
            color: #1e293b;
            font-size: 14px;
        }}
        
        .dropdown-arrow {{
            color: #64748b;
            transition: transform 0.3s ease;
        }}
        
        .user-menu-container.active .dropdown-arrow {{
            transform: rotate(180deg);
        }}
        
        .user-menu-dropdown {{
            position: absolute;
            top: calc(100% + 8px);
            right: 0;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
            min-width: 220px;
            overflow: hidden;
            border: 1px solid #e2e8f0;
            z-index: 1002;
        }}
        
        .menu-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            color: #1e293b;
            text-decoration: none;
            transition: all 0.2s ease;
            font-size: 14px;
        }}
        
        .menu-item:hover {{
            background: #f1f5f9;
        }}
        
        .menu-item svg {{
            color: #64748b;
            flex-shrink: 0;
        }}
        
        .menu-item:hover svg {{
            color: #667eea;
        }}
        
        .menu-divider {{
            height: 1px;
            background: #e2e8f0;
            margin: 4px 0;
        }}
    </style>
    
    <script>
        function toggleUserMenu() {{
            const container = document.getElementById('userMenuContainer');
            const dropdown = document.getElementById('userMenuDropdown');
            
            if (dropdown.style.display === 'none' || !dropdown.style.display) {{
                dropdown.style.display = 'block';
                container.classList.add('active');
            }} else {{
                dropdown.style.display = 'none';
                container.classList.remove('active');
            }}
        }}
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {{
            const container = document.getElementById('userMenuContainer');
            if (container && !container.contains(event.target)) {{
                const dropdown = document.getElementById('userMenuDropdown');
                if (dropdown) {{
                    dropdown.style.display = 'none';
                    container.classList.remove('active');
                }}
            }}
        }});
        
        // Handle avatar error
        function handleAvatarError(img) {{
            img.style.display = 'none';
            const placeholder = img.nextElementSibling;
            if (placeholder) {{
                placeholder.style.display = 'flex';
            }}
        }}
    </script>
    """


def get_account_locked_message() -> str:
    """
    Generate account locked message HTML
    """
    return """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tài Khoản Đã Bị Khóa</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .locked-container {
                background: white;
                border-radius: 24px;
                padding: 48px;
                max-width: 500px;
                width: 100%;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }
            .locked-icon {
                font-size: 80px;
                margin-bottom: 24px;
            }
            h1 {
                font-size: 28px;
                color: #1e293b;
                margin-bottom: 16px;
            }
            p {
                font-size: 16px;
                color: #64748b;
                margin-bottom: 32px;
                line-height: 1.6;
            }
            .contact-info {
                background: #f1f5f9;
                border-radius: 12px;
                padding: 24px;
                margin-top: 32px;
                text-align: left;
            }
            .contact-info h3 {
                font-size: 18px;
                color: #1e293b;
                margin-bottom: 16px;
            }
            .contact-item {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 12px;
                font-size: 14px;
                color: #475569;
            }
            .contact-item a {
                color: #667eea;
                text-decoration: none;
            }
            .contact-item a:hover {
                text-decoration: underline;
            }
            .btn-logout {
                margin-top: 24px;
                padding: 12px 24px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .btn-logout:hover {
                background: #5568d3;
            }
        </style>
    </head>
    <body>
        <div class="locked-container">
            <div class="locked-icon">🔒</div>
            <h1>Tài Khoản Đã Bị Khóa</h1>
            <p>Tài khoản của bạn đã bị khóa, vui lòng liên hệ Admin để biết thêm chi tiết.</p>
            
            <div class="contact-info">
                <h3>📞 Thông Tin Liên Hệ</h3>
                <div class="contact-item">
                    <span>📘 Facebook:</span>
                    <a href="https://www.facebook.com/lev.dat2002" target="_blank">lev.dat2002</a>
                </div>
                <div class="contact-item">
                    <span>💬 Zalo:</span>
                    <a href="https://zalo.me/0386650359" target="_blank">038.665.0359</a>
                </div>
                <div class="contact-item">
                    <span>📱 Số điện thoại:</span>
                    <a href="tel:0386650359">038.665.0359</a>
                </div>
            </div>
            
            <button class="btn-logout" onclick="logout()">Đăng Xuất</button>
        </div>
        
        <script>
            function logout() {
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
                window.location.href = '/auth/login';
            }
        </script>
    </body>
    </html>
    """

