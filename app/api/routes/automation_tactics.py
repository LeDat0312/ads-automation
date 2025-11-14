# -*- coding: utf-8 -*-
"""
Automation Tactics UI - Dựa trên thiết kế Madgicx
Trang chọn chiến thuật automation với giao diện hiện đại
"""
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.core.database import get_db
from app.models.account_prefix import Account, Prefix
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def _get_madgicx_style_css():
    """CSS theo phong cách Madgicx"""
    return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f6f7;
            color: #1c1e21;
            line-height: 1.5;
        }
        
        .page-container {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* Header */
        .page-header {
            background: #fff;
            border-bottom: 1px solid #e4e6eb;
            padding: 16px 24px;
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .back-button {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: #f0f2f5;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            color: #1c1e21;
            transition: background 0.2s;
        }
        
        .back-button:hover {
            background: #e4e6eb;
        }
        
        .page-title {
            font-size: 24px;
            font-weight: 600;
            color: #1c1e21;
        }
        
        /* Main Content */
        .page-body {
            flex: 1;
            padding: 24px;
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
        }
        
        /* Hero Section */
        .hero-section {
            text-align: center;
            padding: 40px 20px;
            margin-bottom: 40px;
        }
        
        .hero-title {
            font-size: 32px;
            font-weight: 700;
            color: #1c1e21;
            margin-bottom: 16px;
        }
        
        .hero-subtitle {
            font-size: 16px;
            color: #65676b;
            max-width: 600px;
            margin: 0 auto 40px;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin-bottom: 60px;
        }
        
        .feature-card {
            display: flex;
            align-items: flex-start;
            gap: 16px;
            padding: 24px;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .feature-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .feature-icon {
            width: 48px;
            height: 48px;
            background: #f0f2f5;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-size: 24px;
        }
        
        .feature-content h3 {
            font-size: 16px;
            font-weight: 600;
            color: #1c1e21;
            margin-bottom: 8px;
        }
        
        .feature-content p {
            font-size: 14px;
            color: #65676b;
            line-height: 1.5;
        }
        
        /* Tactics Section */
        .tactics-section {
            margin-bottom: 60px;
        }
        
        .section-title {
            font-size: 24px;
            font-weight: 600;
            color: #1c1e21;
            margin-bottom: 24px;
        }
        
        .tactics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
        }
        
        .tactic-card {
            background: #fff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            border: 2px solid transparent;
        }
        
        .tactic-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            border-color: #1877f2;
        }
        
        .tactic-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }
        
        .tactic-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: #fff;
        }
        
        .tactic-icon.purple {
            background: #8b5cf6;
        }
        
        .tactic-icon.rose {
            background: #f43f5e;
        }
        
        .tactic-icon.blue {
            background: #3b82f6;
        }
        
        .tactic-name {
            flex: 1;
        }
        
        .tactic-name h3 {
            font-size: 18px;
            font-weight: 600;
            color: #1c1e21;
            margin-bottom: 4px;
        }
        
        .tactic-level {
            font-size: 12px;
            color: #65676b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .tactic-description {
            font-size: 14px;
            color: #65676b;
            line-height: 1.6;
        }
        
        /* Strategies Section */
        .strategies-section {
            margin-top: 60px;
        }
        
        .strategies-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
        }
        
        .strategies-toolbar {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .campaign-type-select {
            padding: 8px 12px;
            border: 1px solid #ccd0d5;
            border-radius: 6px;
            background: #fff;
            font-size: 14px;
            color: #1c1e21;
            cursor: pointer;
        }
        
        .filter-token {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            background: #f0f2f5;
            border-radius: 20px;
            font-size: 14px;
            color: #1c1e21;
            cursor: pointer;
        }
        
        .strategies-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .strategy-card {
            background: #fff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .strategy-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: #f43f5e;
        }
        
        .strategy-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .strategy-title {
            font-size: 16px;
            font-weight: 600;
            color: #1c1e21;
            margin-bottom: 8px;
        }
        
        .strategy-description {
            font-size: 14px;
            color: #65676b;
            line-height: 1.5;
            margin-bottom: 12px;
        }
        
        .strategy-actions {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .action-icon {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .action-icon:hover {
            background: #f0f2f5;
        }
        
        .create-custom-card {
            background: #fff;
            border: 2px dashed #ccd0d5;
            border-radius: 12px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: border-color 0.2s, background 0.2s;
        }
        
        .create-custom-card:hover {
            border-color: #1877f2;
            background: #f0f8ff;
        }
        
        .create-custom-icon {
            width: 64px;
            height: 64px;
            margin: 0 auto 16px;
            background: #f0f2f5;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            color: #8b5cf6;
        }
        
        .create-custom-title {
            font-size: 18px;
            font-weight: 600;
            color: #1c1e21;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .page-body {
                padding: 16px;
            }
            
            .hero-title {
                font-size: 24px;
            }
            
            .features-grid,
            .tactics-grid,
            .strategies-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """


@router.get("/tactics", response_class=HTMLResponse)
async def automation_tactics_page(request: Request, db: Session = Depends(get_db)):
    """Trang chọn chiến thuật automation - Phong cách Madgicx"""
    
    # Lấy danh sách accounts và prefixes
    accounts = db.query(Account).filter(Account.enabled == True).order_by(Account.account_name).all()
    prefixes = db.query(Prefix).filter(Prefix.enabled == True).order_by(Prefix.prefix).all()
    
    # Tạo HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chọn Chiến Thuật Automation - Facebook Ads</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        {_get_madgicx_style_css()}
    </head>
    <body>
        <div class="page-container">
            <!-- Header -->
            <div class="page-header">
                <button class="back-button" onclick="window.history.back()">
                    <span>←</span>
                    <span>Quay lại</span>
                </button>
                <h1 class="page-title">Chọn Chiến Thuật Automation</h1>
            </div>
            
            <!-- Main Content -->
            <div class="page-body">
                <!-- Hero Section -->
                <div class="hero-section">
                    <h2 class="hero-title">Tự động hóa Quảng cáo Facebook</h2>
                    <p class="hero-subtitle">
                        Chọn chiến thuật automation phù hợp để tối ưu hóa hiệu suất quảng cáo của bạn. 
                        Hệ thống sẽ tự động điều chỉnh ngân sách và trạng thái quảng cáo dựa trên hiệu suất thực tế.
                    </p>
                    
                    <div class="features-grid">
                        <div class="feature-card">
                            <div class="feature-icon">⚙️</div>
                            <div class="feature-content">
                                <h3>1. Chiến Thuật & Thực Hành Tốt Nhất</h3>
                                <p>Nhiều quy tắc automation và chiến lược được đóng gói thành các chiến thuật đơn giản</p>
                            </div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🎯</div>
                            <div class="feature-content">
                                <h3>2. Tối Ưu Hóa Thời Gian Thực</h3>
                                <p>Trong khi tiêu chuẩn thị trường là 15/30 phút, hệ thống của chúng tôi kích hoạt ngay lập tức</p>
                            </div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">📊</div>
                            <div class="feature-content">
                                <h3>3. Quy Tắc Động</h3>
                                <p>Thiết lập quy tắc dựa trên các trường động luôn phù hợp khi hiệu suất thay đổi</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Tactics Section -->
                <div class="tactics-section">
                    <h2 class="section-title">Chiến Thuật Automation</h2>
                    <div class="tactics-grid">
                        <!-- SURF Ad Set Level -->
                        <div class="tactic-card" onclick="selectTactic('surf-adset')">
                            <div class="tactic-header">
                                <div class="tactic-icon purple">🌊</div>
                                <div class="tactic-name">
                                    <h3>SURF</h3>
                                    <div class="tactic-level">Cấp độ Nhóm quảng cáo</div>
                                </div>
                            </div>
                            <p class="tactic-description">
                                SURF xác định xu hướng hiệu suất mạnh và tự động tận dụng động lực tích cực 
                                bằng cách tăng ngân sách của nhóm quảng cáo vượt quá giới hạn ban đầu. 
                                Ngân sách sẽ tự động đặt lại vào thời gian địa phương đã chọn.
                            </p>
                        </div>
                        
                        <!-- STOP LOSS Ad Set Level -->
                        <div class="tactic-card" onclick="selectTactic('stop-loss-adset')">
                            <div class="tactic-header">
                                <div class="tactic-icon purple">🚩</div>
                                <div class="tactic-name">
                                    <h3>STOP LOSS</h3>
                                    <div class="tactic-level">Cấp độ Nhóm quảng cáo</div>
                                </div>
                            </div>
                            <p class="tactic-description">
                                Stop Loss bảo vệ ngân sách của bạn bằng cách tạm dừng các nhóm quảng cáo 
                                có hiệu suất thấp với động lực tiêu cực ngay khi phát hiện. 
                                Vào thời gian địa phương đã chọn, nó sẽ bật lại nhóm quảng cáo.
                            </p>
                        </div>
                        
                        <!-- STOP LOSS Ad Level -->
                        <div class="tactic-card" onclick="selectTactic('stop-loss-ad')">
                            <div class="tactic-header">
                                <div class="tactic-icon rose">🚩</div>
                                <div class="tactic-name">
                                    <h3>STOP LOSS</h3>
                                    <div class="tactic-level">Cấp độ Quảng cáo</div>
                                </div>
                            </div>
                            <p class="tactic-description">
                                Stop Loss bảo vệ ngân sách của bạn bằng cách tạm dừng các quảng cáo 
                                có hiệu suất thấp với động lực tiêu cực ngay khi phát hiện. 
                                Vào thời gian địa phương đã chọn, nó sẽ bật lại quảng cáo.
                            </p>
                        </div>
                        
                        <!-- SUNSETTING Ad Set Level -->
                        <div class="tactic-card" onclick="selectTactic('sunsetting-adset')">
                            <div class="tactic-header">
                                <div class="tactic-icon purple">🌅</div>
                                <div class="tactic-name">
                                    <h3>SUNSETTING</h3>
                                    <div class="tactic-level">Cấp độ Nhóm quảng cáo</div>
                                </div>
                            </div>
                            <p class="tactic-description">
                                Sunsetting theo dõi hiệu suất theo thời gian để xác định các nhóm quảng cáo 
                                có hiệu suất thấp và sau đó thực hiện một loạt các bước để bảo vệ ngân sách của bạn theo thời gian.
                            </p>
                        </div>
                        
                        <!-- REVIVE Ad Set Level -->
                        <div class="tactic-card" onclick="selectTactic('revive-adset')">
                            <div class="tactic-header">
                                <div class="tactic-icon purple">🔄</div>
                                <div class="tactic-name">
                                    <h3>REVIVE</h3>
                                    <div class="tactic-level">Cấp độ Nhóm quảng cáo</div>
                                </div>
                            </div>
                            <p class="tactic-description">
                                Revive tự động kích hoạt lại bất kỳ nhóm quảng cáo nào đã tạm dừng 
                                ngay khi phát hiện bất kỳ hoạt động tích cực nào cho thấy nhóm quảng cáo đã trở nên có lợi nhuận trở lại.
                            </p>
                        </div>
                        
                        <!-- REVIVE Ad Level -->
                        <div class="tactic-card" onclick="selectTactic('revive-ad')">
                            <div class="tactic-header">
                                <div class="tactic-icon rose">🔄</div>
                                <div class="tactic-name">
                                    <h3>REVIVE</h3>
                                    <div class="tactic-level">Cấp độ Quảng cáo</div>
                                </div>
                            </div>
                            <p class="tactic-description">
                                Revive tự động kích hoạt lại bất kỳ quảng cáo nào đã tạm dừng 
                                ngay khi phát hiện bất kỳ hoạt động tích cực nào cho thấy quảng cáo đã trở nên có lợi nhuận trở lại.
                            </p>
                        </div>
                        
                        <!-- SURF Campaign Level -->
                        <div class="tactic-card" onclick="selectTactic('surf-campaign')">
                            <div class="tactic-header">
                                <div class="tactic-icon blue">🌊</div>
                                <div class="tactic-name">
                                    <h3>SURF</h3>
                                    <div class="tactic-level">Cấp độ Chiến dịch</div>
                                </div>
                            </div>
                            <p class="tactic-description">
                                SURF xác định xu hướng hiệu suất mạnh và tự động tận dụng động lực tích cực 
                                bằng cách tăng ngân sách của chiến dịch vượt quá giới hạn ban đầu. 
                                Ngân sách sẽ tự động trở về ngân sách ban đầu vào thời gian địa phương đã chọn.
                            </p>
                        </div>
                    </div>
                </div>
                
                <!-- Strategies Section -->
                <div class="strategies-section">
                    <div class="strategies-header">
                        <h2 class="section-title">Chiến Lược Automation</h2>
                        <div class="strategies-toolbar">
                            <select class="campaign-type-select" id="campaignTypeFilter" onchange="filterStrategies()">
                                <option value="">Tất cả</option>
                                <option value="ECOMMERCE">E-commerce</option>
                                <option value="LEAD_GENERATION">Lead Generation</option>
                                <option value="MOBILE_APP">Mobile App</option>
                            </select>
                            <div class="filter-token" onclick="showFilters()">
                                <span>Bộ lọc</span>
                                <span>▼</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="strategies-grid" id="strategiesGrid">
                        <!-- Create Custom -->
                        <div class="create-custom-card" onclick="createCustomAutomation()">
                            <div class="create-custom-icon">➕</div>
                            <div class="create-custom-title">Tạo Automation Tùy Chỉnh</div>
                        </div>
                        
                        <!-- Strategy Cards -->
                        <div class="strategy-card" onclick="selectStrategy('stop-loss-expensive-ads')">
                            <div class="strategy-title">Stop Loss automation cho quảng cáo đắt tiền không có lượt click</div>
                            <div class="strategy-description">
                                Hệ thống sẽ đảm bảo Facebook không chi tiêu ngân sách nhóm quảng cáo 
                                cho các quảng cáo có hiệu suất thấp bằng cách tắt chúng trong ngày hôm nay.
                            </div>
                            <div class="strategy-actions">
                                <div class="action-icon" title="Bật/Tắt">⚙️</div>
                            </div>
                        </div>
                        
                        <div class="strategy-card" onclick="selectStrategy('pause-losing-ads-today')">
                            <div class="strategy-title">Tạm Dừng Quảng Cáo Thua Lỗ Hôm Nay</div>
                            <div class="strategy-description">
                                Hệ thống sẽ tạm dừng các quảng cáo có hiệu suất thấp hôm nay. 
                                Nó sẽ bật lại lúc 00:00 hoặc sớm hơn nếu kết quả của chúng được cải thiện do độ trễ attribution.
                            </div>
                            <div class="strategy-actions">
                                <div class="action-icon" title="Bật/Tắt">⚙️</div>
                                <div class="action-icon" title="Đã bật">✅</div>
                            </div>
                        </div>
                        
                        <div class="strategy-card" onclick="selectStrategy('pause-losing-ads-permanent')">
                            <div class="strategy-title">Tạm Dừng Quảng Cáo Thua Lỗ Vĩnh Viễn</div>
                            <div class="strategy-description">
                                Hệ thống sẽ tạm dừng các quảng cáo có hiệu suất thấp trong vài ngày qua. 
                                Nó sẽ bật lại nếu kết quả của chúng được cải thiện do độ trễ attribution.
                            </div>
                            <div class="strategy-actions">
                                <div class="action-icon" title="Bật/Tắt">⚙️</div>
                                <div class="action-icon" title="Đã bật">✅</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function selectTactic(tacticId) {{
                console.log('Selected tactic:', tacticId);
                // Chuyển đến trang tạo rule với tactic đã chọn
                window.location.href = `/rules/create?tactic=${{tacticId}}`;
            }}
            
            function selectStrategy(strategyId) {{
                console.log('Selected strategy:', strategyId);
                // Chuyển đến trang tạo rule với strategy đã chọn
                window.location.href = `/rules/create?strategy=${{strategyId}}`;
            }}
            
            function createCustomAutomation() {{
                window.location.href = '/rules/create';
            }}
            
            function filterStrategies() {{
                const campaignType = document.getElementById('campaignTypeFilter').value;
                console.log('Filter by campaign type:', campaignType);
                // TODO: Implement filtering
            }}
            
            function showFilters() {{
                alert('Tính năng bộ lọc đang được phát triển');
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

