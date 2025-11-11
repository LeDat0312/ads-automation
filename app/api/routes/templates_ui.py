"""
Templates UI API Routes
API endpoints cho rule templates UI (tương tự Meta Ads)
"""
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse, HTMLResponse
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.rule_template import RuleTemplate
from app.services.rule_template_service import (
    get_all_templates,
    apply_template,
    create_template_from_config
)
from app.services.meta_ads_templates import (
    get_templates_by_category,
    get_template_by_name,
    META_ADS_TEMPLATES
)

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("/ui")
async def get_templates_ui(
    campaign_type: Optional[str] = Query(None),  # 'ECOMMERCE', 'LEAD', 'BOTH'
    category: Optional[str] = Query(None),  # 'essential', 'pause', 'scale', 'optimise'
    db: Session = Depends(get_db)
):
    """
    Get templates grouped by category for UI
    Tương tự Meta Ads interface
    """
    try:
        # Get templates from Meta Ads style definitions
        templates = get_templates_by_category(campaign_type, category)
        
        # Group by category
        grouped = {
            "essential": [],
            "pause": [],
            "scale": [],
            "optimise": []
        }
        
        for template in templates:
            cat = template.get('category', 'essential')
            if cat in grouped:
                grouped[cat].append({
                    "name": template['name'],
                    "description": template['description'],
                    "campaign_type": template['campaign_type'],
                    "labels": template.get('labels', []),
                    "icon": template.get('icon', 'default'),
                    "template_config": template['template_config']
                })
        
        return {
            "templates": grouped,
            "total": len(templates),
            "campaign_type": campaign_type,
            "category": category
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/ui/{template_name}")
async def get_template_details(
    template_name: str,
    db: Session = Depends(get_db)
):
    """
    Get template details by name
    """
    try:
        template = get_template_by_name(template_name)
        if not template:
            return JSONResponse(
                status_code=404,
                content={"error": "Template not found"}
            )
        
        return {
            "name": template['name'],
            "description": template['description'],
            "campaign_type": template['campaign_type'],
            "category": template['category'],
            "labels": template.get('labels', []),
            "icon": template.get('icon', 'default'),
            "template_config": template['template_config']
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.post("/ui/{template_name}/apply")
async def apply_template_ui(
    template_name: str,
    account_id: str = Body(...),
    prefix: Optional[str] = Body(None),
    campaign_id: Optional[str] = Body(None),
    custom_values: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db)
):
    """
    Apply template with UI-friendly response
    """
    try:
        template = get_template_by_name(template_name)
        if not template:
            return JSONResponse(
                status_code=404,
                content={"error": "Template not found"}
            )
        
        # Create template in database if not exists
        existing = db.query(RuleTemplate).filter_by(name=template_name).first()
        if not existing:
            template_id = create_template_from_config({
                "name": template['name'],
                "description": template['description'],
                "campaign_type": template['campaign_type'],
                "template_config": template['template_config']
            })
        else:
            template_id = existing.id
        
        # Apply template
        success = apply_template(
            template_id,
            account_id,
            prefix or "",
            custom_values
        )
        
        if success:
            return {
                "success": True,
                "message": f"Template '{template_name}' applied successfully",
                "template_name": template_name,
                "account_id": account_id,
                "prefix": prefix,
                "campaign_id": campaign_id
            }
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Failed to apply template"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/ui/page")
async def templates_ui_page():
    """
    Serve HTML page for templates UI
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rule Templates - Meta Ads Style</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                margin-bottom: 30px;
            }
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }
            .tab {
                padding: 10px 20px;
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                cursor: pointer;
            }
            .tab.active {
                background: #1877f2;
                color: white;
            }
            .category-section {
                margin-bottom: 40px;
            }
            .category-title {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            .templates-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
            }
            .template-card {
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
                cursor: pointer;
                transition: box-shadow 0.2s;
            }
            .template-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            .template-header {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 10px;
            }
            .template-icon {
                width: 40px;
                height: 40px;
                background: #f0f0f0;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .template-title {
                font-size: 18px;
                font-weight: bold;
            }
            .template-description {
                color: #666;
                margin-bottom: 10px;
            }
            .template-labels {
                display: flex;
                gap: 5px;
                flex-wrap: wrap;
            }
            .label {
                padding: 2px 8px;
                background: #e3f2fd;
                border-radius: 4px;
                font-size: 12px;
            }
            .label.new {
                background: #4caf50;
                color: white;
            }
            .apply-btn {
                margin-top: 10px;
                padding: 8px 16px;
                background: #1877f2;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Rule Templates</h1>
                <div class="tabs">
                    <div class="tab active" onclick="filterTemplates('ECOMMERCE')">E-commerce</div>
                    <div class="tab" onclick="filterTemplates('LEAD')">Lead Generation</div>
                    <div class="tab" onclick="filterTemplates('BOTH')">Both</div>
                </div>
            </div>
            
            <div id="templates-container">
                <!-- Templates will be loaded here -->
            </div>
        </div>
        
        <script>
            let currentCampaignType = 'ECOMMERCE';
            
            async function loadTemplates(campaignType) {
                currentCampaignType = campaignType;
                const response = await fetch(`/api/templates/ui?campaign_type=${campaignType}`);
                const data = await response.json();
                
                const container = document.getElementById('templates-container');
                container.innerHTML = '';
                
                const categories = ['essential', 'pause', 'scale', 'optimise'];
                const categoryTitles = {
                    'essential': 'Essential',
                    'pause': 'Pause',
                    'scale': 'Scale',
                    'optimise': 'Optimise'
                };
                
                categories.forEach(category => {
                    const templates = data.templates[category] || [];
                    if (templates.length === 0) return;
                    
                    const section = document.createElement('div');
                    section.className = 'category-section';
                    section.innerHTML = `
                        <div class="category-title">${categoryTitles[category]}</div>
                        <div class="templates-grid">
                            ${templates.map(t => `
                                <div class="template-card" onclick="previewTemplate('${t.name}')">
                                    <div class="template-header">
                                        <div class="template-icon">${getIcon(t.icon)}</div>
                                        <div class="template-title">${t.name}</div>
                                    </div>
                                    <div class="template-description">${t.description}</div>
                                    <div class="template-labels">
                                        ${t.labels.map(l => `<span class="label ${l.toLowerCase().includes('new') ? 'new' : ''}">${l}</span>`).join('')}
                                    </div>
                                    <button class="apply-btn" onclick="event.stopPropagation(); applyTemplate('${t.name}')">Apply</button>
                                </div>
                            `).join('')}
                        </div>
                    `;
                    container.appendChild(section);
                });
            }
            
            function filterTemplates(campaignType) {
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                event.target.classList.add('active');
                loadTemplates(campaignType);
            }
            
            function getIcon(iconName) {
                const icons = {
                    'play': '▶',
                    'pause': '⏸',
                    'scale': '⚖',
                    'optimise': '⚡',
                    'notify': '🔔'
                };
                return icons[iconName] || '📋';
            }
            
            function previewTemplate(templateName) {
                // TODO: Show preview modal
                console.log('Preview:', templateName);
            }
            
            async function applyTemplate(templateName) {
                const accountId = prompt('Enter Account ID:');
                if (!accountId) return;
                
                const prefix = prompt('Enter Prefix (optional):') || '';
                
                const response = await fetch(`/api/templates/ui/${templateName}/apply`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        account_id: accountId,
                        prefix: prefix
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    alert('Template applied successfully!');
                } else {
                    alert('Error: ' + result.error);
                }
            }
            
            // Load templates on page load
            loadTemplates('ECOMMERCE');
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

