# -*- coding: utf-8 -*-
"""
Rules Management UI - Modern Animated Style
Giao diện hiện đại với animations, gradients, glassmorphism và interactive elements
"""
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.logic_rule import LogicRule
from app.models.account_prefix import Account, Prefix
from app.core.config import get_settings
import json

router = APIRouter(prefix="/rules", tags=["rules_ui_birch"])


# Định nghĩa các strategies mặc định
DEFAULT_STRATEGIES = [
    {
        "id": "notify-key-metrics-drops",
        "name": "Notify about Key Metrics Drops",
        "category": "optimise",
        "campaign_type": "BOTH",
        "icon": "bell",
        "icon_color": "#9b59b6",
        "badge": "Easy to start",
        "badge_color": "green",
        "key_metrics": ["Leads drop check", "CPL", "CPM"],
        "benefits": ["Instant alerts", "Prevent budget waste", "Quick response time"],
        "description": "Notify if conversion metrics shift (ROAS, CPP, CPM)",
        "logic_type": "notification"
    },
    {
        "id": "optimize-performance",
        "name": "Optimize Performance",
        "category": "optimise",
        "campaign_type": "BOTH",
        "icon": "optimize",
        "icon_color": "#9b59b6",
        "key_metrics": ["CPL tracking", "Budget reallocation"],
        "benefits": ["Targeted optimization", "Efficient budget use", "Timely performance recovery"],
        "description": "Pause and start based on ad performance",
        "logic_type": "logic2"
    },
    {
        "id": "scale-ad-sets",
        "name": "Scale Ad Sets",
        "category": "scale",
        "campaign_type": "ECOMMERCE",
        "icon": "scale",
        "icon_color": "#f39c12",
        "key_metrics": ["CPL tracking", "Budget reallocation"],
        "benefits": ["Smart budget scaling", "Automatic cutbacks", "Performance-based control"],
        "description": "Gradually increase the budget for high-performing ad sets and decrease the budget for underperformers",
        "logic_type": "scale"
    },
    {
        "id": "logic-1-giai-doan-1",
        "name": "Giai đoạn 1: Tắt khi chi tiêu cao, không có kết quả",
        "category": "pause",
        "campaign_type": "BOTH",
        "icon": "pause",
        "icon_color": "#e74c3c",
        "key_metrics": ["Spend", "Results"],
        "benefits": ["Prevent budget waste", "Quick response", "Automated control"],
        "description": "Tắt adset khi chi tiêu > ngưỡng và kết quả = 0",
        "logic_type": "logic1"
    },
    {
        "id": "logic-2-giai-doan-2",
        "name": "Giai đoạn 2: Tắt khi giá DATA cao",
        "category": "pause",
        "campaign_type": "BOTH",
        "icon": "pause",
        "icon_color": "#e74c3c",
        "key_metrics": ["Spend", "Giá DATA"],
        "benefits": ["Control costs", "Optimize performance", "Data-driven"],
        "description": "Tắt adset khi chi tiêu > ngưỡng và giá DATA > ngưỡng",
        "logic_type": "logic2"
    },
    {
        "id": "logic-3-bat-lai",
        "name": "Bật lại: Resume khi đáp ứng điều kiện",
        "category": "essential",
        "campaign_type": "BOTH",
        "icon": "resume",
        "icon_color": "#27ae60",
        "key_metrics": ["Spend", "Results"],
        "benefits": ["Smart resume", "Late conversions", "Performance recovery"],
        "description": "Bật lại adset khi đáp ứng điều kiện spend và results",
        "logic_type": "logic3"
    },
    {
        "id": "logic-7days-filter",
        "name": "Logic Lọc 7 Ngày",
        "category": "pause",
        "campaign_type": "BOTH",
        "icon": "filter",
        "icon_color": "#3498db",
        "key_metrics": ["7-day spend", "Giá DATA", "Results"],
        "benefits": ["Long-term analysis", "Data-driven decisions", "Cost control"],
        "description": "Lọc adsets trong 7 ngày qua dựa trên chi tiêu, giá DATA và kết quả",
        "logic_type": "logic7days"
    }
]

STRATEGY_CATEGORIES = {
    "essential": "Essential",
    "scale": "Scale",
    "pause": "Pause",
    "time": "Time",
    "optimise": "Optimise"
}


def _render_strategy_cards_html(strategies, show_description=False):
    """Render strategy cards HTML với animations"""
    cards = []
    for idx, strategy in enumerate(strategies):
        icon_emoji = {
            "bell": "🔔",
            "optimize": "⚡",
            "scale": "📈",
            "pause": "⏸️",
            "resume": "▶️",
            "filter": "🔍"
        }.get(strategy.get("icon", ""), "📋")
        
        badge_html = ""
        if strategy.get("badge"):
            badge_html = f'<div class="strategy-badge pulse-animation">{strategy["badge"]}</div>'
        
        key_metrics_html = "".join([
            f'<span class="strategy-tag fade-in" style="animation-delay: {i*0.1}s">{metric}</span>'
            for i, metric in enumerate(strategy.get("key_metrics", []))
        ])
        
        benefits_html = "".join([
            f'<span class="strategy-tag benefit fade-in" style="animation-delay: {i*0.1}s">{benefit}</span>'
            for i, benefit in enumerate(strategy.get("benefits", []))
        ])
        
        icon_color = strategy.get('icon_color', '#9b59b6')
        
        if show_description:
            description = strategy.get("description", "")
            body_content = f'<div class="strategy-description">{description}</div>'
        else:
            body_content = f'''
                <div class="strategy-section">
                    <div class="strategy-section-label">Key metrics</div>
                    <div class="strategy-tags">
                        {key_metrics_html}
                    </div>
                </div>
                <div class="strategy-section">
                    <div class="strategy-section-label">Benefits</div>
                    <div class="strategy-tags">
                        {benefits_html}
                    </div>
                </div>
                '''
        
        card = f"""
        <div class="strategy-card card-hover" onclick="checkStrategy('{strategy["id"]}')" style="animation-delay: {idx*0.1}s">
            <div class="strategy-card-header" style="background: linear-gradient(135deg, {icon_color}20 0%, {icon_color}10 100%);">
                {badge_html}
                <div class="strategy-icon floating-animation" style="background: {icon_color}20; box-shadow: 0 8px 32px {icon_color}40;">
                    {icon_emoji}
                </div>
            </div>
            <div class="strategy-card-body">
                <div class="strategy-card-title">{strategy["name"]}</div>
                {body_content}
            </div>
            <div class="strategy-card-footer">
                <button class="btn-check-strategy" onclick="event.stopPropagation(); checkStrategy('{strategy["id"]}')">
                    <span>Check strategy</span>
                    <span class="arrow">→</span>
                </button>
            </div>
        </div>
        """
        cards.append(card)
    return "".join(cards)


@router.get("/", response_class=HTMLResponse)
async def rules_home_birch_style(db: Session = Depends(get_db)):
    """Trang chủ Rules - Modern Animated Style"""
    accounts = db.query(Account).filter(Account.enabled == True).order_by(Account.account_id).all()
    account_ids = [acc.account_id for acc in accounts] if accounts else []
    
    allowed_prefixes = ['FL', 'NM', 'PX', 'TL']
    prefixes = db.query(Prefix).filter(
        Prefix.enabled == True,
        Prefix.prefix.in_(allowed_prefixes)
    ).order_by(Prefix.prefix).all()
    prefix_list = [p.prefix for p in prefixes] if prefixes else allowed_prefixes
    
    popular_strategies = DEFAULT_STRATEGIES[:3]
    strategy_cards_html = _render_strategy_cards_html(popular_strategies)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Automated Rules - Facebook Ads Automation</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            :root {{
                --primary: #6366f1;
                --primary-dark: #4f46e5;
                --secondary: #8b5cf6;
                --success: #10b981;
                --danger: #ef4444;
                --warning: #f59e0b;
                --info: #3b82f6;
                --dark: #1e293b;
                --light: #f8fafc;
                --gray: #64748b;
                --white: #ffffff;
                --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                --gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
                --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
                color: var(--dark);
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
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                padding: 20px 32px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                position: sticky;
                top: 0;
                z-index: 100;
                box-shadow: var(--shadow-md);
            }}
            
            .header-left {{
                display: flex;
                align-items: center;
                gap: 24px;
            }}
            
            .header h3 {{
                font-size: 24px;
                font-weight: 700;
                background: var(--gradient-1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .platform-selector {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 16px;
                border: 2px solid rgba(99, 102, 241, 0.2);
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.8);
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 500;
            }}
            
            .platform-selector:hover {{
                background: rgba(255, 255, 255, 1);
                border-color: var(--primary);
                transform: translateY(-2px);
                box-shadow: var(--shadow-md);
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 60px 32px;
                position: relative;
                z-index: 1;
            }}
            
            .hero-section {{
                text-align: center;
                margin-bottom: 80px;
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
            
            .hero-section h1 {{
                font-size: 56px;
                font-weight: 800;
                color: var(--white);
                margin-bottom: 20px;
                text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                line-height: 1.2;
            }}
            
            .hero-section p {{
                font-size: 20px;
                color: rgba(255, 255, 255, 0.9);
                max-width: 700px;
                margin: 0 auto;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}
            
            .strategies-section {{
                margin-bottom: 60px;
                animation: fadeInUp 1s ease 0.2s both;
            }}
            
            .strategies-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 40px;
                flex-wrap: wrap;
                gap: 20px;
            }}
            
            .strategies-header h2 {{
                font-size: 36px;
                font-weight: 700;
                color: var(--white);
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            }}
            
            .strategies-actions {{
                display: flex;
                gap: 16px;
                flex-wrap: wrap;
            }}
            
            .btn-link {{
                color: var(--white);
                text-decoration: none;
                font-weight: 600;
                font-size: 16px;
                padding: 12px 0;
                transition: all 0.3s ease;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            }}
            
            .btn-link:hover {{
                transform: translateY(-2px);
                text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            }}
            
            .btn-primary {{
                background: var(--white);
                color: var(--primary);
                border: none;
                border-radius: 12px;
                padding: 14px 28px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 10px;
                transition: all 0.3s ease;
                box-shadow: var(--shadow-lg);
            }}
            
            .btn-primary:hover {{
                transform: translateY(-3px);
                box-shadow: var(--shadow-xl);
                background: var(--light);
            }}
            
            .btn-primary:active {{
                transform: translateY(-1px);
            }}
            
            .strategies-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
                gap: 32px;
            }}
            
            .strategy-card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 24px;
                overflow: hidden;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                box-shadow: var(--shadow-xl);
                animation: fadeInUp 0.6s ease both;
            }}
            
            .card-hover:hover {{
                transform: translateY(-12px) scale(1.02);
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            }}
            
            .strategy-card-header {{
                height: 160px;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }}
            
            .strategy-card-header::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
                animation: rotate 20s linear infinite;
            }}
            
            @keyframes rotate {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(360deg); }}
            }}
            
            .strategy-icon {{
                width: 80px;
                height: 80px;
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 40px;
                position: relative;
                z-index: 2;
                transition: all 0.3s ease;
            }}
            
            .floating-animation {{
                animation: float 3s ease-in-out infinite;
            }}
            
            @keyframes float {{
                0%, 100% {{ transform: translateY(0px); }}
                50% {{ transform: translateY(-10px); }}
            }}
            
            .strategy-badge {{
                position: absolute;
                top: 16px;
                left: 16px;
                background: var(--success);
                color: var(--white);
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                z-index: 3;
                box-shadow: var(--shadow-md);
            }}
            
            .pulse-animation {{
                animation: pulse 2s ease-in-out infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
            }}
            
            .strategy-card-body {{
                padding: 28px;
            }}
            
            .strategy-card-title {{
                font-size: 20px;
                font-weight: 700;
                color: var(--dark);
                margin-bottom: 20px;
                line-height: 1.4;
            }}
            
            .strategy-section {{
                margin-bottom: 20px;
            }}
            
            .strategy-section-label {{
                font-size: 12px;
                font-weight: 700;
                color: var(--gray);
                margin-bottom: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .strategy-tags {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }}
            
            .strategy-tag {{
                background: var(--light);
                color: var(--gray);
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 500;
                transition: all 0.3s ease;
            }}
            
            .strategy-tag:hover {{
                transform: scale(1.05);
                box-shadow: var(--shadow-sm);
            }}
            
            .strategy-tag.benefit {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: var(--white);
            }}
            
            .fade-in {{
                animation: fadeIn 0.5s ease both;
            }}
            
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                    transform: translateY(10px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .strategy-card-footer {{
                padding: 20px 28px;
                border-top: 1px solid rgba(0, 0, 0, 0.05);
                background: rgba(248, 250, 252, 0.5);
            }}
            
            .btn-check-strategy {{
                width: 100%;
                background: var(--white);
                border: 2px solid var(--primary);
                border-radius: 12px;
                padding: 14px 20px;
                font-size: 15px;
                font-weight: 600;
                color: var(--primary);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                transition: all 0.3s ease;
            }}
            
            .btn-check-strategy:hover {{
                background: var(--primary);
                color: var(--white);
                transform: translateY(-2px);
                box-shadow: var(--shadow-md);
            }}
            
            .btn-check-strategy .arrow {{
                transition: transform 0.3s ease;
            }}
            
            .btn-check-strategy:hover .arrow {{
                transform: translateX(4px);
            }}
            
            .run-automation-section {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-radius: 24px;
                padding: 40px;
                margin-top: 60px;
                box-shadow: var(--shadow-xl);
                animation: fadeInUp 1.2s ease 0.4s both;
            }}
            
            .run-automation-section h3 {{
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 16px;
                background: var(--gradient-1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .run-automation-section p {{
                color: var(--gray);
                margin-bottom: 24px;
                font-size: 16px;
            }}
            
            .run-buttons {{
                display: flex;
                gap: 16px;
                flex-wrap: wrap;
            }}
            
            .btn-run {{
                background: var(--gradient-1);
                color: var(--white);
                border: none;
                border-radius: 12px;
                padding: 16px 32px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: var(--shadow-lg);
                position: relative;
                overflow: hidden;
            }}
            
            .btn-run::before {{
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transform: translate(-50%, -50%);
                transition: width 0.6s, height 0.6s;
            }}
            
            .btn-run:hover::before {{
                width: 300px;
                height: 300px;
            }}
            
            .btn-run:hover {{
                transform: translateY(-3px);
                box-shadow: var(--shadow-xl);
            }}
            
            .btn-run:active {{
                transform: translateY(-1px);
            }}
            
            .btn-run-secondary {{
                background: var(--white);
                color: var(--primary);
                border: 2px solid var(--primary);
            }}
            
            .btn-run-secondary:hover {{
                background: var(--primary);
                color: var(--white);
            }}
            
            .log-container {{
                background: var(--dark);
                color: #d4d4d4;
                padding: 24px;
                border-radius: 16px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                max-height: 500px;
                overflow-y: auto;
                margin-top: 24px;
                box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.3);
            }}
            
            .log-entry {{
                margin-bottom: 8px;
                padding: 4px 0;
                animation: slideIn 0.3s ease;
            }}
            
            @keyframes slideIn {{
                from {{
                    opacity: 0;
                    transform: translateX(-10px);
                }}
                to {{
                    opacity: 1;
                    transform: translateX(0);
                }}
            }}
            
            .log-entry.info {{ color: #d4d4d4; }}
            .log-entry.success {{ color: #10b981; }}
            .log-entry.error {{ color: #ef4444; }}
            .log-entry.warning {{ color: #f59e0b; }}
            
            /* Toast Notification */
            .toast-container {{
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }}
            
            .toast {{
                background: var(--white);
                color: var(--dark);
                padding: 16px 24px;
                border-radius: 12px;
                box-shadow: var(--shadow-xl);
                display: flex;
                align-items: center;
                gap: 12px;
                min-width: 300px;
                animation: slideInRight 0.3s ease;
                border-left: 4px solid var(--primary);
            }}
            
            @keyframes slideInRight {{
                from {{
                    opacity: 0;
                    transform: translateX(100%);
                }}
                to {{
                    opacity: 1;
                    transform: translateX(0);
                }}
            }}
            
            .toast.success {{ border-left-color: var(--success); }}
            .toast.error {{ border-left-color: var(--danger); }}
            .toast.warning {{ border-left-color: var(--warning); }}
            .toast.info {{ border-left-color: var(--info); }}
            
            /* Loading Spinner */
            .spinner {{
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-top: 3px solid var(--white);
                border-radius: 50%;
                width: 20px;
                height: 20px;
                animation: spin 1s linear infinite;
                display: inline-block;
                margin-right: 8px;
            }}
            
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            /* Responsive */
            @media (max-width: 768px) {{
                .hero-section h1 {{
                    font-size: 36px;
                }}
                
                .strategies-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .container {{
                    padding: 40px 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="toast-container" id="toast-container"></div>
        
        <div class="header">
            <div class="header-left">
                <h3>🚀 Automated Rules</h3>
                <div class="platform-selector">
                    <span>📘</span>
                    <span>Meta Ads</span>
                    <span>▼</span>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="hero-section">
                <h1>Let's begin optimizing your ads</h1>
                <p>Automated rules help you save time by continuously tracking campaign performance and taking action for you.</p>
            </div>
            
            <div class="strategies-section">
                <div class="strategies-header">
                    <h2>Use popular strategies</h2>
                    <div class="strategies-actions">
                        <a href="/rules/all" class="btn-link">Show all strategies →</a>
                        <button class="btn-primary" onclick="createRule()">
                            <span>+</span>
                            <span>Create rule</span>
                        </button>
                    </div>
                </div>
                
                <div class="strategies-grid" id="strategies-grid">
                    {strategy_cards_html}
                </div>
            </div>
            
            <div class="run-automation-section">
                <h3>▶️ Chạy Automation</h3>
                <p>Chạy automation trực tiếp từ website. Logs sẽ hiển thị real-time bên dưới.</p>
                
                <div class="run-buttons">
                    <button class="btn-run" onclick="runAutomation()" id="run-btn">
                        <span>▶️ Chạy Automation</span>
                    </button>
                    <button class="btn-run btn-run-secondary" onclick="runTestAutomation()" id="test-run-btn">
                        <span>🧪 Test (Bỏ qua khung giờ)</span>
                    </button>
                    <button class="btn-run btn-run-secondary" onclick="run7DaysFilter()" id="7days-run-btn">
                        <span>🔍 Chạy Logic 7 Ngày</span>
                    </button>
                </div>
                
                <div class="log-container" id="log-container">
                    <div class="log-entry info">Chờ lệnh chạy...</div>
                </div>
            </div>
        </div>
        
        <script>
            const accountIds = {json.dumps(account_ids)};
            const prefixes = {json.dumps(prefix_list)};
            
            // Toast notification system
            function showToast(message, type = 'info') {{
                const container = document.getElementById('toast-container');
                const toast = document.createElement('div');
                toast.className = `toast ${{type}}`;
                
                const icons = {{
                    success: '✅',
                    error: '❌',
                    warning: '⚠️',
                    info: 'ℹ️'
                }};
                
                toast.innerHTML = `
                    <span style="font-size: 20px;">${{icons[type] || icons.info}}</span>
                    <span style="flex: 1;">${{message}}</span>
                `;
                
                container.appendChild(toast);
                
                setTimeout(() => {{
                    toast.style.animation = 'slideInRight 0.3s ease reverse';
                    setTimeout(() => toast.remove(), 300);
                }}, 3000);
            }}
            
            // Run automation functions
            function addLog(message, type = 'info') {{
                const container = document.getElementById('log-container');
                const timestamp = new Date().toLocaleTimeString('vi-VN');
                const logEntry = document.createElement('div');
                logEntry.className = `log-entry ${{type}}`;
                logEntry.innerHTML = `[${{timestamp}}] ${{message}}`;
                container.appendChild(logEntry);
                container.scrollTop = container.scrollHeight;
            }}
            
            async function runAutomation() {{
                const btn = document.getElementById('run-btn');
                const testBtn = document.getElementById('test-run-btn');
                const daysBtn = document.getElementById('7days-run-btn');
                const logContainer = document.getElementById('log-container');
                
                btn.disabled = true;
                testBtn.disabled = true;
                daysBtn.disabled = true;
                btn.innerHTML = '<span class="spinner"></span> Đang chạy...';
                logContainer.innerHTML = '';
                addLog('🚀 Bắt đầu chạy automation...', 'info');
                showToast('Đang chạy automation...', 'info');
                
                try {{
                    const response = await fetch('/api/automation/run-web', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                    
                    if (!response.ok) {{
                        const error = await response.json();
                        addLog('❌ Lỗi: ' + (error.error || 'Unknown error'), 'error');
                        showToast('Lỗi: ' + (error.error || 'Unknown error'), 'error');
                        return;
                    }}
                    
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    
                    while (true) {{
                        const {{ done, value }} = await reader.read();
                        if (done) break;
                        
                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\\n').filter(l => l.trim());
                        
                        for (const line of lines) {{
                            try {{
                                const data = JSON.parse(line);
                                if (data.type === 'log') {{
                                    addLog(data.message, data.level || 'info');
                                }} else if (data.type === 'complete') {{
                                    addLog('✅ Hoàn thành!', 'success');
                                    showToast('Automation hoàn thành thành công!', 'success');
                                }} else if (data.type === 'error') {{
                                    addLog('❌ Lỗi: ' + data.message, 'error');
                                    showToast('Lỗi: ' + data.message, 'error');
                                }}
                            }} catch (e) {{
                                if (line.trim()) {{
                                    addLog(line, 'info');
                                }}
                            }}
                        }}
                    }}
                }} catch (error) {{
                    addLog('❌ Lỗi kết nối: ' + error.message, 'error');
                    showToast('Lỗi kết nối: ' + error.message, 'error');
                }} finally {{
                    btn.disabled = false;
                    testBtn.disabled = false;
                    daysBtn.disabled = false;
                    btn.innerHTML = '<span>▶️ Chạy Automation</span>';
                }}
            }}
            
            async function runTestAutomation() {{
                const btn = document.getElementById('run-btn');
                const testBtn = document.getElementById('test-run-btn');
                const daysBtn = document.getElementById('7days-run-btn');
                const logContainer = document.getElementById('log-container');
                
                btn.disabled = true;
                testBtn.disabled = true;
                daysBtn.disabled = true;
                testBtn.innerHTML = '<span class="spinner"></span> Đang chạy...';
                logContainer.innerHTML = '';
                addLog('🧪 Bắt đầu chạy test automation (bỏ qua khung giờ)...', 'info');
                showToast('Đang chạy test automation...', 'info');
                
                try {{
                    const response = await fetch('/api/automation/test-web', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                    
                    if (!response.ok) {{
                        const error = await response.json();
                        addLog('❌ Lỗi: ' + (error.error || 'Unknown error'), 'error');
                        showToast('Lỗi: ' + (error.error || 'Unknown error'), 'error');
                        return;
                    }}
                    
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    
                    while (true) {{
                        const {{ done, value }} = await reader.read();
                        if (done) break;
                        
                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\\n').filter(l => l.trim());
                        
                        for (const line of lines) {{
                            try {{
                                const data = JSON.parse(line);
                                if (data.type === 'log') {{
                                    addLog(data.message, data.level || 'info');
                                }} else if (data.type === 'complete') {{
                                    addLog('✅ Hoàn thành!', 'success');
                                    showToast('Test automation hoàn thành!', 'success');
                                }} else if (data.type === 'error') {{
                                    addLog('❌ Lỗi: ' + data.message, 'error');
                                    showToast('Lỗi: ' + data.message, 'error');
                                }}
                            }} catch (e) {{
                                if (line.trim()) {{
                                    addLog(line, 'info');
                                }}
                            }}
                        }}
                    }}
                }} catch (error) {{
                    addLog('❌ Lỗi kết nối: ' + error.message, 'error');
                    showToast('Lỗi kết nối: ' + error.message, 'error');
                }} finally {{
                    btn.disabled = false;
                    testBtn.disabled = false;
                    daysBtn.disabled = false;
                    testBtn.innerHTML = '<span>🧪 Test (Bỏ qua khung giờ)</span>';
                }}
            }}
            
            async function run7DaysFilter() {{
                const btn = document.getElementById('run-btn');
                const testBtn = document.getElementById('test-run-btn');
                const daysBtn = document.getElementById('7days-run-btn');
                const logContainer = document.getElementById('log-container');
                
                btn.disabled = true;
                testBtn.disabled = true;
                daysBtn.disabled = true;
                daysBtn.innerHTML = '<span class="spinner"></span> Đang chạy...';
                logContainer.innerHTML = '';
                addLog('🔍 Bắt đầu chạy logic lọc 7 ngày...', 'info');
                showToast('Đang chạy logic lọc 7 ngày...', 'info');
                
                try {{
                    const response = await fetch('/api/automation/run-7days-web', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                    
                    if (!response.ok) {{
                        const error = await response.json();
                        addLog('❌ Lỗi: ' + (error.error || 'Unknown error'), 'error');
                        showToast('Lỗi: ' + (error.error || 'Unknown error'), 'error');
                        return;
                    }}
                    
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    
                    while (true) {{
                        const {{ done, value }} = await reader.read();
                        if (done) break;
                        
                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\\n').filter(l => l.trim());
                        
                        for (const line of lines) {{
                            try {{
                                const data = JSON.parse(line);
                                if (data.type === 'log') {{
                                    addLog(data.message, data.level || 'info');
                                }} else if (data.type === 'complete') {{
                                    addLog('✅ Hoàn thành!', 'success');
                                    showToast('Logic 7 ngày hoàn thành!', 'success');
                                }} else if (data.type === 'error') {{
                                    addLog('❌ Lỗi: ' + data.message, 'error');
                                    showToast('Lỗi: ' + data.message, 'error');
                                }}
                            }} catch (e) {{
                                if (line.trim()) {{
                                    addLog(line, 'info');
                                }}
                            }}
                        }}
                    }}
                }} catch (error) {{
                    addLog('❌ Lỗi kết nối: ' + error.message, 'error');
                    showToast('Lỗi kết nối: ' + error.message, 'error');
                }} finally {{
                    btn.disabled = false;
                    testBtn.disabled = false;
                    daysBtn.disabled = false;
                    daysBtn.innerHTML = '<span>🔍 Chạy Logic 7 Ngày</span>';
                }}
            }}
            
            function createRule() {{
                window.location.href = '/rules/create';
            }}
            
            function checkStrategy(strategyId) {{
                window.location.href = `/rules/strategy/${{strategyId}}`;
            }}
            
            // Smooth scroll on page load
            window.addEventListener('load', () => {{
                window.scrollTo({{ top: 0, behavior: 'smooth' }});
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
