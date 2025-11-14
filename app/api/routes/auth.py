# -*- coding: utf-8 -*-
"""
Authentication Routes - Login/Register/Logout
"""
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.models.user import User
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    get_current_user
)

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from token (optional, returns None if not authenticated)"""
    if not credentials:
        return None
    try:
        token = credentials.credentials
        return get_current_user(db, token)
    except:
        return None


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Đăng Nhập - Facebook Ads Automation</title>
        <link rel="icon" type="image/png" href="/static/favicon.png">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            .login-container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                padding: 48px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                width: 100%;
                max-width: 420px;
                animation: fadeInUp 0.6s ease;
            }
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            .logo {
                text-align: center;
                margin-bottom: 32px;
            }
            .logo img {
                width: 80px;
                height: 80px;
                margin-bottom: 16px;
            }
            .logo h1 {
                font-size: 28px;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 8px;
            }
            .logo p {
                color: #64748b;
                font-size: 14px;
            }
            .form-group {
                margin-bottom: 24px;
            }
            .form-group label {
                display: block;
                font-size: 14px;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 8px;
            }
            .form-group input {
                width: 100%;
                padding: 14px 18px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 15px;
                transition: all 0.3s ease;
                background: white;
            }
            .form-group input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            }
            .remember-me {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 24px;
            }
            .remember-me input[type="checkbox"] {
                width: 18px;
                height: 18px;
                cursor: pointer;
            }
            .remember-me label {
                font-size: 14px;
                color: #64748b;
                cursor: pointer;
            }
            .btn-login {
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }
            .btn-login:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
            }
            .btn-login:active {
                transform: translateY(0);
            }
            .error-message {
                background: #fee2e2;
                color: #991b1b;
                padding: 12px 16px;
                border-radius: 8px;
                margin-bottom: 24px;
                font-size: 14px;
                display: none;
            }
            .error-message.show {
                display: block;
            }
            .loading {
                display: none;
                text-align: center;
                padding: 12px;
            }
            .loading.show {
                display: block;
            }
            .spinner {
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-top: 3px solid white;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                animation: spin 1s linear infinite;
                display: inline-block;
                margin-right: 8px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">
                <img src="/static/favicon.png" alt="Logo" onerror="this.style.display='none'">
                <h1>🚀 Facebook Ads Automation</h1>
                <p>Đăng nhập để tiếp tục</p>
            </div>
            
            <div class="error-message" id="error-message"></div>
            
            <form id="login-form" onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label for="username">Tên đăng nhập</label>
                    <input type="text" id="username" name="username" required autofocus>
                </div>
                
                <div class="form-group">
                    <label for="password">Mật khẩu</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <div class="remember-me">
                    <input type="checkbox" id="remember" name="remember">
                    <label for="remember">Ghi nhớ đăng nhập (30 ngày)</label>
                </div>
                
                <button type="submit" class="btn-login" id="login-btn">
                    <span id="login-text">Đăng Nhập</span>
                    <span class="loading" id="loading">
                        <span class="spinner"></span>Đang đăng nhập...
                    </span>
                </button>
            </form>
        </div>
        
        <script>
            async function handleLogin(event) {
                event.preventDefault();
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const remember = document.getElementById('remember').checked;
                const errorDiv = document.getElementById('error-message');
                const loginBtn = document.getElementById('login-btn');
                const loginText = document.getElementById('login-text');
                const loading = document.getElementById('loading');
                
                // Hide error
                errorDiv.classList.remove('show');
                
                // Show loading
                loginText.style.display = 'none';
                loading.classList.add('show');
                loginBtn.disabled = true;
                
                try {
                    const formData = new FormData();
                    formData.append('username', username);
                    formData.append('password', password);
                    if (remember) {
                        formData.append('remember', 'true');
                    }
                    
                    const response = await fetch('/auth/login', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok && data.access_token) {
                        // Save token to localStorage
                        localStorage.setItem('access_token', data.access_token);
                        localStorage.setItem('user', JSON.stringify(data.user));
                        
                        // Redirect to home
                        window.location.href = '/';
                    } else {
                        // Show error
                        errorDiv.textContent = data.detail || 'Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.';
                        errorDiv.classList.add('show');
                    }
                } catch (error) {
                    errorDiv.textContent = 'Lỗi kết nối. Vui lòng thử lại.';
                    errorDiv.classList.add('show');
                } finally {
                    // Hide loading
                    loginText.style.display = 'block';
                    loading.classList.remove('show');
                    loginBtn.disabled = false;
                }
            }
            
            // Check if already logged in
            if (localStorage.getItem('access_token')) {
                window.location.href = '/';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Login endpoint"""
    # Find user
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa"
        )
    
    # Create token
    token_data = {"sub": user.username}
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role
        }
    }


@router.post("/logout")
async def logout():
    """Logout endpoint"""
    return {"message": "Đăng xuất thành công"}


@router.get("/me")
async def get_me(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get current user info"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chưa đăng nhập"
        )
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "role": current_user.role,
        "avatar": current_user.avatar
    }

