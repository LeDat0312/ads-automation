# -*- coding: utf-8 -*-
"""
Rules Management UI - Birch/Madgicx Style
Giao diện mới theo style Birch/Madgicx với strategy cards và visual builder
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


# Định nghĩa các strategies mặc định (tương tự Birch)
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
    """Render strategy cards HTML"""
    cards = []
    for strategy in strategies:
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
            badge_html = f'<div class="strategy-badge">{strategy["badge"]}</div>'
        
        key_metrics_html = "".join([
            f'<span class="strategy-tag">{metric}</span>'
            for metric in strategy.get("key_metrics", [])
        ])
        
        benefits_html = "".join([
            f'<span class="strategy-tag benefit">{benefit}</span>'
            for benefit in strategy.get("benefits", [])
        ])
        
        icon_color = strategy.get('icon_color', '#9b59b6')
        
        # Build body content based on show_description
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
        <div class="strategy-card" onclick="checkStrategy('{strategy["id"]}')">
            <div class="strategy-card-header" style="background: {icon_color}20;">
                {badge_html}
                <div class="strategy-icon" style="background: {icon_color}20;">
                    {icon_emoji}
                </div>
            </div>
            <div class="strategy-card-body">
                <div class="strategy-card-title">{strategy["name"]}</div>
                {body_content}
            </div>
            <div class="strategy-card-footer">
                <button class="btn-check-strategy" onclick="event.stopPropagation(); checkStrategy('{strategy["id"]}')">
                    Check strategy
                </button>
            </div>
        </div>
        """
        cards.append(card)
    return "".join(cards)


@router.get("/", response_class=HTMLResponse)
async def rules_home_birch_style(db: Session = Depends(get_db)):
    """Trang chủ Rules - Style Birch/Madgicx"""
    # Lấy accounts và prefixes
    accounts = db.query(Account).filter(Account.enabled == True).order_by(Account.account_id).all()
    account_ids = [acc.account_id for acc in accounts] if accounts else []
    
    allowed_prefixes = ['FL', 'NM', 'PX', 'TL']
    prefixes = db.query(Prefix).filter(
        Prefix.enabled == True,
        Prefix.prefix.in_(allowed_prefixes)
    ).order_by(Prefix.prefix).all()
    prefix_list = [p.prefix for p in prefixes] if prefixes else allowed_prefixes
    
    # Lấy 3 strategies phổ biến để hiển thị trên trang chủ
    popular_strategies = DEFAULT_STRATEGIES[:3]
    
    # Render strategy cards HTML
    strategy_cards_html = _render_strategy_cards_html(popular_strategies)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Automated Rules - Facebook Ads Automation</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: #ffffff;
                color: #1c1e21;
                line-height: 1.5;
            }}
            .header {{
                background: #ffffff;
                border-bottom: 1px solid #dadde1;
                padding: 16px 24px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            .header-left {{
                display: flex;
                align-items: center;
                gap: 16px;
            }}
            .header h3 {{
                font-size: 20px;
                font-weight: 600;
                color: #1c1e21;
            }}
            .platform-selector {{
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                border: 1px solid #dadde1;
                border-radius: 6px;
                background: #ffffff;
                cursor: pointer;
            }}
            .platform-selector:hover {{
                background: #f2f3f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 24px;
            }}
            .hero-section {{
                text-align: center;
                margin-bottom: 48px;
            }}
            .hero-section h1 {{
                font-size: 32px;
                font-weight: 700;
                color: #1c1e21;
                margin-bottom: 12px;
            }}
            .hero-section p {{
                font-size: 16px;
                color: #65676b;
                max-width: 600px;
                margin: 0 auto;
            }}
            .strategies-section {{
                margin-bottom: 40px;
            }}
            .strategies-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 24px;
            }}
            .strategies-header h2 {{
                font-size: 24px;
                font-weight: 600;
                color: #1c1e21;
            }}
            .strategies-actions {{
                display: flex;
                gap: 12px;
            }}
            .btn-link {{
                color: #1877f2;
                text-decoration: none;
                font-weight: 500;
                font-size: 15px;
                padding: 8px 0;
            }}
            .btn-link:hover {{
                text-decoration: underline;
            }}
            .btn-primary {{
                background: #1877f2;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 15px;
                font-weight: 500;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .btn-primary:hover {{
                background: #166fe5;
            }}
            .strategies-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                gap: 24px;
            }}
            .strategy-card {{
                background: #ffffff;
                border: 1px solid #dadde1;
                border-radius: 8px;
                overflow: hidden;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .strategy-card:hover {{
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }}
            .strategy-card-header {{
                height: 120px;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .strategy-card-header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(135deg, rgba(155, 89, 182, 0.1) 0%, rgba(155, 89, 182, 0.05) 100%);
            }}
            .strategy-icon {{
                width: 64px;
                height: 64px;
                background: rgba(155, 89, 182, 0.1);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 32px;
                position: relative;
                z-index: 1;
            }}
            .strategy-badge {{
                position: absolute;
                top: 12px;
                left: 12px;
                background: #27ae60;
                color: #ffffff;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                z-index: 2;
            }}
            .strategy-card-body {{
                padding: 20px;
            }}
            .strategy-card-title {{
                font-size: 18px;
                font-weight: 600;
                color: #1c1e21;
                margin-bottom: 16px;
            }}
            .strategy-section {{
                margin-bottom: 16px;
            }}
            .strategy-section-label {{
                font-size: 13px;
                font-weight: 600;
                color: #65676b;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .strategy-tags {{
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
            }}
            .strategy-tag {{
                background: #f2f3f5;
                color: #65676b;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 13px;
            }}
            .strategy-tag.benefit {{
                background: #e8f5e9;
                color: #2e7d32;
            }}
            .strategy-card-footer {{
                padding: 16px 20px;
                border-top: 1px solid #dadde1;
            }}
            .btn-check-strategy {{
                width: 100%;
                background: #ffffff;
                border: 1px solid #dadde1;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 15px;
                font-weight: 500;
                color: #1c1e21;
                cursor: pointer;
            }}
            .btn-check-strategy:hover {{
                background: #f2f3f5;
            }}
            .run-automation-section {{
                background: #f2f3f5;
                border-radius: 8px;
                padding: 24px;
                margin-top: 40px;
            }}
            .run-automation-section h3 {{
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 16px;
            }}
            .run-buttons {{
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
            }}
            .btn-run {{
                background: #1877f2;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 15px;
                font-weight: 500;
                cursor: pointer;
            }}
            .btn-run:hover {{
                background: #166fe5;
            }}
            .btn-run-secondary {{
                background: #ffffff;
                color: #1877f2;
                border: 1px solid #1877f2;
            }}
            .btn-run-secondary:hover {{
                background: #f0f2f5;
            }}
            .log-container {{
                background: #1e1e1e;
                color: #d4d4d4;
                padding: 20px;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                max-height: 400px;
                overflow-y: auto;
                margin-top: 16px;
            }}
            .log-entry {{
                margin-bottom: 4px;
            }}
            .log-entry.info {{ color: #d4d4d4; }}
            .log-entry.success {{ color: #4ec9b0; }}
            .log-entry.error {{ color: #f48771; }}
            .log-entry.warning {{ color: #dcdcaa; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-left">
                <h3>Automated Rules</h3>
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
                        <a href="/rules/all" class="btn-link">Show all strategies</a>
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
                <p style="color: #65676b; margin-bottom: 16px;">Chạy automation trực tiếp từ website. Logs sẽ hiển thị real-time bên dưới.</p>
                
                <div class="run-buttons">
                    <button class="btn-run" onclick="runAutomation()" id="run-btn">▶️ Chạy Automation</button>
                    <button class="btn-run btn-run-secondary" onclick="runTestAutomation()" id="test-run-btn">🧪 Test (Bỏ qua khung giờ)</button>
                    <button class="btn-run btn-run-secondary" onclick="run7DaysFilter()" id="7days-run-btn">🔍 Chạy Logic 7 Ngày</button>
                </div>
                
                <div class="log-container" id="log-container">
                    <div class="log-entry info">Chờ lệnh chạy...</div>
                </div>
            </div>
        </div>
        
        <script>
            const accountIds = {json.dumps(account_ids)};
            const prefixes = {json.dumps(prefix_list)};
            
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
                logContainer.innerHTML = '';
                addLog('🚀 Bắt đầu chạy automation...', 'info');
                
                try {{
                    const response = await fetch('/api/automation/run-web', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                    
                    if (!response.ok) {{
                        const error = await response.json();
                        addLog('❌ Lỗi: ' + (error.error || 'Unknown error'), 'error');
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
                                    addLog('Kết quả: ' + JSON.stringify(data.result, null, 2), 'info');
                                }} else if (data.type === 'error') {{
                                    addLog('❌ Lỗi: ' + data.message, 'error');
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
                }} finally {{
                    btn.disabled = false;
                    testBtn.disabled = false;
                    daysBtn.disabled = false;
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
                logContainer.innerHTML = '';
                addLog('🧪 Bắt đầu chạy test automation (bỏ qua khung giờ)...', 'info');
                
                try {{
                    const response = await fetch('/api/automation/test-web', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                    
                    if (!response.ok) {{
                        const error = await response.json();
                        addLog('❌ Lỗi: ' + (error.error || 'Unknown error'), 'error');
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
                                    addLog('Kết quả: ' + JSON.stringify(data.result, null, 2), 'info');
                                }} else if (data.type === 'error') {{
                                    addLog('❌ Lỗi: ' + data.message, 'error');
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
                }} finally {{
                    btn.disabled = false;
                    testBtn.disabled = false;
                    daysBtn.disabled = false;
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
                logContainer.innerHTML = '';
                addLog('🔍 Bắt đầu chạy logic lọc 7 ngày...', 'info');
                
                try {{
                    const response = await fetch('/api/automation/run-7days-web', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                    
                    if (!response.ok) {{
                        const error = await response.json();
                        addLog('❌ Lỗi: ' + (error.error || 'Unknown error'), 'error');
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
                                    addLog('Kết quả: ' + JSON.stringify(data.result, null, 2), 'info');
                                }} else if (data.type === 'error') {{
                                    addLog('❌ Lỗi: ' + data.message, 'error');
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
                }} finally {{
                    btn.disabled = false;
                    testBtn.disabled = false;
                    daysBtn.disabled = false;
                }}
            }}
            
            function createRule() {{
                window.location.href = '/rules/create';
            }}
            
            function checkStrategy(strategyId) {{
                window.location.href = `/rules/strategy/${{strategyId}}`;
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/all", response_class=HTMLResponse)
async def show_all_strategies(db: Session = Depends(get_db)):
    """Trang "Show all strategies" - Style Birch/Madgicx"""
    # Group strategies by category
    strategies_by_category = {}
    for strategy in DEFAULT_STRATEGIES:
        category = strategy.get("category", "essential")
        if category not in strategies_by_category:
            strategies_by_category[category] = []
        strategies_by_category[category].append(strategy)
    
    # Render categories HTML
    categories_html = ""
    for category_key, category_name in STRATEGY_CATEGORIES.items():
        strategies = strategies_by_category.get(category_key, [])
        if not strategies:
            continue
        
        strategies_html = _render_strategy_cards_html(strategies, show_description=True)
        
        categories_html += f"""
        <div class="category-section">
            <h2 class="category-title">{category_name}</h2>
            <div class="strategies-grid">
                {strategies_html}
            </div>
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>All Strategies - Facebook Ads Automation</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: #ffffff;
                color: #1c1e21;
                line-height: 1.5;
            }}
            .header {{
                background: #ffffff;
                border-bottom: 1px solid #dadde1;
                padding: 16px 24px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            .header-left {{
                display: flex;
                align-items: center;
                gap: 16px;
            }}
            .header h2 {{
                font-size: 24px;
                font-weight: 600;
                color: #1c1e21;
            }}
            .platform-selector {{
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                border: 1px solid #dadde1;
                border-radius: 6px;
                background: #ffffff;
                cursor: pointer;
            }}
            .platform-selector:hover {{
                background: #f2f3f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 24px;
            }}
            .page-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 32px;
            }}
            .page-header h1 {{
                font-size: 32px;
                font-weight: 700;
                color: #1c1e21;
            }}
            .btn-my-strategies {{
                background: #ffffff;
                border: 1px solid #dadde1;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 15px;
                font-weight: 500;
                color: #1c1e21;
                cursor: pointer;
            }}
            .btn-my-strategies:hover {{
                background: #f2f3f5;
            }}
            .filter-tabs {{
                display: flex;
                gap: 8px;
                margin-bottom: 32px;
                border-bottom: 1px solid #dadde1;
            }}
            .filter-tab {{
                padding: 12px 20px;
                background: transparent;
                border: none;
                border-bottom: 2px solid transparent;
                font-size: 15px;
                font-weight: 500;
                color: #65676b;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .filter-tab:hover {{
                color: #1c1e21;
                background: #f2f3f5;
            }}
            .filter-tab.active {{
                color: #1877f2;
                border-bottom-color: #1877f2;
            }}
            .category-section {{
                margin-bottom: 48px;
            }}
            .category-title {{
                font-size: 20px;
                font-weight: 600;
                color: #1c1e21;
                margin-bottom: 24px;
            }}
            .strategies-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                gap: 24px;
            }}
            .strategy-card {{
                background: #ffffff;
                border: 1px solid #dadde1;
                border-radius: 8px;
                overflow: hidden;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .strategy-card:hover {{
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }}
            .strategy-card-header {{
                height: 120px;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .strategy-icon {{
                width: 64px;
                height: 64px;
                background: rgba(155, 89, 182, 0.1);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 32px;
                position: relative;
                z-index: 1;
            }}
            .strategy-badge {{
                position: absolute;
                top: 12px;
                left: 12px;
                background: #27ae60;
                color: #ffffff;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                z-index: 2;
            }}
            .strategy-card-body {{
                padding: 20px;
            }}
            .strategy-card-title {{
                font-size: 18px;
                font-weight: 600;
                color: #1c1e21;
                margin-bottom: 12px;
            }}
            .strategy-description {{
                font-size: 14px;
                color: #65676b;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-left">
                <h2>Strategies</h2>
                <div class="platform-selector">
                    <span>📘</span>
                    <span>Meta Ads</span>
                    <span>▼</span>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="page-header">
                <h1>Strategies</h1>
                <button class="btn-my-strategies" onclick="showMyStrategies()">My strategies</button>
            </div>
            
            <div class="filter-tabs">
                <button class="filter-tab active" onclick="filterByType('all')">All</button>
                <button class="filter-tab" onclick="filterByType('ecommerce')">🛒 E-commerce</button>
                <button class="filter-tab" onclick="filterByType('lead')">📞 Lead Generation</button>
                <button class="filter-tab" onclick="filterByType('mobile')">📱 Mobile App</button>
            </div>
            
            {categories_html}
        </div>
        
        <script>
            function filterByType(type) {{
                // Update active tab
                document.querySelectorAll('.filter-tab').forEach(tab => {{
                    tab.classList.remove('active');
                }});
                event.target.classList.add('active');
                
                // Filter strategies (simplified - in production would filter by campaign_type)
                console.log('Filter by:', type);
            }}
            
            function showMyStrategies() {{
                alert('My strategies feature coming soon!');
            }}
            
            function checkStrategy(strategyId) {{
                window.location.href = `/rules/strategy/${{strategyId}}`;
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/strategy/{strategy_id}", response_class=HTMLResponse)
async def strategy_detail(strategy_id: str, db: Session = Depends(get_db)):
    """Trang chi tiết strategy - Style Birch/Madgicx với form builder"""
    # Tìm strategy trong DEFAULT_STRATEGIES
    strategy = None
    for s in DEFAULT_STRATEGIES:
        if s["id"] == strategy_id:
            strategy = s
            break
    
    if not strategy:
        return HTMLResponse(content="<h1>Strategy not found</h1>", status_code=404)
    
    # Lấy accounts và prefixes
    accounts = db.query(Account).filter(Account.enabled == True).order_by(Account.account_id).all()
    account_list = [{"id": acc.account_id, "name": acc.account_name or acc.account_id} for acc in accounts]
    
    allowed_prefixes = ['FL', 'NM', 'PX', 'TL']
    prefixes = db.query(Prefix).filter(
        Prefix.enabled == True,
        Prefix.prefix.in_(allowed_prefixes)
    ).order_by(Prefix.prefix).all()
    prefix_list = [p.prefix for p in prefixes] if prefixes else allowed_prefixes
    
    # Available metrics based on campaign type
    ecommerce_metrics = ["spend", "purchases", "purchase_roas", "cost_per_purchase", "revenue", "cpm", "ctr"]
    lead_metrics = ["spend", "leads", "cost_per_lead", "cpl", "cpm", "ctr", "results"]
    all_metrics = list(set(ecommerce_metrics + lead_metrics))
    
    # Build strategy image emoji
    icon_emoji_map = {
        "bell": "🔔",
        "optimize": "⚡",
        "scale": "📈",
        "pause": "⏸️",
        "resume": "▶️",
        "filter": "🔍"
    }
    strategy_icon = icon_emoji_map.get(strategy.get("icon", ""), "📋")
    
    # Build badges HTML
    badges_html = f'<span class="strategy-badge">Meta Ads</span><span class="strategy-badge">{strategy.get("campaign_type", "BOTH")}</span>'
    if strategy.get("logic_type"):
        badges_html += f'<span class="strategy-badge">{strategy.get("logic_type")}</span>'
    
    # Build account options
    account_options = '<option value="">All accounts</option>'
    for acc in account_list:
        account_options += f'<option value="{acc["id"]}">{acc["name"]}</option>'
    
    # Build prefix options
    prefix_options = '<option value="">All prefixes</option>'
    for p in prefix_list:
        prefix_options += f'<option value="{p}">{p}</option>'
    
    # Build metric options
    metric_options = '<option value="">Select metric</option>'
    for m in all_metrics:
        metric_options += f'<option value="{m}">{m}</option>'
    
    # Build timeframe options
    timeframes = ["today", "yesterday", "last_3days", "last_7days", "last_14days", "last_30days"]
    timeframe_options = '<option value="">Select period</option>'
    for t in timeframes:
        display_name = t.replace('_', ' ').title()
        timeframe_options += f'<option value="{t}">{display_name}</option>'
    
    # Build operator options for JavaScript
    operators = [" > ", " < ", " >= ", " <= ", " == ", " != "]
    operator_options_js = ""
    for op in operators:
        op_trimmed = op.strip()
        operator_options_js += f'<option value="{op_trimmed}">{op}</option>'
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{strategy["name"]} - Facebook Ads Automation</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: #ffffff;
                color: #1c1e21;
                line-height: 1.5;
            }}
            .header {{
                background: #ffffff;
                border-bottom: 1px solid #dadde1;
                padding: 16px 24px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            .header-left {{
                display: flex;
                align-items: center;
                gap: 16px;
            }}
            .header h2 {{
                font-size: 24px;
                font-weight: 600;
                color: #1c1e21;
            }}
            .btn-share {{
                background: #ffffff;
                border: 1px solid #dadde1;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 15px;
                font-weight: 500;
                color: #1c1e21;
                cursor: pointer;
            }}
            .btn-share:hover {{
                background: #f2f3f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 24px;
            }}
            .strategy-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 32px;
            }}
            .strategy-info {{
                flex: 1;
            }}
            .strategy-info h1 {{
                font-size: 32px;
                font-weight: 700;
                color: #1c1e21;
                margin-bottom: 16px;
            }}
            .strategy-badges {{
                display: flex;
                gap: 8px;
                margin-bottom: 16px;
            }}
            .strategy-badge {{
                background: #f2f3f5;
                color: #65676b;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 500;
            }}
            .strategy-description {{
                font-size: 16px;
                color: #65676b;
                line-height: 1.6;
                margin-bottom: 24px;
            }}
            .strategy-image {{
                width: 200px;
                height: 200px;
                background: {strategy.get('icon_color', '#9b59b6')}20;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 80px;
            }}
            .btn-create-rules {{
                background: #1877f2;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                margin-top: 16px;
            }}
            .btn-create-rules:hover {{
                background: #166fe5;
            }}
            .form-builder {{
                background: #ffffff;
                border: 1px solid #dadde1;
                border-radius: 8px;
                padding: 24px;
                margin-top: 32px;
            }}
            .form-builder h3 {{
                font-size: 20px;
                font-weight: 600;
                color: #1c1e21;
                margin-bottom: 24px;
            }}
            .form-group {{
                margin-bottom: 24px;
            }}
            .form-group label {{
                display: block;
                font-size: 14px;
                font-weight: 600;
                color: #1c1e21;
                margin-bottom: 8px;
            }}
            .form-group input,
            .form-group select {{
                width: 100%;
                padding: 10px 12px;
                border: 1px solid #dadde1;
                border-radius: 6px;
                font-size: 15px;
                color: #1c1e21;
            }}
            .form-group input:focus,
            .form-group select:focus {{
                outline: none;
                border-color: #1877f2;
            }}
            .conditions-builder {{
                background: #f2f3f5;
                border-radius: 8px;
                padding: 20px;
                margin-top: 16px;
            }}
            .condition-item {{
                background: #ffffff;
                border: 1px solid #dadde1;
                border-radius: 6px;
                padding: 16px;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .condition-item select,
            .condition-item input {{
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #dadde1;
                border-radius: 4px;
            }}
            .btn-add-condition {{
                background: #1877f2;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                margin-top: 12px;
            }}
            .btn-add-condition:hover {{
                background: #166fe5;
            }}
            .btn-remove-condition {{
                background: #e74c3c;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                cursor: pointer;
            }}
            .btn-remove-condition:hover {{
                background: #c0392b;
            }}
            .preview-section {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin-top: 24px;
            }}
            .preview-section h4 {{
                font-size: 16px;
                font-weight: 600;
                color: #1c1e21;
                margin-bottom: 12px;
            }}
            .preview-text {{
                font-size: 14px;
                color: #65676b;
                line-height: 1.6;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-left">
                <h2>{strategy["name"]}</h2>
            </div>
            <button class="btn-share" onclick="shareStrategy()">Share</button>
        </div>
        
        <div class="container">
            <div class="strategy-header">
                <div class="strategy-info">
                    <h1>{strategy["name"]}</h1>
                    <div class="strategy-badges">
                        {badges_html}
                    </div>
                    <div class="strategy-description">
                        {strategy.get("description", "No description available")}
                    </div>
                    <button class="btn-create-rules" onclick="createRuleFromStrategy()">
                        Create rule
                    </button>
                </div>
                <div class="strategy-image">
                    {strategy_icon}
                </div>
            </div>
            
            <div class="form-builder" id="form-builder" style="display: none;">
                <h3>Create Rule</h3>
                <form id="rule-form" onsubmit="saveRule(event)">
                    <div class="form-group">
                        <label>Rule Name *</label>
                        <input type="text" id="rule-name" required placeholder="e.g., Increase budget when ROAS > 3">
                    </div>
                    
                    <div class="form-group">
                        <label>Account</label>
                        <select id="rule-account" multiple>
                            {account_options}
                        </select>
                        <small style="color: #65676b; font-size: 13px;">Hold Ctrl/Cmd to select multiple. Leave empty for all accounts.</small>
                    </div>
                    
                    <div class="form-group">
                        <label>Prefix</label>
                        <select id="rule-prefix" multiple>
                            {prefix_options}
                        </select>
                        <small style="color: #65676b; font-size: 13px;">Hold Ctrl/Cmd to select multiple. Leave empty for all prefixes.</small>
                    </div>
                    
                    <div class="form-group">
                        <label>Action *</label>
                        <select id="rule-action" required>
                            <option value="PAUSE">Pause</option>
                            <option value="RESUME">Resume</option>
                            <option value="INCREASE_BUDGET">Increase Budget</option>
                            <option value="DECREASE_BUDGET">Decrease Budget</option>
                        </select>
                    </div>
                    
                    <div class="conditions-builder">
                        <h4 style="margin-bottom: 16px; font-size: 16px; font-weight: 600;">Conditions</h4>
                        <div id="conditions-container">
                            <!-- Conditions will be added here -->
                        </div>
                        <button type="button" class="btn-add-condition" onclick="addCondition()">+ Add Condition</button>
                    </div>
                    
                    <div class="preview-section">
                        <h4>Preview</h4>
                        <div class="preview-text" id="preview-text">
                            {strategy.get("name", "")} if conditions are met
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 12px; margin-top: 24px;">
                        <button type="submit" class="btn-create-rules">Save Rule</button>
                        <button type="button" class="btn-share" onclick="cancelForm()">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
            const strategy = {json.dumps(strategy)};
            const accounts = {json.dumps(account_list)};
            const prefixes = {json.dumps(prefix_list)};
            const metrics = {json.dumps(all_metrics)};
            const operators = [" > ", " < ", " >= ", " <= ", " == ", " != "];
            const timeframes = {json.dumps(timeframes)};
            
            let conditionCount = 0;
            
            function createRuleFromStrategy() {{
                document.getElementById('form-builder').style.display = 'block';
                // Set default action based on strategy
                if (strategy.logic_type === 'logic1' || strategy.logic_type === 'logic2') {{
                    document.getElementById('rule-action').value = 'PAUSE';
                }} else if (strategy.logic_type === 'logic3') {{
                    document.getElementById('rule-action').value = 'RESUME';
                }}
                addCondition(); // Add first condition
            }}
            
            function addCondition() {{
                conditionCount++;
                const container = document.getElementById('conditions-container');
                const conditionDiv = document.createElement('div');
                conditionDiv.className = 'condition-item';
                conditionDiv.id = `condition-${{conditionCount}}`;
                
                conditionDiv.innerHTML = `
                    <select class="condition-metric" onchange="updatePreview()">
                        {metric_options}
                    </select>
                    <select class="condition-timeframe" onchange="updatePreview()">
                        {timeframe_options}
                    </select>
                    <select class="condition-operator" onchange="updatePreview()">
                        {operator_options_js}
                    </select>
                    <input type="number" class="condition-value" placeholder="Value" onchange="updatePreview()" step="0.01">
                    <button type="button" class="btn-remove-condition" onclick="removeCondition(${{conditionCount}})">Remove</button>
                `;
                
                container.appendChild(conditionDiv);
                updatePreview();
            }}
            
            function removeCondition(id) {{
                const condition = document.getElementById(`condition-${{id}}`);
                if (condition) {{
                    condition.remove();
                    updatePreview();
                }}
            }}
            
            function updatePreview() {{
                const action = document.getElementById('rule-action').value;
                const conditions = [];
                
                document.querySelectorAll('.condition-item').forEach(item => {{
                    const metric = item.querySelector('.condition-metric').value;
                    const timeframe = item.querySelector('.condition-timeframe').value;
                    const operator = item.querySelector('.condition-operator').value;
                    const value = item.querySelector('.condition-value').value;
                    
                    if (metric && timeframe && operator && value) {{
                        const timeframeDisplay = timeframe.replace(/_/g, ' ');
                        conditions.push(`${{metric}} (${{timeframeDisplay}}) ${{operator}} ${{value}}`);
                    }}
                }});
                
                const preview = document.getElementById('preview-text');
                if (conditions.length > 0) {{
                    preview.textContent = `${{action.replace('_', ' ')}} if ${{conditions.join(' and ')}}`;
                }} else {{
                    preview.textContent = `${{action.replace('_', ' ')}} if conditions are met`;
                }}
            }}
            
            async function saveRule(event) {{
                event.preventDefault();
                
                const ruleData = {{
                    name: document.getElementById('rule-name').value,
                    folder: strategy.category || 'General',
                    account_ids: Array.from(document.getElementById('rule-account').selectedOptions).map(o => o.value).filter(v => v),
                    prefixes: Array.from(document.getElementById('rule-prefix').selectedOptions).map(o => o.value).filter(v => v),
                    action: document.getElementById('rule-action').value,
                    conditions: {{
                        AND: []
                    }},
                    action_params: {{}},
                    schedule: {{}},
                    filters: {{}},
                    enabled: true,
                    status: 'DRAFT',
                    description: strategy.description
                }};
                
                // Build conditions
                document.querySelectorAll('.condition-item').forEach(item => {{
                    const metric = item.querySelector('.condition-metric').value;
                    const timeframe = item.querySelector('.condition-timeframe').value;
                    const operator = item.querySelector('.condition-operator').value;
                    const value = item.querySelector('.condition-value').value;
                    
                    if (metric && timeframe && operator && value) {{
                        ruleData.conditions.AND.push({{
                            metric: metric,
                            timeframe: timeframe,
                            operator: operator.trim(),
                            value: parseFloat(value) || value
                        }});
                    }}
                }});
                
                if (ruleData.conditions.AND.length === 0) {{
                    alert('Please add at least one condition');
                    return;
                }}
                
                try {{
                    const response = await fetch('/api/rules/', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify(ruleData)
                    }});
                    
                    if (!response.ok) {{
                        const error = await response.json();
                        alert('Error: ' + (error.detail || 'Failed to save rule'));
                        return;
                    }}
                    
                    alert('Rule created successfully!');
                    document.getElementById('form-builder').style.display = 'none';
                    document.getElementById('rule-form').reset();
                    document.getElementById('conditions-container').innerHTML = '';
                    conditionCount = 0;
                }} catch (error) {{
                    alert('Error: ' + error.message);
                }}
            }}
            
            function cancelForm() {{
                document.getElementById('form-builder').style.display = 'none';
                document.getElementById('rule-form').reset();
                document.getElementById('conditions-container').innerHTML = '';
                conditionCount = 0;
            }}
            
            function shareStrategy() {{
                navigator.clipboard.writeText(window.location.href);
                alert('Strategy link copied to clipboard!');
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/create", response_class=HTMLResponse)
async def create_rule_page(db: Session = Depends(get_db)):
    """Trang tạo rule mới - Style Birch/Madgicx"""
    # Lấy accounts và prefixes
    accounts = db.query(Account).filter(Account.enabled == True).order_by(Account.account_id).all()
    account_list = [{"id": acc.account_id, "name": acc.account_name or acc.account_id} for acc in accounts]
    
    allowed_prefixes = ['FL', 'NM', 'PX', 'TL']
    prefixes = db.query(Prefix).filter(
        Prefix.enabled == True,
        Prefix.prefix.in_(allowed_prefixes)
    ).order_by(Prefix.prefix).all()
    prefix_list = [p.prefix for p in prefixes] if prefixes else allowed_prefixes
    
    # Available metrics
    ecommerce_metrics = ["spend", "purchases", "purchase_roas", "cost_per_purchase", "revenue", "cpm", "ctr"]
    lead_metrics = ["spend", "leads", "cost_per_lead", "cpl", "cpm", "ctr", "results"]
    all_metrics = list(set(ecommerce_metrics + lead_metrics))
    
    # Build options
    account_options = '<option value="">All accounts</option>'
    for acc in account_list:
        account_options += f'<option value="{acc["id"]}">{acc["name"]}</option>'
    
    prefix_options = '<option value="">All prefixes</option>'
    for p in prefix_list:
        prefix_options += f'<option value="{p}">{p}</option>'
    
    metric_options = '<option value="">Select metric</option>'
    for m in all_metrics:
        metric_options += f'<option value="{m}">{m}</option>'
    
    timeframes = ["today", "yesterday", "last_3days", "last_7days", "last_14days", "last_30days"]
    timeframe_options = '<option value="">Select period</option>'
    for t in timeframes:
        display_name = t.replace('_', ' ').title()
        timeframe_options += f'<option value="{t}">{display_name}</option>'
    
    operators = [" > ", " < ", " >= ", " <= ", " == ", " != "]
    operator_options_js = ""
    for op in operators:
        op_trimmed = op.strip()
        operator_options_js += f'<option value="{op_trimmed}">{op}</option>'
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Create Rule - Facebook Ads Automation</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: #ffffff;
                color: #1c1e21;
                line-height: 1.5;
            }}
            .header {{
                background: #ffffff;
                border-bottom: 1px solid #dadde1;
                padding: 16px 24px;
            }}
            .header h2 {{
                font-size: 24px;
                font-weight: 600;
                color: #1c1e21;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                padding: 40px 24px;
            }}
            .page-header {{
                margin-bottom: 32px;
            }}
            .page-header h1 {{
                font-size: 32px;
                font-weight: 700;
                color: #1c1e21;
                margin-bottom: 8px;
            }}
            .page-header p {{
                font-size: 16px;
                color: #65676b;
            }}
            .form-builder {{
                background: #ffffff;
                border: 1px solid #dadde1;
                border-radius: 8px;
                padding: 24px;
            }}
            .form-builder h3 {{
                font-size: 20px;
                font-weight: 600;
                color: #1c1e21;
                margin-bottom: 24px;
            }}
            .form-group {{
                margin-bottom: 24px;
            }}
            .form-group label {{
                display: block;
                font-size: 14px;
                font-weight: 600;
                color: #1c1e21;
                margin-bottom: 8px;
            }}
            .form-group input,
            .form-group select {{
                width: 100%;
                padding: 10px 12px;
                border: 1px solid #dadde1;
                border-radius: 6px;
                font-size: 15px;
                color: #1c1e21;
            }}
            .form-group input:focus,
            .form-group select:focus {{
                outline: none;
                border-color: #1877f2;
            }}
            .conditions-builder {{
                background: #f2f3f5;
                border-radius: 8px;
                padding: 20px;
                margin-top: 16px;
            }}
            .condition-item {{
                background: #ffffff;
                border: 1px solid #dadde1;
                border-radius: 6px;
                padding: 16px;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .condition-item select,
            .condition-item input {{
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #dadde1;
                border-radius: 4px;
            }}
            .btn-add-condition {{
                background: #1877f2;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                margin-top: 12px;
            }}
            .btn-add-condition:hover {{
                background: #166fe5;
            }}
            .btn-remove-condition {{
                background: #e74c3c;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                cursor: pointer;
            }}
            .btn-remove-condition:hover {{
                background: #c0392b;
            }}
            .preview-section {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin-top: 24px;
            }}
            .preview-section h4 {{
                font-size: 16px;
                font-weight: 600;
                color: #1c1e21;
                margin-bottom: 12px;
            }}
            .preview-text {{
                font-size: 14px;
                color: #65676b;
                line-height: 1.6;
            }}
            .btn-save {{
                background: #1877f2;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
            }}
            .btn-save:hover {{
                background: #166fe5;
            }}
            .btn-cancel {{
                background: #ffffff;
                color: #1c1e21;
                border: 1px solid #dadde1;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
            }}
            .btn-cancel:hover {{
                background: #f2f3f5;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Create Rule</h2>
        </div>
        
        <div class="container">
            <div class="page-header">
                <h1>Create New Rule</h1>
                <p>Build a custom automation rule with your own conditions and actions</p>
            </div>
            
            <div class="form-builder">
                <h3>Rule Configuration</h3>
                <form id="rule-form" onsubmit="saveRule(event)">
                    <div class="form-group">
                        <label>Rule Name *</label>
                        <input type="text" id="rule-name" required placeholder="e.g., Increase budget when ROAS > 3">
                    </div>
                    
                    <div class="form-group">
                        <label>Folder</label>
                        <select id="rule-folder">
                            <option value="General">General</option>
                            <option value="Essential">Essential</option>
                            <option value="Scale">Scale</option>
                            <option value="Pause">Pause</option>
                            <option value="Time">Time</option>
                            <option value="Optimise">Optimise</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Account</label>
                        <select id="rule-account" multiple>
                            {account_options}
                        </select>
                        <small style="color: #65676b; font-size: 13px;">Hold Ctrl/Cmd to select multiple. Leave empty for all accounts.</small>
                    </div>
                    
                    <div class="form-group">
                        <label>Prefix</label>
                        <select id="rule-prefix" multiple>
                            {prefix_options}
                        </select>
                        <small style="color: #65676b; font-size: 13px;">Hold Ctrl/Cmd to select multiple. Leave empty for all prefixes.</small>
                    </div>
                    
                    <div class="form-group">
                        <label>Action *</label>
                        <select id="rule-action" required>
                            <option value="PAUSE">Pause</option>
                            <option value="RESUME">Resume</option>
                            <option value="INCREASE_BUDGET">Increase Budget</option>
                            <option value="DECREASE_BUDGET">Decrease Budget</option>
                        </select>
                    </div>
                    
                    <div class="conditions-builder">
                        <h4 style="margin-bottom: 16px; font-size: 16px; font-weight: 600;">Conditions</h4>
                        <div id="conditions-container">
                            <!-- Conditions will be added here -->
                        </div>
                        <button type="button" class="btn-add-condition" onclick="addCondition()">+ Add Condition</button>
                    </div>
                    
                    <div class="preview-section">
                        <h4>Preview</h4>
                        <div class="preview-text" id="preview-text">
                            Rule preview will appear here
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 12px; margin-top: 24px;">
                        <button type="submit" class="btn-save">Save Rule</button>
                        <button type="button" class="btn-cancel" onclick="window.location.href='/rules/'">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
            const accounts = {json.dumps(account_list)};
            const prefixes = {json.dumps(prefix_list)};
            const metrics = {json.dumps(all_metrics)};
            const timeframes = {json.dumps(timeframes)};
            
            let conditionCount = 0;
            
            // Add first condition on load
            window.addEventListener('DOMContentLoaded', function() {{
                addCondition();
            }});
            
            function addCondition() {{
                conditionCount++;
                const container = document.getElementById('conditions-container');
                const conditionDiv = document.createElement('div');
                conditionDiv.className = 'condition-item';
                conditionDiv.id = `condition-${{conditionCount}}`;
                
                conditionDiv.innerHTML = `
                    <select class="condition-metric" onchange="updatePreview()">
                        {metric_options}
                    </select>
                    <select class="condition-timeframe" onchange="updatePreview()">
                        {timeframe_options}
                    </select>
                    <select class="condition-operator" onchange="updatePreview()">
                        {operator_options_js}
                    </select>
                    <input type="number" class="condition-value" placeholder="Value" onchange="updatePreview()" step="0.01">
                    <button type="button" class="btn-remove-condition" onclick="removeCondition(${{conditionCount}})">Remove</button>
                `;
                
                container.appendChild(conditionDiv);
                updatePreview();
            }}
            
            function removeCondition(id) {{
                const condition = document.getElementById(`condition-${{id}}`);
                if (condition) {{
                    condition.remove();
                    updatePreview();
                }}
            }}
            
            function updatePreview() {{
                const action = document.getElementById('rule-action').value;
                const conditions = [];
                
                document.querySelectorAll('.condition-item').forEach(item => {{
                    const metric = item.querySelector('.condition-metric').value;
                    const timeframe = item.querySelector('.condition-timeframe').value;
                    const operator = item.querySelector('.condition-operator').value;
                    const value = item.querySelector('.condition-value').value;
                    
                    if (metric && timeframe && operator && value) {{
                        const timeframeDisplay = timeframe.replace(/_/g, ' ');
                        conditions.push(`${{metric}} (${{timeframeDisplay}}) ${{operator}} ${{value}}`);
                    }}
                }});
                
                const preview = document.getElementById('preview-text');
                if (conditions.length > 0) {{
                    preview.textContent = `${{action.replace('_', ' ')}} if ${{conditions.join(' and ')}}`;
                }} else {{
                    preview.textContent = `${{action.replace('_', ' ')}} if conditions are met`;
                }}
            }}
            
            async function saveRule(event) {{
                event.preventDefault();
                
                const ruleData = {{
                    name: document.getElementById('rule-name').value,
                    folder: document.getElementById('rule-folder').value || 'General',
                    account_ids: Array.from(document.getElementById('rule-account').selectedOptions).map(o => o.value).filter(v => v),
                    prefixes: Array.from(document.getElementById('rule-prefix').selectedOptions).map(o => o.value).filter(v => v),
                    action: document.getElementById('rule-action').value,
                    conditions: {{
                        AND: []
                    }},
                    action_params: {{}},
                    schedule: {{}},
                    filters: {{}},
                    enabled: true,
                    status: 'DRAFT'
                }};
                
                // Build conditions
                document.querySelectorAll('.condition-item').forEach(item => {{
                    const metric = item.querySelector('.condition-metric').value;
                    const timeframe = item.querySelector('.condition-timeframe').value;
                    const operator = item.querySelector('.condition-operator').value;
                    const value = item.querySelector('.condition-value').value;
                    
                    if (metric && timeframe && operator && value) {{
                        ruleData.conditions.AND.push({{
                            metric: metric,
                            timeframe: timeframe,
                            operator: operator.trim(),
                            value: parseFloat(value) || value
                        }});
                    }}
                }});
                
                if (ruleData.conditions.AND.length === 0) {{
                    alert('Please add at least one condition');
                    return;
                }}
                
                try {{
                    const response = await fetch('/api/rules/', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify(ruleData)
                    }});
                    
                    if (!response.ok) {{
                        const error = await response.json();
                        alert('Error: ' + (error.detail || 'Failed to save rule'));
                        return;
                    }}
                    
                    alert('Rule created successfully!');
                    window.location.href = '/rules/';
                }} catch (error) {{
                    alert('Error: ' + error.message);
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

