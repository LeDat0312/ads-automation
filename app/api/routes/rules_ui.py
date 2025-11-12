"""
Rules Management UI
Giao diện đơn giản để quản lý logic rules cho từng account/prefix
"""
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.logic_rule import LogicRule
from app.core.config import get_settings
import json

router = APIRouter(prefix="/rules", tags=["rules_ui"])


@router.get("/", response_class=HTMLResponse)
async def rules_management_page():
    """Trang quản lý logic rules"""
    settings = get_settings()
    account_ids = settings.ad_account_ids_list
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quản lý Logic Rules - Facebook Ads Automation</title>
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
                max-width: 1200px;
                margin: 20px auto;
                padding: 0 20px;
            }}
            .card {{
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .card h2 {{
                font-size: 18px;
                margin-bottom: 15px;
                color: #333;
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
            .btn-danger:hover {{
                background: #dc2626;
            }}
            .btn-secondary {{
                background: #6b7280;
                color: white;
            }}
            .rules-list {{
                margin-top: 20px;
            }}
            .rule-item {{
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 15px;
                margin-bottom: 10px;
                display: flex;
                justify-content: space-between;
                align-items: start;
            }}
            .rule-info {{
                flex: 1;
            }}
            .rule-info h3 {{
                font-size: 16px;
                margin-bottom: 5px;
                color: #333;
            }}
            .rule-meta {{
                font-size: 12px;
                color: #6b7280;
                margin-top: 5px;
            }}
            .rule-actions {{
                display: flex;
                gap: 10px;
            }}
            .badge {{
                display: inline-block;
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
            .checkbox-group {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 5px;
            }}
            .checkbox-item {{
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            .checkbox-item input[type="checkbox"] {{
                width: auto;
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
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚙️ Quản lý Logic Rules</h1>
            <p>Thiết lập logic tự động cho từng tài khoản và prefix</p>
        </div>
        
        <div class="container">
            <div id="alert-container"></div>
            
            <!-- Form tạo/sửa rule -->
            <div class="card">
                <h2 id="form-title">➕ Tạo Rule Mới</h2>
                <form id="rule-form">
                    <input type="hidden" id="rule-id" value="">
                    
                    <div class="form-group">
                        <label>Tên Rule *</label>
                        <input type="text" id="rule-name" required placeholder="VD: Tăng budget khi CPL thấp">
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Tài khoản (Account IDs)</label>
                            <div class="checkbox-group">
                                <label class="checkbox-item">
                                    <input type="checkbox" id="all-accounts" checked>
                                    <span>Tất cả</span>
                                </label>
                                {"".join([f'''
                                <label class="checkbox-item">
                                    <input type="checkbox" class="account-checkbox" value="{acc}" disabled>
                                    <span>{acc}</span>
                                </label>
                                ''' for acc in account_ids])}
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label>Prefix</label>
                            <div class="checkbox-group">
                                <label class="checkbox-item">
                                    <input type="checkbox" id="all-prefixes" checked>
                                    <span>Tất cả</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" class="prefix-checkbox" value="FL">
                                    <span>FL</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" class="prefix-checkbox" value="PX">
                                    <span>PX</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" class="prefix-checkbox" value="TL">
                                    <span>TL</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" class="prefix-checkbox" value="NM">
                                    <span>NM</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" class="prefix-checkbox" value="CCHL">
                                    <span>CCHL</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" class="prefix-checkbox" value="DHHL">
                                    <span>DHHL</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" class="prefix-checkbox" value="HSHL">
                                    <span>HSHL</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" class="prefix-checkbox" value="CCB">
                                    <span>CCB</span>
                                </label>
                            </div>
                        </div>
                    </div>
                    
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
                        <label>Điều kiện (JSON) *</label>
                        <textarea id="rule-conditions" required placeholder='{{"AND": [{{"metric": "spend", "operator": ">", "value": 100000}}]}}'></textarea>
                        <small style="color: #6b7280; font-size: 12px;">
                            Format JSON. VD: {{"AND": [{{"metric": "spend", "operator": ">", "value": 100000}}]}}
                        </small>
                    </div>
                    
                    <div class="form-group">
                        <label>Action Params (JSON)</label>
                        <textarea id="rule-action-params" placeholder='{{"percent": 20, "frequency": "once_a_day"}}'></textarea>
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
            </div>
            
            <!-- Danh sách rules -->
            <div class="card">
                <h2>📋 Danh sách Rules</h2>
                <div id="rules-list" class="rules-list">
                    <p>Đang tải...</p>
                </div>
            </div>
        </div>
        
        <script>
            const accountIds = {json.dumps(account_ids)};
            const prefixes = {json.dumps(['FL', 'PX', 'TL', 'NM', 'CCHL', 'DHHL', 'HSHL', 'CCB'])};
            
            // Load rules khi trang load
            window.addEventListener('DOMContentLoaded', () => {{
                loadRules();
                setupFormHandlers();
            }});
            
            // Setup form handlers
            function setupFormHandlers() {{
                document.getElementById('all-accounts').addEventListener('change', function() {{
                    const checkboxes = document.querySelectorAll('.account-checkbox');
                    checkboxes.forEach(cb => {{
                        cb.disabled = this.checked;
                        cb.checked = false;
                    }});
                }});
                
                document.getElementById('all-prefixes').addEventListener('change', function() {{
                    const checkboxes = document.querySelectorAll('.prefix-checkbox');
                    checkboxes.forEach(cb => {{
                        cb.disabled = this.checked;
                        cb.checked = false;
                    }});
                }});
                
                document.getElementById('rule-form').addEventListener('submit', async (e) => {{
                    e.preventDefault();
                    await saveRule();
                }});
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
                        ? rule.prefixes.map(p => `<span class="badge badge-prefix">${{p}}</span>`).join('')
                        : '<span class="badge badge-prefix">Tất cả</span>';
                    
                    return `
                        <div class="rule-item">
                            <div class="rule-info">
                                <h3>${{rule.name}}</h3>
                                <div class="rule-meta">
                                    <span class="badge ${{rule.enabled ? 'badge-enabled' : 'badge-disabled'}}">
                                        ${{rule.enabled ? 'Bật' : 'Tắt'}}
                                    </span>
                                    <span class="badge">${{rule.status}}</span>
                                    <span class="badge">${{rule.action}}</span>
                                    <br>
                                    <strong>Accounts:</strong> ${{accountBadges}}
                                    <strong>Prefixes:</strong> ${{prefixBadges}}
                                </div>
                            </div>
                            <div class="rule-actions">
                                <button class="btn btn-primary" onclick="editRule(${{rule.id}})">✏️ Sửa</button>
                                <button class="btn btn-danger" onclick="deleteRule(${{rule.id}})">🗑️ Xóa</button>
                            </div>
                        </div>
                    `;
                }}).join('');
            }}
            
            // Save rule
            async function saveRule() {{
                const ruleId = document.getElementById('rule-id').value;
                const formData = {{
                    name: document.getElementById('rule-name').value,
                    account_ids: getSelectedAccounts(),
                    prefixes: getSelectedPrefixes(),
                    action: document.getElementById('rule-action').value,
                    action_params: parseJSON(document.getElementById('rule-action-params').value) || {{}},
                    conditions: parseJSON(document.getElementById('rule-conditions').value),
                    status: document.getElementById('rule-status').value,
                    enabled: document.getElementById('rule-enabled').checked,
                    folder: 'General'
                }};
                
                try {{
                    const url = ruleId ? `/api/rules/${{ruleId}}` : '/api/rules';
                    const method = ruleId ? 'PUT' : 'POST';
                    
                    const response = await fetch(url, {{
                        method: method,
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(formData)
                    }});
                    
                    if (response.ok) {{
                        showAlert(ruleId ? 'Đã cập nhật rule!' : 'Đã tạo rule mới!', 'success');
                        resetForm();
                        loadRules();
                    }} else {{
                        const error = await response.json();
                        showAlert('Lỗi: ' + (error.detail || 'Unknown error'), 'error');
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
                    document.getElementById('rule-conditions').value = JSON.stringify(rule.conditions, null, 2);
                    document.getElementById('rule-action-params').value = JSON.stringify(rule.action_params || {{}}, null, 2);
                    document.getElementById('form-title').textContent = '✏️ Sửa Rule';
                    
                    // Set accounts
                    if (rule.account_ids && rule.account_ids.length > 0) {{
                        document.getElementById('all-accounts').checked = false;
                        rule.account_ids.forEach(acc => {{
                            const cb = document.querySelector(`.account-checkbox[value="${{acc}}"]`);
                            if (cb) {{
                                cb.disabled = false;
                                cb.checked = true;
                            }}
                        }});
                    }} else {{
                        document.getElementById('all-accounts').checked = true;
                    }}
                    
                    // Set prefixes
                    if (rule.prefixes && rule.prefixes.length > 0) {{
                        document.getElementById('all-prefixes').checked = false;
                        rule.prefixes.forEach(prefix => {{
                            const cb = document.querySelector(`.prefix-checkbox[value="${{prefix}}"]`);
                            if (cb) {{
                                cb.disabled = false;
                                cb.checked = true;
                            }}
                        }});
                    }} else {{
                        document.getElementById('all-prefixes').checked = true;
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
                        showAlert('Lỗi khi xóa rule', 'error');
                    }}
                }} catch (error) {{
                    showAlert('Lỗi: ' + error.message, 'error');
                }}
            }}
            
            // Helper functions
            function getSelectedAccounts() {{
                if (document.getElementById('all-accounts').checked) return [];
                const selected = Array.from(document.querySelectorAll('.account-checkbox:checked'))
                    .map(cb => cb.value);
                return selected;
            }}
            
            function getSelectedPrefixes() {{
                if (document.getElementById('all-prefixes').checked) return [];
                const selected = Array.from(document.querySelectorAll('.prefix-checkbox:checked'))
                    .map(cb => cb.value);
                return selected;
            }}
            
            function parseJSON(str) {{
                try {{
                    return JSON.parse(str);
                }} catch {{
                    return null;
                }}
            }}
            
            function resetForm() {{
                document.getElementById('rule-form').reset();
                document.getElementById('rule-id').value = '';
                document.getElementById('form-title').textContent = '➕ Tạo Rule Mới';
                document.getElementById('all-accounts').checked = true;
                document.getElementById('all-prefixes').checked = true;
                document.querySelectorAll('.account-checkbox, .prefix-checkbox').forEach(cb => {{
                    cb.disabled = true;
                    cb.checked = false;
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

