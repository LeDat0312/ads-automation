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
async def rules_management_v2(db: Session = Depends(get_db)):
    """Giao diện quản lý rules V2 - Trực quan và mạnh mẽ hơn"""
    from app.models.account_prefix import Account, Prefix
    
    # Lấy accounts từ database
    accounts = db.query(Account).filter(Account.enabled == True).order_by(Account.account_id).all()
    account_ids = [acc.account_id for acc in accounts]
    
    # Nếu không có account trong DB, fallback về settings
    if not account_ids:
        settings = get_settings()
        account_ids = settings.ad_account_ids_list
    
    # Lấy prefixes từ database
    prefix_objs = db.query(Prefix).filter(Prefix.enabled == True).order_by(Prefix.prefix).all()
    prefixes = [p.prefix for p in prefix_objs]
    
    # Nếu không có prefix trong DB, fallback về hardcode
    if not prefixes:
        prefixes = ['FL', 'PX', 'TL', 'NM', 'CCHL', 'DHHL', 'HSHL', 'CCB', 'LAKVDH']
    
    # Emoji constants để tránh lỗi backslash trong f-string
    emoji_clipboard = '\U0001F4CB'  # 📋
    emoji_chart = '\U0001F4CA'  # 📊
    emoji_play = '\u25B6'  # ▶
    emoji_folder = '\U0001F4C1'  # 📁
    emoji_label = '\U0001F3F7'  # 🏷
    
    # Helper function để tạo prefix items HTML
    def build_prefix_items(account_id, prefix_list):
        items = []
        for prefix in prefix_list:
            items.append(f'''                            <li class="tree-item" data-account="{account_id}" data-prefix="{prefix}">
                                <div class="tree-label" onclick="selectNode(this, 'prefix', '{account_id}', '{prefix}')">
                                    <span class="tree-icon">{emoji_label}</span>
                                    <span>{prefix}</span>
                                </div>
                            </li>''')
        return '\n'.join(items)
    
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
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1>⚙️ Quản lý Logic Rules V2</h1>
                    <p>Giao diện trực quan để cấu hình rules cho từng tài khoản và prefix</p>
                </div>
                <button class="btn btn-primary" onclick="openManageModal()" style="padding: 10px 20px; font-size: 14px;">
                    ⚙️ Quản lý Accounts & Prefixes
                </button>
            </div>
        </div>
        
        <div class="container">
            <!-- Sidebar: Tree view -->
            <div class="sidebar">
                <h3 style="margin-bottom: 15px;">{emoji_clipboard} Chọn Account & Prefix</h3>
                <ul class="tree-view" id="tree-view">
                    <li class="tree-item" data-type="all">
                        <div class="tree-label" onclick="selectNode(this, 'all', null, null)">
                            <span class="tree-icon">{emoji_chart}</span>
                            <span>Tất cả</span>
                        </div>
                    </li>
                    {"".join([f'''
                    <li class="tree-item" data-account="{acc}">
                        <div class="tree-label" onclick="toggleNode(this)">
                            <span class="tree-icon">{emoji_play}</span>
                            <span>{acc}</span>
                        </div>
                        <ul class="tree-children">
                            <li class="tree-item" data-account="{acc}" data-prefix="all">
                                <div class="tree-label" onclick="selectNode(this, 'account', '{acc}', null)">
                                    <span class="tree-icon">{emoji_folder}</span>
                                    <span>Tất cả Prefix</span>
                                </div>
                            </li>
                            {build_prefix_items(acc, prefixes)}
                        </ul>
                    </li>
                    ''' for acc in account_ids])}
                </ul>
            </div>
            
            <!-- Main Content: Form -->
            <div class="main-content">
                <div id="alert-container"></div>
                
                <!-- Tabs: Rules vs Logic 7 Days Config -->
                <div class="objective-selector" style="margin-bottom: 20px;">
                    <div class="objective-btn active" data-tab="rules" onclick="switchTab('rules')">
                        📋 Logic Rules
                    </div>
                    <div class="objective-btn" data-tab="7days" onclick="switchTab('7days')">
                        🔍 Logic 7 Ngày
                    </div>
                </div>
                
                <!-- Rules Tab -->
                <div id="rules-tab" class="tab-content">
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
                
                <!-- Logic 7 Days Config Tab -->
                <div id="7days-tab" class="tab-content" style="display: none;">
                    <h3 style="margin-bottom: 20px;">🔍 Cấu hình Logic Lọc 7 Ngày</h3>
                    <p style="color: #666; margin-bottom: 20px;">
                        Cấu hình ngưỡng và điều kiện cho logic lọc adsets trong N ngày qua.
                        Mỗi account + prefix có thể có config riêng. Để trống account/prefix = áp dụng cho tất cả.
                    </p>
                    
                    <!-- 7 Days Config Form -->
                    <form id="7days-config-form">
                        <input type="hidden" id="config-id" value="">
                        <input type="hidden" id="config-account" value="">
                        <input type="hidden" id="config-prefix" value="">
                        
                        <div class="form-section">
                            <h3>📝 Thông tin cơ bản</h3>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Account</label>
                                    <input type="text" id="display-config-account" readonly placeholder="Chọn từ tree view bên trái">
                                    <small style="color: #666;">Để trống = áp dụng cho tất cả accounts</small>
                                </div>
                                <div class="form-group">
                                    <label>Prefix</label>
                                    <input type="text" id="display-config-prefix" readonly placeholder="Chọn từ tree view bên trái">
                                    <small style="color: #666;">Để trống = áp dụng cho tất cả prefixes</small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="form-section">
                            <h3>⚙️ Ngưỡng cấu hình</h3>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Ngưỡng chi tiêu (VND) *</label>
                                    <input type="number" id="config-spend-threshold" value="100000" min="0" step="1000" required>
                                    <small style="color: #666;">Mặc định: 100,000₫</small>
                                </div>
                                <div class="form-group">
                                    <label>Ngưỡng giá DATA (VND)</label>
                                    <input type="number" id="config-gia-data-threshold" value="0" min="0" step="1000">
                                    <small style="color: #666;">0 = dùng từ SL_2_GIA_DATA trong Logic Rules</small>
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Ngưỡng giữ lại Cost/Purchase (VND) *</label>
                                    <input type="number" id="config-cost-per-purchase" value="150000" min="0" step="1000" required>
                                    <small style="color: #666;">Nếu cost_per_purchase < ngưỡng này thì giữ lại dù gia_data > ngưỡng</small>
                                </div>
                                <div class="form-group">
                                    <label>Số ngày lọc *</label>
                                    <input type="number" id="config-days" value="7" min="1" max="30" required>
                                    <small style="color: #666;">Mặc định: 7 ngày</small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="config-enabled" checked>
                                Bật config này
                            </label>
                        </div>
                        
                        <div style="display: flex; gap: 10px;">
                            <button type="submit" class="btn btn-primary">💾 Lưu Config</button>
                            <button type="button" class="btn btn-secondary" onclick="reset7DaysForm()">🔄 Reset</button>
                        </div>
                    </form>
                    
                    <!-- 7 Days Config List -->
                    <div class="rules-list" style="margin-top: 30px;">
                        <h3>📋 Danh sách Config Logic 7 Ngày</h3>
                        <div id="7days-configs-container">Đang tải...</div>
                    </div>
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
                load7DaysConfigs();
                setupFormHandlers();
            }});
            
            // Setup form handlers
            function setupFormHandlers() {{
                document.getElementById('rule-form').addEventListener('submit', async (e) => {{
                    e.preventDefault();
                    await saveRule();
                }});
                
                const configForm = document.getElementById('7days-config-form');
                if (configForm) {{
                    configForm.addEventListener('submit', async (e) => {{
                        e.preventDefault();
                        await save7DaysConfig();
                    }});
                }}
            }}
            
            // Switch tab
            function switchTab(tabName) {{
                // Hide all tabs
                document.getElementById('rules-tab').style.display = 'none';
                document.getElementById('7days-tab').style.display = 'none';
                
                // Show selected tab
                document.getElementById(tabName + '-tab').style.display = 'block';
                
                // Update tab buttons
                document.querySelectorAll('[data-tab]').forEach(btn => {{
                    btn.classList.remove('active');
                }});
                const activeBtn = document.querySelector(`[data-tab="${{tabName}}"]`);
                if (activeBtn) {{
                    activeBtn.classList.add('active');
                }}
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
                
                // Update 7 days config form nếu đang ở tab 7days
                const tab7days = document.getElementById('7days-tab');
                if (tab7days && tab7days.style.display !== 'none') {{
                    document.getElementById('config-account').value = account || '';
                    document.getElementById('config-prefix').value = prefix || '';
                    
                    if (type === 'all') {{
                        document.getElementById('display-config-account').value = '';
                        document.getElementById('display-config-prefix').value = '';
                    }} else if (type === 'account') {{
                        document.getElementById('display-config-account').value = account;
                        document.getElementById('display-config-prefix').value = '';
                    }} else if (type === 'prefix') {{
                        document.getElementById('display-config-account').value = account;
                        document.getElementById('display-config-prefix').value = prefix;
                    }}
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
            // ===== QUẢN LÝ ACCOUNTS & PREFIXES =====
            let manageModal = null;
            
            function openManageModal() {{
                if (!manageModal) {{
                    createManageModal();
                }}
                manageModal.style.display = 'block';
                loadAccounts();
                loadPrefixes();
            }}
            
            function closeManageModal() {{
                if (manageModal) {{
                    manageModal.style.display = 'none';
                }}
            }}
            
            function createManageModal() {{
                const modal = document.createElement('div');
                modal.id = 'manage-modal';
                modal.style.cssText = 'display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; overflow-y: auto;';
                modal.innerHTML = `
                    <div style="max-width: 900px; margin: 50px auto; background: white; border-radius: 8px; padding: 30px; position: relative;">
                        <button onclick="closeManageModal()" style="position: absolute; top: 10px; right: 10px; background: #ef4444; color: white; border: none; border-radius: 4px; padding: 8px 12px; cursor: pointer;">✕ Đóng</button>
                        <h2 style="margin-bottom: 20px;">⚙️ Quản lý Accounts & Prefixes</h2>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                            <!-- Accounts Section -->
                            <div>
                                <h3 style="margin-bottom: 15px;">📊 Accounts</h3>
                                <div id="accounts-list" style="margin-bottom: 15px; max-height: 400px; overflow-y: auto;"></div>
                                <div style="border-top: 1px solid #ddd; padding-top: 15px;">
                                    <h4>Thêm Account mới</h4>
                                    <input type="text" id="new-account-id" placeholder="Account ID (VD: 2827767517395636)" style="width: 100%; padding: 8px; margin-bottom: 8px; border: 1px solid #ddd; border-radius: 4px;">
                                    <input type="text" id="new-account-name" placeholder="Tên Account (tùy chọn)" style="width: 100%; padding: 8px; margin-bottom: 8px; border: 1px solid #ddd; border-radius: 4px;">
                                    <button class="btn btn-primary" onclick="addAccount()" style="width: 100%;">➕ Thêm Account</button>
                                </div>
                            </div>
                            
                            <!-- Prefixes Section -->
                            <div>
                                <h3 style="margin-bottom: 15px;">🏷 Prefixes</h3>
                                <div id="prefixes-list" style="margin-bottom: 15px; max-height: 400px; overflow-y: auto;"></div>
                                <div style="border-top: 1px solid #ddd; padding-top: 15px;">
                                    <h4>Thêm Prefix mới</h4>
                                    <input type="text" id="new-prefix" placeholder="Prefix (VD: FL, PX, TL)" style="width: 100%; padding: 8px; margin-bottom: 8px; border: 1px solid #ddd; border-radius: 4px;">
                                    <input type="text" id="new-prefix-name" placeholder="Tên Prefix (tùy chọn)" style="width: 100%; padding: 8px; margin-bottom: 8px; border: 1px solid #ddd; border-radius: 4px;">
                                    <button class="btn btn-primary" onclick="addPrefix()" style="width: 100%;">➕ Thêm Prefix</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
                manageModal = modal;
                
                // Close modal when clicking outside
                modal.addEventListener('click', function(e) {{
                    if (e.target === modal) {{
                        closeManageModal();
                    }}
                }});
            }}
            
            async function loadAccounts() {{
                try {{
                    const response = await fetch('/api/accounts-prefixes/accounts');
                    const accounts = await response.json();
                    const container = document.getElementById('accounts-list');
                    
                    if (accounts.length === 0) {{
                        container.innerHTML = '<p style="color: #666;">Chưa có account nào</p>';
                        return;
                    }}
                    
                    container.innerHTML = accounts.map(acc => `
                        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>${{acc.account_id}}</strong>
                                ${{acc.account_name ? '<br><small style="color: #666;">' + acc.account_name + '</small>' : ''}}
                                <br><small style="color: ${{acc.enabled ? '#10b981' : '#ef4444'}};">${{acc.enabled ? '✓ Bật' : '✗ Tắt'}}</small>
                            </div>
                            <div>
                                <button class="btn btn-primary" onclick="toggleAccount('${{acc.account_id}}', ${{!acc.enabled}})" style="padding: 4px 8px; font-size: 12px; margin-right: 5px;">
                                    ${{acc.enabled ? 'Tắt' : 'Bật'}}
                                </button>
                                <button class="btn btn-danger" onclick="deleteAccount('${{acc.account_id}}')" style="padding: 4px 8px; font-size: 12px;">Xóa</button>
                            </div>
                        </div>
                    `).join('');
                }} catch (error) {{
                    console.error('Error loading accounts:', error);
                }}
            }}
            
            async function loadPrefixes() {{
                try {{
                    const response = await fetch('/api/accounts-prefixes/prefixes');
                    const prefixes = await response.json();
                    const container = document.getElementById('prefixes-list');
                    
                    if (prefixes.length === 0) {{
                        container.innerHTML = '<p style="color: #666;">Chưa có prefix nào</p>';
                        return;
                    }}
                    
                    container.innerHTML = prefixes.map(prefix => `
                        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>${{prefix.prefix}}</strong>
                                ${{prefix.prefix_name ? '<br><small style="color: #666;">' + prefix.prefix_name + '</small>' : ''}}
                                <br><small style="color: ${{prefix.enabled ? '#10b981' : '#ef4444'}};">${{prefix.enabled ? '✓ Bật' : '✗ Tắt'}}</small>
                            </div>
                            <div>
                                <button class="btn btn-primary" onclick="togglePrefix('${{prefix.prefix}}', ${{!prefix.enabled}})" style="padding: 4px 8px; font-size: 12px; margin-right: 5px;">
                                    ${{prefix.enabled ? 'Tắt' : 'Bật'}}
                                </button>
                                <button class="btn btn-danger" onclick="deletePrefix('${{prefix.prefix}}')" style="padding: 4px 8px; font-size: 12px;">Xóa</button>
                            </div>
                        </div>
                    `).join('');
                }} catch (error) {{
                    console.error('Error loading prefixes:', error);
                }}
            }}
            
            async function addAccount() {{
                const accountId = document.getElementById('new-account-id').value.trim();
                const accountName = document.getElementById('new-account-name').value.trim();
                
                if (!accountId) {{
                    alert('Vui lòng nhập Account ID');
                    return;
                }}
                
                try {{
                    const response = await fetch('/api/accounts-prefixes/accounts', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            account_id: accountId,
                            account_name: accountName || null,
                            enabled: true
                        }})
                    }});
                    
                    if (response.ok) {{
                        document.getElementById('new-account-id').value = '';
                        document.getElementById('new-account-name').value = '';
                        loadAccounts();
                        // Reload tree view
                        location.reload();
                    }} else {{
                        const error = await response.json();
                        alert('Lỗi: ' + (error.detail || 'Unknown error'));
                    }}
                }} catch (error) {{
                    alert('Lỗi: ' + error.message);
                }}
            }}
            
            async function addPrefix() {{
                const prefix = document.getElementById('new-prefix').value.trim().toUpperCase();
                const prefixName = document.getElementById('new-prefix-name').value.trim();
                
                if (!prefix) {{
                    alert('Vui lòng nhập Prefix');
                    return;
                }}
                
                try {{
                    const response = await fetch('/api/accounts-prefixes/prefixes', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            prefix: prefix,
                            prefix_name: prefixName || null,
                            enabled: true
                        }})
                    }});
                    
                    if (response.ok) {{
                        document.getElementById('new-prefix').value = '';
                        document.getElementById('new-prefix-name').value = '';
                        loadPrefixes();
                        // Reload tree view
                        location.reload();
                    }} else {{
                        const error = await response.json();
                        alert('Lỗi: ' + (error.detail || 'Unknown error'));
                    }}
                }} catch (error) {{
                    alert('Lỗi: ' + error.message);
                }}
            }}
            
            async function toggleAccount(accountId, enabled) {{
                try {{
                    const response = await fetch(`/api/accounts-prefixes/accounts/${{accountId}}`, {{
                        method: 'PUT',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ enabled: enabled }})
                    }});
                    
                    if (response.ok) {{
                        loadAccounts();
                        location.reload();
                    }} else {{
                        const error = await response.json();
                        alert('Lỗi: ' + (error.detail || 'Unknown error'));
                    }}
                }} catch (error) {{
                    alert('Lỗi: ' + error.message);
                }}
            }}
            
            async function togglePrefix(prefix, enabled) {{
                try {{
                    const response = await fetch(`/api/accounts-prefixes/prefixes/${{prefix}}`, {{
                        method: 'PUT',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ enabled: enabled }})
                    }});
                    
                    if (response.ok) {{
                        loadPrefixes();
                        location.reload();
                    }} else {{
                        const error = await response.json();
                        alert('Lỗi: ' + (error.detail || 'Unknown error'));
                    }}
                }} catch (error) {{
                    alert('Lỗi: ' + error.message);
                }}
            }}
            
            async function deleteAccount(accountId) {{
                if (!confirm(`Bạn có chắc muốn xóa account ${{accountId}}?`)) return;
                
                try {{
                    const response = await fetch(`/api/accounts-prefixes/accounts/${{accountId}}`, {{
                        method: 'DELETE'
                    }});
                    
                    if (response.ok) {{
                        loadAccounts();
                        location.reload();
                    }} else {{
                        const error = await response.json();
                        alert('Lỗi: ' + (error.detail || 'Unknown error'));
                    }}
                }} catch (error) {{
                    alert('Lỗi: ' + error.message);
                }}
            }}
            
            async function deletePrefix(prefix) {{
                if (!confirm(`Bạn có chắc muốn xóa prefix ${{prefix}}?`)) return;
                
                try {{
                    const response = await fetch(`/api/accounts-prefixes/prefixes/${{prefix}}`, {{
                        method: 'DELETE'
                    }});
                    
                    if (response.ok) {{
                        loadPrefixes();
                        location.reload();
                    }} else {{
                        const error = await response.json();
                        alert('Lỗi: ' + (error.detail || 'Unknown error'));
                    }}
                }} catch (error) {{
                    alert('Lỗi: ' + error.message);
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

