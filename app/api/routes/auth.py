# -*- coding: utf-8 -*-
"""
Authentication Routes - Login/Register/Logout
"""
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, Response
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
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from token (optional, returns None if not authenticated)
    Checks both Bearer token in Authorization header and access_token cookie
    Also checks if user is_active - returns None if account is locked
    """
    token = None
    
    # Try Bearer token first
    if credentials:
        token = credentials.credentials
    
    # Try cookie if no Bearer token
    if not token:
        token = request.cookies.get('access_token')
    
    if not token:
        return None
    
    try:
        user = get_current_user(db, token)
        # Check if user is active
        if user and not user.is_active:
            # Return None if account is locked (will trigger login redirect)
            return None
        return user
    except:
        return None


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page with AI character"""
    html_content = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Đăng Nhập - Facebook Ads Automation</title>
        <link rel="icon" type="image/png" href="/static/favicon.png">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                overflow: hidden;
                position: relative;
            }
            
            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            /* Floating particles effect */
            .particles {
                position: absolute;
                width: 100%;
                height: 100%;
                overflow: hidden;
                pointer-events: none;
            }
            
            .particle {
                position: absolute;
                width: 10px;
                height: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 50%;
                animation: float 20s infinite;
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0) translateX(0); opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { transform: translateY(-100vh) translateX(100px); opacity: 0; }
            }
            
            .main-container {
                display: flex;
                gap: 60px;
                align-items: center;
                animation: fadeInUp 0.8s ease;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(40px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* AI Character */
            .ai-container {
                position: relative;
                width: 280px;
                height: 280px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .ai-character {
                position: relative;
                width: 200px;
                height: 200px;
            }
            
            .ai-head {
                width: 200px;
                height: 200px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                position: relative;
                box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
                animation: float-ai 3s ease-in-out infinite;
            }
            
            @keyframes float-ai {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
            }
            
            /* AI Antenna */
            .ai-antenna {
                position: absolute;
                top: -30px;
                left: 50%;
                transform: translateX(-50%);
                width: 4px;
                height: 25px;
                background: #667eea;
                border-radius: 2px;
            }
            
            .ai-antenna::after {
                content: '';
                position: absolute;
                top: -8px;
                left: 50%;
                transform: translateX(-50%);
                width: 12px;
                height: 12px;
                background: #f093fb;
                border-radius: 50%;
                box-shadow: 0 0 15px rgba(240, 147, 251, 0.8);
                animation: pulse 2s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0%, 100% { transform: translateX(-50%) scale(1); }
                50% { transform: translateX(-50%) scale(1.3); }
            }
            
            /* AI Eyes Container */
            .ai-eyes {
                position: absolute;
                top: 60px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 40px;
                transition: all 0.3s ease;
            }
            
            .ai-eye {
                width: 50px;
                height: 50px;
                background: white;
                border-radius: 50%;
                position: relative;
                overflow: hidden;
                box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            
            .ai-pupil {
                width: 24px;
                height: 24px;
                background: #1e293b;
                border-radius: 50%;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                transition: all 0.15s ease;
            }
            
            .ai-pupil::after {
                content: '';
                position: absolute;
                top: 6px;
                left: 6px;
                width: 8px;
                height: 8px;
                background: white;
                border-radius: 50%;
            }
            
            /* AI Hands for covering eyes */
            .ai-hands {
                position: absolute;
                top: 60px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 40px;
                opacity: 0;
                pointer-events: none;
                transition: all 0.3s ease;
            }
            
            .ai-hands.show {
                opacity: 1;
            }
            
            .ai-hand {
                width: 60px;
                height: 40px;
                background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
                border-radius: 20px;
                position: relative;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            }
            
            /* AI Mouth */
            .ai-mouth {
                position: absolute;
                bottom: 50px;
                left: 50%;
                transform: translateX(-50%);
                width: 60px;
                height: 30px;
                border: 4px solid white;
                border-top: none;
                border-radius: 0 0 40px 40px;
                transition: all 0.3s ease;
            }
            
            .ai-mouth.happy {
                border-radius: 0 0 50px 50px;
                width: 70px;
            }
            
            .ai-mouth.shy {
                width: 40px;
                height: 20px;
            }
            
            /* Login Container */
            .login-container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                padding: 48px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                width: 100%;
                max-width: 420px;
                animation: fadeInUp 0.6s ease 0.2s backwards;
            }
            
            .logo {
                text-align: center;
                margin-bottom: 32px;
            }
            
            .logo h1 {
                font-size: 28px;
                font-weight: 800;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 8px;
                letter-spacing: -0.5px;
            }
            
            .logo p {
                color: #64748b;
                font-size: 14px;
                font-weight: 500;
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
            
            .input-wrapper {
                position: relative;
            }
            
            .form-group input {
                width: 100%;
                padding: 14px 18px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 15px;
                transition: all 0.3s ease;
                background: white;
                font-family: inherit;
            }
            
            .form-group input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            }
            
            .input-icon {
                position: absolute;
                right: 16px;
                top: 50%;
                transform: translateY(-50%);
                color: #94a3b8;
                font-size: 18px;
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
                accent-color: #667eea;
            }
            
            .remember-me label {
                font-size: 14px;
                color: #64748b;
                cursor: pointer;
                font-weight: 500;
            }
            
            .btn-login {
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                font-family: inherit;
                letter-spacing: 0.3px;
            }
            
            .btn-login:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
            }
            
            .btn-login:active:not(:disabled) {
                transform: translateY(0);
            }
            
            .btn-login:disabled {
                opacity: 0.7;
                cursor: not-allowed;
            }
            
            .error-message {
                background: linear-gradient(135deg, #fee2e2, #fecaca);
                color: #991b1b;
                padding: 14px 18px;
                border-radius: 12px;
                margin-bottom: 24px;
                font-size: 14px;
                font-weight: 500;
                display: none;
                border-left: 4px solid #dc2626;
                animation: shake 0.5s ease;
            }
            
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-10px); }
                75% { transform: translateX(10px); }
            }
            
            .error-message.show {
                display: block;
            }
            
            .loading {
                display: none;
            }
            
            .loading.show {
                display: inline;
            }
            
            .spinner {
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-top: 3px solid white;
                border-radius: 50%;
                width: 18px;
                height: 18px;
                animation: spin 0.8s linear infinite;
                display: inline-block;
                margin-right: 8px;
                vertical-align: middle;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .main-container {
                    gap: 30px;
                }
                
                .ai-container {
                    width: 200px;
                    height: 200px;
                }
                
                .ai-character {
                    width: 150px;
                    height: 150px;
                }
                
                .ai-head {
                    width: 150px;
                    height: 150px;
                }
                
                .ai-eyes {
                    top: 45px;
                    gap: 30px;
                }
                
                .ai-eye {
                    width: 35px;
                    height: 35px;
                }
                
                .ai-pupil {
                    width: 18px;
                    height: 18px;
                }
                
                .ai-hands {
                    top: 45px;
                    gap: 30px;
                }
                
                .ai-hand {
                    width: 45px;
                    height: 30px;
                }
                
                .ai-mouth {
                    bottom: 35px;
                    width: 45px;
                    height: 22px;
                }
                
                .login-container {
                    padding: 32px;
                }
            }
        </style>
    </head>
    <body>
        <!-- Floating particles -->
        <div class="particles" id="particles"></div>
        
        <div class="main-container">
            <!-- AI Character -->
            <div class="ai-container">
                <div class="ai-character">
                    <div class="ai-head">
                        <div class="ai-antenna"></div>
                        
                        <!-- Eyes -->
                        <div class="ai-eyes" id="ai-eyes">
                            <div class="ai-eye">
                                <div class="ai-pupil" id="pupil-left"></div>
                            </div>
                            <div class="ai-eye">
                                <div class="ai-pupil" id="pupil-right"></div>
                            </div>
                        </div>
                        
                        <!-- Hands for covering eyes -->
                        <div class="ai-hands" id="ai-hands">
                            <div class="ai-hand"></div>
                            <div class="ai-hand"></div>
                        </div>
                        
                        <!-- Mouth -->
                        <div class="ai-mouth" id="ai-mouth"></div>
                    </div>
                </div>
            </div>
            
            <!-- Login Form -->
            <div class="login-container">
                <div class="logo">
                    <h1>🚀 Facebook Ads AI</h1>
                    <p>Đăng nhập để tiếp tục quản lý quảng cáo</p>
                </div>
                
                <div class="error-message" id="error-message"></div>
                
                <form id="login-form" onsubmit="handleLogin(event)">
                    <div class="form-group">
                        <label for="username">👤 Tên đăng nhập</label>
                        <div class="input-wrapper">
                            <input type="text" id="username" name="username" required autofocus 
                                   placeholder="Nhập tên đăng nhập">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">🔒 Mật khẩu</label>
                        <div class="input-wrapper">
                            <input type="password" id="password" name="password" required 
                                   placeholder="Nhập mật khẩu">
                        </div>
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
        </div>
        
        <script>
            // Create floating particles
            function createParticles() {
                const particlesContainer = document.getElementById('particles');
                for (let i = 0; i < 20; i++) {
                    const particle = document.createElement('div');
                    particle.className = 'particle';
                    particle.style.left = Math.random() * 100 + '%';
                    particle.style.animationDelay = Math.random() * 20 + 's';
                    particle.style.animationDuration = (15 + Math.random() * 10) + 's';
                    particlesContainer.appendChild(particle);
                }
            }
            createParticles();
            
            // AI Character eye tracking
            const pupilLeft = document.getElementById('pupil-left');
            const pupilRight = document.getElementById('pupil-right');
            const aiEyes = document.getElementById('ai-eyes');
            const aiHands = document.getElementById('ai-hands');
            const aiMouth = document.getElementById('ai-mouth');
            const passwordInput = document.getElementById('password');
            const usernameInput = document.getElementById('username');
            
            let isPasswordFocused = false;
            
            // Track mouse movement for eye following
            document.addEventListener('mousemove', (e) => {
                if (isPasswordFocused) return; // Don't track if password is focused
                
                const eyes = document.querySelectorAll('.ai-eye');
                eyes.forEach(eye => {
                    const rect = eye.getBoundingClientRect();
                    const eyeX = rect.left + rect.width / 2;
                    const eyeY = rect.top + rect.height / 2;
                    
                    const deltaX = e.clientX - eyeX;
                    const deltaY = e.clientY - eyeY;
                    const angle = Math.atan2(deltaY, deltaX);
                    const distance = Math.min(Math.sqrt(deltaX * deltaX + deltaY * deltaY) / 20, 12);
                    
                    const pupil = eye.querySelector('.ai-pupil');
                    const pupilX = Math.cos(angle) * distance;
                    const pupilY = Math.sin(angle) * distance;
                    
                    pupil.style.transform = `translate(calc(-50% + ${pupilX}px), calc(-50% + ${pupilY}px))`;
                });
            });
            
            // Password field focus - cover eyes
            passwordInput.addEventListener('focus', () => {
                isPasswordFocused = true;
                aiHands.classList.add('show');
                aiMouth.classList.add('shy');
                
                // Reset pupil position
                pupilLeft.style.transform = 'translate(-50%, -50%)';
                pupilRight.style.transform = 'translate(-50%, -50%)';
            });
            
            passwordInput.addEventListener('blur', () => {
                isPasswordFocused = false;
                aiHands.classList.remove('show');
                aiMouth.classList.remove('shy');
            });
            
            // Username field focus - happy
            usernameInput.addEventListener('focus', () => {
                aiMouth.classList.add('happy');
            });
            
            usernameInput.addEventListener('blur', () => {
                aiMouth.classList.remove('happy');
            });
            
            // Login form handler
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
                        
                        // Show success state
                        aiMouth.classList.add('happy');
                        
                        // Redirect after short delay
                        setTimeout(() => {
                            window.location.href = '/';
                        }, 300);
                    } else {
                        // Show error
                        errorDiv.textContent = data.detail || 'Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.';
                        errorDiv.classList.add('show');
                        
                        // Shake the AI head on error
                        const aiHead = document.querySelector('.ai-head');
                        aiHead.style.animation = 'none';
                        setTimeout(() => {
                            aiHead.style.animation = 'float-ai 3s ease-in-out infinite, shake 0.5s ease';
                        }, 10);
                    }
                } catch (error) {
                    errorDiv.textContent = 'Lỗi kết nối. Vui lòng thử lại.';
                    errorDiv.classList.add('show');
                } finally {
                    // Hide loading
                    loginText.style.display = 'inline';
                    loading.classList.remove('show');
                    loginBtn.disabled = false;
                }
            }
            
            // Helper function to get cookie
            function getCookie(name) {
                const value = `; ${document.cookie}`;
                const parts = value.split(`; ${name}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }
            
            // Check if already logged in - redirect to home if token exists
            const token = localStorage.getItem('access_token') || getCookie('access_token');
            if (token) {
                // Only redirect if we're not already on home page
                if (window.location.pathname === '/auth/login' || window.location.pathname === '/auth/login/') {
                    window.location.href = '/';
                }
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
    
    # Create response with cookie
    response = JSONResponse({
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role
        }
    })
    
    # Set cookie for server-side auth check
    max_age = 30 * 24 * 60 * 60 if remember else None  # 30 days if remember, session cookie otherwise
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=max_age,
        httponly=False,  # Allow JS to read for localStorage sync
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return response


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
        "avatar": current_user.avatar,
        "is_active": current_user.is_active
    }

