# -*- coding: utf-8 -*-
"""
Home Page - Trang chủ duy nhất với navigation buttons
Tất cả các trang khác được điều hướng từ đây
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def _get_home_css():
    """CSS cho trang chủ"""
    return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .home-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 60px 40px;
            max-width: 900px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            animation: fadeInUp 0.6s ease-out;
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
        
        .home-header {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .home-title {
            font-size: 42px;
            font-weight: 700;
            color: #1c1e21;
            margin-bottom: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .home-subtitle {
            font-size: 18px;
            color: #65676b;
            line-height: 1.6;
        }
        
        .nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        
        .nav-card {
            background: #fff;
            border: 2px solid #e4e6eb;
            border-radius: 16px;
            padding: 30px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            color: inherit;
            display: block;
        }
        
        .nav-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
            border-color: #667eea;
        }
        
        .nav-card-icon {
            font-size: 48px;
            margin-bottom: 16px;
            display: block;
        }
        
        .nav-card-title {
            font-size: 20px;
            font-weight: 600;
            color: #1c1e21;
            margin-bottom: 8px;
        }
        
        .nav-card-description {
            font-size: 14px;
            color: #65676b;
            line-height: 1.5;
        }
        
        .nav-card.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            border-color: transparent;
        }
        
        .nav-card.primary .nav-card-title,
        .nav-card.primary .nav-card-description {
            color: #fff;
        }
        
        .nav-card.primary:hover {
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.5);
        }
        
        @media (max-width: 768px) {
            .home-container {
                padding: 40px 24px;
            }
            
            .home-title {
                font-size: 32px;
            }
            
            .nav-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Trang chủ duy nhất với các nút điều hướng"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Facebook Ads Automation - Trang Chủ</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        {_get_home_css()}
    </head>
    <body>
        <div class="home-container">
            <div class="home-header">
                <h1 class="home-title">🚀 Facebook Ads Automation</h1>
                <p class="home-subtitle">
                    Hệ thống tự động hóa quảng cáo Facebook thông minh.<br>
                    Tối ưu hóa ngân sách và hiệu suất quảng cáo tự động.
                </p>
            </div>
            
            <div class="nav-grid">
                <a href="/tactics" class="nav-card primary" onclick="navigateTo('/tactics'); return false;">
                    <span class="nav-card-icon">⚡</span>
                    <div class="nav-card-title">Chọn Chiến Thuật</div>
                    <div class="nav-card-description">
                        Chọn chiến thuật automation phù hợp với nhu cầu của bạn
                    </div>
                </a>
                
                <a href="/rules/" class="nav-card" onclick="navigateTo('/rules/'); return false;">
                    <span class="nav-card-icon">📋</span>
                    <div class="nav-card-title">Quản Lý Rules</div>
                    <div class="nav-card-description">
                        Xem và quản lý tất cả các automation rules
                    </div>
                </a>
                
                <a href="/settings/accounts/" class="nav-card" onclick="navigateTo('/settings/accounts/'); return false;">
                    <span class="nav-card-icon">👥</span>
                    <div class="nav-card-title">Quản Lý Accounts</div>
                    <div class="nav-card-description">
                        Quản lý Facebook Ad Accounts và cấu hình
                    </div>
                </a>
                
                <a href="/api/dashboard/" class="nav-card" onclick="navigateTo('/api/dashboard/'); return false;">
                    <span class="nav-card-icon">📊</span>
                    <div class="nav-card-title">Dashboard</div>
                    <div class="nav-card-description">
                        Xem tổng quan hiệu suất và thống kê quảng cáo
                    </div>
                </a>
            </div>
        </div>
        
        <script>
            function navigateTo(url) {{
                window.location.href = url;
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

