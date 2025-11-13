# -*- coding: utf-8 -*-
"""
Rules Management UI V2 - Giao diện trực quan và mạnh mẽ hơn
- Tree view: Account → Prefix → Rules
- Chọn mục tiêu: E-commerce / Lead
- Form builder trực quan
- Templates cho các giai đoạn
"""
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.logic_rule import LogicRule
from app.core.config import get_settings
import json

router = APIRouter(prefix="/rules-v2", tags=["rules_ui_v2"])


@router.get("/", response_class=HTMLResponse)
async def rules_management_v2():
    """Giao diện quản lý rules V2 - Trực quan và mạnh mẽ hơn"""
    settings = get_settings()
    account_ids = settings.ad_account_ids_list
    
    # Lấy prefixes từ database hoặc hardcode
    prefixes = ['FL', 'PX', 'TL', 'NM', 'CCHL', 'DHHL', 'HSHL', 'CCB', 'CCB', 'LAKVDH']
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quản lý Logic Rules V2 - Facebook Ads Automation</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f5f5;
                color: #333;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                font-size: 24px;
                margin-bottom: 5px;
            }}
            .container {{
                max-width: 1600px;
                margin: 20px auto;
                padding: 0 20px;
                display: grid;
                grid-template-columns: 350px 1fr;
                gap: 20px;
            }}
            .sidebar {{
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                height: fit-content;
                position: sticky;
                top: 20px;
            }}
            .main-content {{
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .tree-view {{
                list-style: none;
            }}
            .tree-item {{
                margin-bottom: 5px;
            }}
            .tree-item > .tree-label {{
                padding: 8px 12px;
                cursor: pointer;
                border-radius: 4px;
                display: flex;
                align-items: center;
                gap: 8px;
                user-select: none;
            }}
            .tree-item > .tree-label:hover {{
                background: #f3f4f6;
            }}
            .tree-item.active > .tree-label {{
                background: #667eea;
                color: white;
            }}
            .tree-children {{
                margin-left: 20px;
                margin-top: 5px;
                display: none;
            }}
            .tree-item.expanded > .tree-children {{
                display: block;
            }}
            .tree-icon {{
                width: 16px;
                text-align: center;
            }}
            .form-section {{
                margin-bottom: 25px;
                padding-bottom: 25px;
                border-bottom: 1px solid #e5e7eb;
            }}
            .form-section:last-child {{
                border-bottom: none;
            }}
            .form-section h3 {{
                font-size: 16px;
                margin-bottom: 15px;
                color: #374151;
            }}
            .form-group {{
                margin-bottom: 15px;
            }}
            .form-group label {{
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                font-size: 14px;
                color: #555;
            }}
            .form-group input,
            .form-group select,
            .form-group textarea {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }}
            .form-group textarea {{
                min-height: 100px;
                font-family: monospace;
            }}
            .form-row {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }}
            .btn {{
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: background 0.2s;
            }}
            .btn-primary {{
                background: #667eea;
                color: white;
            }}
            .btn-primary:hover {{
                background: #5568d3;
            }}
            .btn-danger {{
                background: #ef4444;
                color: white;
            }}
            .btn-secondary {{
                background: #6b7280;
                color: white;
            }}
            .objective-selector {{
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }}
            .objective-btn {{
                flex: 1;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                background: white;
                cursor: pointer;
                text-align: center;
                font-weight: 500;
                transition: all 0.2s;
            }}
            .objective-btn.active {{
                border-color: #667eea;
                background: #667eea;
                color: white;
            }}
            .condition-builder {{
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 15px;
            }}
            .condition-item {{
                display: grid;
                grid-template-columns: 2fr 1fr 1fr 1fr auto;
                gap: 10px;
                margin-bottom: 10px;
                align-items: center;
            }}
            .condition-item:last-child {{
                margin-bottom: 0;
            }}
            .btn-add-condition {{
                background: #10b981;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
            }}
            .btn-remove {{
                background: #ef4444;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
            }}
            .alert {{
                padding: 12px;
                border-radius: 4px;
                margin-bottom: 15px;
            }}
            .alert-success {{
                background: #d1fae5;
                color: #065f46;
                border: 1px solid #a7f3d0;
            }}
            .alert-error {{
                background: #fee2e2;
                color: #991b1b;
                border: 1px solid #fecaca;
            }}
            .hidden {{
                display: none;
            }}
            .rules-list {{
                margin-top: 20px;
            }}
            .rule-card {{
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 15px;
                margin-bottom: 10px;
            }}
            .rule-header {{
                display: flex;
                justify-content: space-between;
                align-items: start;
                margin-bottom: 10px;
            }}
            .rule-title {{
                font-weight: 600;
                font-size: 16px;
            }}
            .rule-badges {{
                display: flex;
                gap: 5px;
                flex-wrap: wrap;
                margin-top: 10px;
            }}
            .badge {{
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }}
            .badge-enabled {{
                background: #d1fae5;
                color: #065f46;
            }}
            .badge-disabled {{
                background: #fee2e2;
                color: #991b1b;
            }}
            .badge-account {{
                background: #dbeafe;
                color: #1e40af;
            }}
            .badge-prefix {{
                background: #f3e8ff;
                color: #6b21a8;
            }}
            .badge-objective {{
                background: #fef3c7;
                color: #92400e;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚙️ Quản lý Logic Rules V2</h1>
            <p>Giao diện trực quan để cấu hình rules cho từng tài khoản và prefix</p>
        </div>
        
        <div class="container">
            <!-- Sidebar: Tree view -->
            <div class="sidebar">
                <h3 style="margin-bottom: 15px;">📋 Chọn Account & Prefix</h3>
                <ul class="tree-view" id="tree-view">
                    <li class="tree-item" data-type="all">
                        <div class="tree-label" onclick="selectNode(this, 'all', null, null)">
                            <span class="tree-icon">\U0001F4CA</span>
                            <span>Tất cả</span>
                        </div>
                    </li>
                    {"".join([f'''
                    <li class="tree-item" data-account="{acc}">
                        <div class="tree-label" onclick="toggleNode(this)">
                            <span class="tree-icon">\u25B6</span>
                            <span>{acc}</span>
                        </div>
                        <ul class="tree-children">
                            <li class="tree-item" data-account="{acc}" data-prefix="all">
                                <div class="tree-label" onclick="selectNode(this, 'account', '{acc}', null)">
                                    <span class="tree-icon">\U0001F4C1</span>
                                    <span>Tất cả Prefix</span>
                                </div>
                            </li>
                            {"".join([f'''
                            <li class="tree-item" data-account="{acc}" data-prefix="{prefix}">
                                <div class="tree-label" onclick="selectNode(this, 'prefix', '{acc}', '{prefix}')">
                                    <span class="tree-icon">\U0001F3F7</span>
                                    <span>{prefix}</span>
                                </div>
                            </li>
                            ''' for prefix in prefixes])}
                        </ul>
                    </li>
                    ''' for acc in account_ids])}
                </ul>
            </div>
            
            <!-- Main Content: Form -->
            <div class="main-content">
                <div id="alert-container"></div>
                
                <!-- Objective Selector -->
                <div class="objective-selector">
                    <div class="objective-btn active" data-objective="ECOMMERCE" onclick="selectObjective('ECOMMERCE')">
                        🛒 Thương mại điện tử
                    </div>
                    <div class="objective-btn" data-objective="LEAD" onclick="selectObjective('LEAD')">
                        📞 Số lượng khách hàng tiềm năng
                    </div>
                </div>
                
                <!-- Form -->
                <form id="rule-form">
                    <input type="hidden" id="rule-id" value="">
                    <input type="hidden" id="selected-account" value="">
                    <input type="hidden" id="selected-prefix" value="">
                    <input type="hidden" id="selected-objective" value="ECOMMERCE">
                    
                    <div class="form-section">
                        <h3>📝 Thông tin cơ bản</h3>
                        <div class="form-group">
                            <label>Tên Rule *</label>
                            <input type="text" id="rule-name" required placeholder="VD: Tăng budget khi CPL thấp">
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Account</label>
                                <input type="text" id="display-account" readonly placeholder="Chọn từ tree view bên trái">
                            </div>
                            <div class="form-group">
                                <label>Prefix</label>
                                <input type="text" id="display-prefix" readonly placeholder="Chọn từ tree view bên trái">
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h3>🎯 Điều kiện (Conditions)</h3>
                        <div class="condition-builder" id="condition-builder">
                            <div class="condition-item">
                                <select class="condition-metric">
                                    <option value="spend">Chi tiêu (Spend)</option>
                                    <option value="cpl">CPL (Cost per Lead)</option>
                                    <option value="cpa">CPA (Cost per Action)</option>
                                    <option value="roas">ROAS</option>
                                    <option value="results">Kết quả (Results)</option>
                                    <option value="gia_data">Giá DATA</option>
                                    <option value="purchases">Lượt mua (Purchases)</option>
                                    <option value="purchase_value">Giá trị chuyển đổi</option>
                                    <option value="leads">Leads</option>
                                    <option value="checkouts">Checkouts Initiated</option>
                                </select>
                                <select class="condition-operator">
                                    <option value=">">Lớn hơn (>)</option>
                                    <option value="<">Nhỏ hơn (<)</option>
                                    <option value=">=">Lớn hơn hoặc bằng (>=)</option>
                                    <option value="<=">Nhỏ hơn hoặc bằng (<=)</option>
                                    <option value="==">Bằng (==)</option>
                                    <option value="!=">Khác (!=)</option>
                                </select>
                                <input type="number" class="condition-value" placeholder="Giá trị" step="0.01">
                                <select class="condition-timeframe">
                                    <option value="today">Hôm nay</option>
                                    <option value="yesterday">Hôm qua</option>
                                    <option value="last_3days">3 ngày gần nhất</option>
                                    <option value="last_7days">7 ngày gần nhất</option>
                                </select>
                                <button type="button" class="btn-remove" onclick="removeCondition(this)">✕</button>
                            </div>
                        </div>
                        <button type="button" class="btn-add-condition" onclick="addCondition()">+ Thêm điều kiện</button>
                    </div>
                    
                    <div class="form-section">
                        <h3>⚡ Action</h3>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Action *</label>
                                <select id="rule-action" required>
                                    <option value="">-- Chọn action --</option>
                                    <option value="INCREASE_BUDGET">Tăng Budget</option>
                                    <option value="DECREASE_BUDGET">Giảm Budget</option>
                                    <option value="PAUSE">Tạm dừng</option>
                                    <option value="RESUME">Tiếp tục</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Trạng thái</label>
                                <select id="rule-status">
                                    <option value="DRAFT">Draft</option>
                                    <option value="LIVE">Live</option>
                                    <option value="PAUSED">Paused</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Action Params (JSON - tùy chọn)</label>
                            <textarea id="rule-action-params" placeholder='{{"percent": 20, "frequency": "once_a_day"}}'></textarea>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="rule-enabled" checked>
                            Bật rule này
                        </label>
                    </div>
                    
                    <div style="display: flex; gap: 10px;">
                        <button type="submit" class="btn btn-primary">💾 Lưu Rule</button>
                        <button type="button" class="btn btn-secondary" onclick="resetForm()">🔄 Reset</button>
                    </div>
                </form>
                
                <!-- Rules List -->
                <div class="rules-list" id="rules-list">
                    <h3 style="margin-top: 30px; margin-bottom: 15px;">📋 Danh sách Rules</h3>
                    <p>Đang tải...</p>
                </div>
            </div>
        </div>
        
        <script>
            const accountIds = {json.dumps(account_ids)};
            const prefixes = {json.dumps(prefixes)};
            let currentObjective = 'ECOMMERCE';
            let currentAccount = null;
            let currentPrefix = null;
            
            // Load rules khi trang load
            window.addEventListener('DOMContentLoaded', () => {{
                loadRules();
                setupFormHandlers();
            }});
            
            // Setup form handlers
            function setupFormHandlers() {{
                document.getElementById('rule-form').addEventListener('submit', async (e) => {{
                    e.preventDefault();
                    await saveRule();
                }});
            }}
            
            // Select objective
            function selectObjective(objective) {{
                currentObjective = objective;
                document.getElementById('selected-objective').value = objective;
                document.querySelectorAll('.objective-btn').forEach(btn => {{
                    btn.classList.remove('active');
                }});
                document.querySelector(`[data-objective="${{objective}}"]`).classList.add('active');
            }}
            
            // Toggle tree node
            function toggleNode(element) {{
                const item = element.closest('.tree-item');
                item.classList.toggle('expanded');
                const icon = element.querySelector('.tree-icon');
                icon.textContent = item.classList.contains('expanded') ? '▼' : '▶';
            }}
            
            // Select node
            function selectNode(element, type, account, prefix) {{
                // Remove active from all
                document.querySelectorAll('.tree-item').forEach(item => {{
                    item.classList.remove('active');
                }});
                
                // Add active to selected
                element.closest('.tree-item').classList.add('active');
                
                // Update form
                currentAccount = account;
                currentPrefix = prefix;
                document.getElementById('selected-account').value = account || '';
                document.getElementById('selected-prefix').value = prefix || '';
                
                if (type === 'all') {{
                    document.getElementById('display-account').value = 'Tất cả';
                    document.getElementById('display-prefix').value = 'Tất cả';
                }} else if (type === 'account') {{
                    document.getElementById('display-account').value = account;
                    document.getElementById('display-prefix').value = 'Tất cả';
                }} else if (type === 'prefix') {{
                    document.getElementById('display-account').value = account;
                    document.getElementById('display-prefix').value = prefix;
                }}
            }}
            
            // Add condition
            function addCondition() {{
                const builder = document.getElementById('condition-builder');
                const newCondition = document.createElement('div');
                newCondition.className = 'condition-item';
                newCondition.innerHTML = `
                    <select class="condition-metric">
                        <option value="spend">Chi tiêu (Spend)</option>
                        <option value="cpl">CPL (Cost per Lead)</option>
                        <option value="cpa">CPA (Cost per Action)</option>
                        <option value="roas">ROAS</option>
                        <option value="results">Kết quả (Results)</option>
                        <option value="gia_data">Giá DATA</option>
                        <option value="purchases">Lượt mua (Purchases)</option>
                        <option value="purchase_value">Giá trị chuyển đổi</option>
                        <option value="leads">Leads</option>
                        <option value="checkouts">Checkouts Initiated</option>
                    </select>
                    <select class="condition-operator">
                        <option value=">">Lớn hơn (>)</option>
                        <option value="<">Nhỏ hơn (<)</option>
                        <option value=">=">Lớn hơn hoặc bằng (>=)</option>
                        <option value="<=">Nhỏ hơn hoặc bằng (<=)</option>
                        <option value="==">Bằng (==)</option>
                        <option value="!=">Khác (!=)</option>
                    </select>
                    <input type="number" class="condition-value" placeholder="Giá trị" step="0.01">
                    <select class="condition-timeframe">
                        <option value="today">Hôm nay</option>
                        <option value="yesterday">Hôm qua</option>
                        <option value="last_3days">3 ngày gần nhất</option>
                        <option value="last_7days">7 ngày gần nhất</option>
                    </select>
                    <button type="button" class="btn-remove" onclick="removeCondition(this)">✕</button>
                `;
                builder.appendChild(newCondition);
            }}
            
            // Remove condition
            function removeCondition(button) {{
                const builder = document.getElementById('condition-builder');
                if (builder.children.length > 1) {{
                    button.closest('.condition-item').remove();
                }}
            }}
            
            // Build conditions JSON
            function buildConditions() {{
                const items = document.querySelectorAll('.condition-item');
                const conditions = [];
                
                items.forEach(item => {{
                    const metric = item.querySelector('.condition-metric').value;
                    const operator = item.querySelector('.condition-operator').value;
                    const valueInput = item.querySelector('.condition-value').value;
                    const timeframe = item.querySelector('.condition-timeframe').value;
                    
                    // Validate
                    if (!metric || !operator || !timeframe) {{
                        return; // Skip invalid condition
                    }}
                    
                    // Parse value - có thể là số hoặc string
                    let value;
                    if (valueInput === '' || valueInput === null || valueInput === undefined) {{
                        return; // Skip if value is empty
                    }}
                    
                    // Try parse as number first
                    const numValue = parseFloat(valueInput);
                    if (!isNaN(numValue)) {{
                        value = numValue;
                    }} else {{
                        value = valueInput; // Keep as string if not a number
                    }}
                    
                    conditions.push({{
                        metric: metric,
                        operator: operator,
                        value: value,
                        timeframe: timeframe
                    }});
                }});
                
                // Phải có ít nhất 1 condition
                if (conditions.length === 0) {{
                    return null;
                }}
                
                return {{ AND: conditions }};
            }}
            
            // Load rules
            async function loadRules() {{
                try {{
                    const response = await fetch('/api/rules?limit=100');
                    const data = await response.json();
                    renderRules(data.rules || []);
                }} catch (error) {{
                    showAlert('Lỗi khi tải rules: ' + error.message, 'error');
                }}
            }}
            
            // Render rules
            function renderRules(rules) {{
                const container = document.getElementById('rules-list');
                if (rules.length === 0) {{
                    container.innerHTML = '<p>Chưa có rule nào. Tạo rule mới ở trên.</p>';
                    return;
                }}
                
                container.innerHTML = rules.map(rule => {{
                    const accountBadges = (rule.account_ids || []).length > 0 
                        ? rule.account_ids.map(acc => `<span class="badge badge-account">${{acc}}</span>`).join('')
                        : '<span class="badge badge-account">Tất cả</span>';
                    
                    const prefixBadges = (rule.prefixes || []).length > 0
                        ? rule.prefixes.filter(p => p).map(p => `<span class="badge badge-prefix">${{p}}</span>`).join('')
                        : '<span class="badge badge-prefix">Tất cả</span>';
                    
                    return `
                        <div class="rule-card">
                            <div class="rule-header">
                                <div>
                                    <div class="rule-title">${{rule.name}}</div>
                                    <div class="rule-badges">
                                        <span class="badge ${{rule.enabled ? 'badge-enabled' : 'badge-disabled'}}">
                                            ${{rule.enabled ? 'Bật' : 'Tắt'}}
                                        </span>
                                        <span class="badge">${{rule.status}}</span>
                                        <span class="badge">${{rule.action}}</span>
                                        ${{accountBadges}}
                                        ${{prefixBadges}}
                                    </div>
                                </div>
                                <div style="display: flex; gap: 5px;">
                                    <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="editRule(${{rule.id}})">✏️ Sửa</button>
                                    <button class="btn btn-danger" style="padding: 6px 12px; font-size: 12px;" onclick="deleteRule(${{rule.id}})">🗑️ Xóa</button>
                                </div>
                            </div>
                        </div>
                    `;
                }}).join('');
            }}
            
            // Save rule
            async function saveRule() {{
                const ruleId = document.getElementById('rule-id').value;
                const account = document.getElementById('selected-account').value;
                const prefix = document.getElementById('selected-prefix').value;
                const objective = document.getElementById('selected-objective').value;
                
                if (!account && account !== '') {{
                    showAlert('Vui lòng chọn account từ tree view bên trái!', 'error');
                    return;
                }}
                
                const conditions = buildConditions();
                if (!conditions || !conditions.AND || conditions.AND.length === 0) {{
                    showAlert('Vui lòng thêm ít nhất 1 điều kiện hợp lệ! (Metric, Operator, Value, Timeframe)', 'error');
                    return;
                }}
                
                const formData = {{
                    name: document.getElementById('rule-name').value,
                    account_ids: account ? [account] : [],
                    prefixes: prefix ? [prefix] : [],
                    action: document.getElementById('rule-action').value,
                    action_params: parseJSON(document.getElementById('rule-action-params').value) || {{}},
                    conditions: conditions,
                    status: document.getElementById('rule-status').value,
                    enabled: document.getElementById('rule-enabled').checked,
                    folder: objective,
                    filters: {{
                        campaign_types: [objective]
                    }}
                }};
                
                try {{
                    const url = ruleId ? `/api/rules/${{ruleId}}` : '/api/rules';
                    const method = ruleId ? 'PUT' : 'POST';
                    
                    const response = await fetch(url, {{
                        method: method,
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(formData)
                    }});
                    
                    const responseData = await response.json();
                    
                    if (response.ok) {{
                        showAlert(ruleId ? 'Đã cập nhật rule!' : 'Đã tạo rule mới!', 'success');
                        resetForm();
                        loadRules();
                    }} else {{
                        const errorMsg = responseData.detail || responseData.message || JSON.stringify(responseData);
                        showAlert('Lỗi: ' + errorMsg, 'error');
                    }}
                }} catch (error) {{
                    showAlert('Lỗi: ' + error.message, 'error');
                }}
            }}
            
            // Edit rule
            async function editRule(ruleId) {{
                try {{
                    const response = await fetch(`/api/rules/${{ruleId}}`);
                    const rule = await response.json();
                    
                    document.getElementById('rule-id').value = rule.id;
                    document.getElementById('rule-name').value = rule.name;
                    document.getElementById('rule-action').value = rule.action;
                    document.getElementById('rule-status').value = rule.status;
                    document.getElementById('rule-enabled').checked = rule.enabled;
                    document.getElementById('rule-action-params').value = JSON.stringify(rule.action_params || {{}}, null, 2);
                    
                    // Set objective from folder or filters
                    const objective = rule.filters?.campaign_types?.[0] || rule.folder || 'ECOMMERCE';
                    selectObjective(objective);
                    
                    // Set account/prefix
                    if (rule.account_ids && rule.account_ids.length > 0) {{
                        document.getElementById('selected-account').value = rule.account_ids[0];
                        document.getElementById('display-account').value = rule.account_ids[0];
                    }}
                    if (rule.prefixes && rule.prefixes.length > 0 && rule.prefixes[0]) {{
                        document.getElementById('selected-prefix').value = rule.prefixes[0];
                        document.getElementById('display-prefix').value = rule.prefixes[0];
                    }}
                    
                    // Load conditions
                    const builder = document.getElementById('condition-builder');
                    builder.innerHTML = '';
                    if (rule.conditions && rule.conditions.AND) {{
                        rule.conditions.AND.forEach(cond => {{
                            addCondition();
                            const lastItem = builder.lastElementChild;
                            lastItem.querySelector('.condition-metric').value = cond.metric || 'spend';
                            lastItem.querySelector('.condition-operator').value = cond.operator || '>';
                            lastItem.querySelector('.condition-value').value = cond.value || '';
                            lastItem.querySelector('.condition-timeframe').value = cond.timeframe || 'today';
                        }});
                    }} else {{
                        addCondition();
                    }}
                    
                    window.scrollTo({{ top: 0, behavior: 'smooth' }});
                }} catch (error) {{
                    showAlert('Lỗi khi tải rule: ' + error.message, 'error');
                }}
            }}
            
            // Delete rule
            async function deleteRule(ruleId) {{
                if (!confirm('Bạn có chắc muốn xóa rule này?')) return;
                
                try {{
                    const response = await fetch(`/api/rules/${{ruleId}}`, {{ method: 'DELETE' }});
                    if (response.ok) {{
                        showAlert('Đã xóa rule!', 'success');
                        loadRules();
                    }} else {{
                        const error = await response.json();
                        showAlert('Lỗi: ' + (error.detail || 'Unknown error'), 'error');
                    }}
                }} catch (error) {{
                    showAlert('Lỗi: ' + error.message, 'error');
                }}
            }}
            
            // Helper functions
            function parseJSON(str) {{
                if (!str || str.trim() === '') return null;
                try {{
                    return JSON.parse(str);
                }} catch {{
                    return null;
                }}
            }}
            
            function resetForm() {{
                document.getElementById('rule-form').reset();
                document.getElementById('rule-id').value = '';
                document.getElementById('selected-account').value = '';
                document.getElementById('selected-prefix').value = '';
                document.getElementById('display-account').value = '';
                document.getElementById('display-prefix').value = '';
                document.getElementById('condition-builder').innerHTML = '';
                addCondition();
                selectObjective('ECOMMERCE');
                document.querySelectorAll('.tree-item').forEach(item => {{
                    item.classList.remove('active');
                }});
            }}
            
            function showAlert(message, type) {{
                const container = document.getElementById('alert-container');
                container.innerHTML = `<div class="alert alert-${{type}}">${{message}}</div>`;
                setTimeout(() => {{
                    container.innerHTML = '';
                }}, 5000);
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

