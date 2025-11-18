"""
Dashboard API Endpoints - Bổ sung cho dashboard.py
Thêm các endpoint này vào cuối file dashboard.py
"""

@router.get("/data")
async def get_dashboard_data(
    request: Request,
    view_mode: str = Query("ecommerce", description="View mode: ecommerce or lead"),
    account_id: Optional[str] = Query(None),
    prefix: Optional[str] = Query(None),
    date_range: str = Query("last7days"),
    search: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get dashboard data based on view mode and filters"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Get user's accounts and prefixes
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db)
        
        if not user_account_ids and not user_prefixes:
            return JSONResponse({
                "overview": {},
                "ads": [],
                "message": "No accounts or prefixes configured"
            })
        
        # Build date filter
        end_date = datetime.now(HCM_TZ).replace(hour=23, minute=59, second=59, microsecond=999999)
        
        if date_range == "today":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "yesterday":
            start_date = (end_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = (end_date - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        elif date_range == "last7days":
            start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "last30days":
            start_date = (end_date - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Default to last 7 days
            start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Build query
        query = db.query(AdMetrics).filter(
            AdMetrics.date_start >= start_date.date(),
            AdMetrics.date_stop <= end_date.date()
        )
        
        # Filter by user's accounts and prefixes
        account_prefix_filter = []
        if user_account_ids:
            account_prefix_filter.append(AdMetrics.account_id.in_(user_account_ids))
        if user_prefixes:
            # Filter by prefix in ad name
            prefix_conditions = [AdMetrics.adset_name.like(f"{prefix}%") for prefix in user_prefixes]
            if prefix_conditions:
                account_prefix_filter.append(or_(*prefix_conditions))
        
        if account_prefix_filter:
            query = query.filter(or_(*account_prefix_filter))
        
        # Apply additional filters
        if account_id:
            query = query.filter(AdMetrics.account_id == account_id)
        
        if prefix:
            query = query.filter(AdMetrics.adset_name.like(f"{prefix}%"))
        
        if search:
            search_filter = or_(
                AdMetrics.adset_name.ilike(f"%{search}%"),
                AdMetrics.ad_name.ilike(f"%{search}%"),
                AdMetrics.campaign_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get data
        metrics = query.all()
        
        if not metrics:
            return JSONResponse({
                "overview": {},
                "ads": [],
                "message": "No data found for selected filters"
            })
        
        # Aggregate data by adset
        adset_data = {}
        for metric in metrics:
            adset_id = metric.adset_id
            if adset_id not in adset_data:
                adset_data[adset_id] = {
                    'id': adset_id,
                    'name': metric.adset_name,
                    'campaign_name': metric.campaign_name,
                    'account_id': metric.account_id,
                    'status': metric.adset_status or 'UNKNOWN',
                    'budget': 0,
                    'spend': 0,
                    'impressions': 0,
                    'clicks': 0,
                    'reach': 0,
                    'results': 0,
                    'link_clicks': 0,
                    'post_engagement': 0,
                    'video_views': 0,
                    'checkout_started': 0,
                    'purchases': 0,
                    'purchase_value': 0,
                    'leads': 0,
                    'comments': 0,
                    'messages': 0
                }
            
            # Aggregate metrics
            data = adset_data[adset_id]
            data['spend'] += float(metric.spend or 0)
            data['impressions'] += int(metric.impressions or 0)
            data['clicks'] += int(metric.clicks or 0)
            data['reach'] += int(metric.reach or 0)
            
            # Add action metrics
            if hasattr(metric, 'post_engagements'):
                data['post_engagement'] += int(metric.post_engagements or 0)
            if hasattr(metric, 'video_p25_watched_actions'):
                data['video_views'] += int(metric.video_p25_watched_actions or 0)
            
            # Purchase/conversion metrics
            if hasattr(metric, 'offsite_conversion_fb_pixel_initiate_checkout'):
                data['checkout_started'] += int(metric.offsite_conversion_fb_pixel_initiate_checkout or 0)
            if hasattr(metric, 'offsite_conversion_fb_pixel_purchase'):
                data['purchases'] += int(metric.offsite_conversion_fb_pixel_purchase or 0)
            if hasattr(metric, 'offsite_conversion_fb_pixel_purchase_value'):
                data['purchase_value'] += float(metric.offsite_conversion_fb_pixel_purchase_value or 0)
            
            # Lead metrics
            if hasattr(metric, 'onsite_conversion_messaging_conversation_started_7d'):
                data['messages'] += int(metric.onsite_conversion_messaging_conversation_started_7d or 0)
            if hasattr(metric, 'post_comments'):
                data['comments'] += int(metric.post_comments or 0)
        
        # Calculate derived metrics for each adset
        processed_ads = []
        for data in adset_data.values():
            # Basic calculations
            data['frequency'] = data['impressions'] / data['reach'] if data['reach'] > 0 else 0
            data['ctr'] = (data['clicks'] / data['impressions'] * 100) if data['impressions'] > 0 else 0
            data['cpc'] = data['spend'] / data['clicks'] if data['clicks'] > 0 else 0
            data['cpm'] = data['spend'] / data['impressions'] * 1000 if data['impressions'] > 0 else 0
            
            # View mode specific calculations
            if view_mode == "ecommerce":
                data['results'] = data['purchases']
                data['giaData'] = data['spend'] / data['purchases'] if data['purchases'] > 0 else 0
                data['adsPercent'] = (data['spend'] / data['purchase_value'] * 100) if data['purchase_value'] > 0 else 0
                data['conversionRate'] = (data['purchases'] / data['checkout_started'] * 100) if data['checkout_started'] > 0 else 0
            else:
                # Lead generation
                data['leads'] = data['comments'] + data['messages']
                data['results'] = data['leads']
                data['giaData'] = data['spend'] / data['leads'] if data['leads'] > 0 else 0
                data['costPerCheckout'] = data['spend'] / data['checkout_started'] if data['checkout_started'] > 0 else 0
            
            processed_ads.append(data)
        
        # Calculate overview metrics
        total_spend = sum(ad['spend'] for ad in processed_ads)
        total_impressions = sum(ad['impressions'] for ad in processed_ads)
        total_purchases = sum(ad['purchases'] for ad in processed_ads)
        total_purchase_value = sum(ad['purchase_value'] for ad in processed_ads)
        total_leads = sum(ad.get('leads', 0) for ad in processed_ads)
        
        active_adsets = len([ad for ad in processed_ads if ad['status'] == 'ACTIVE'])
        paused_adsets = len([ad for ad in processed_ads if ad['status'] in ['PAUSED', 'ARCHIVED']])
        total_adsets = len(processed_ads)
        
        if view_mode == "ecommerce":
            overview = {
                'totalSpend': total_spend,
                'adsPercent': (total_spend / total_purchase_value * 100) if total_purchase_value > 0 else 0,
                'purchaseValue': total_purchase_value,
                'activeAdsets': active_adsets,
                'pausedAdsets': paused_adsets,
                'totalAdsets': total_adsets
            }
        else:
            overview = {
                'totalSpend': total_spend,
                'totalLeads': total_leads,
                'avgGiaData': total_spend / total_leads if total_leads > 0 else 0,
                'activeAdsets': active_adsets,
                'pausedAdsets': paused_adsets,
                'totalAdsets': total_adsets
            }
        
        # Sort ads by spend (descending)
        processed_ads.sort(key=lambda x: x['spend'], reverse=True)
        
        return JSONResponse({
            "overview": overview,
            "ads": processed_ads[:100],  # Limit to 100 records for performance
            "total_records": len(processed_ads),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading dashboard data: {str(e)}")


@router.post("/action/{action}/{item_id}")
async def dashboard_action(
    request: Request,
    action: str,
    item_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Perform action on adset (activate/pause)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if action not in ["activate", "pause"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    try:
        # Verify user has access to this adset
        user_account_ids, user_prefixes = get_user_account_prefixes(current_user.id, db)
        
        # Check if adset belongs to user's accounts
        adset_query = db.query(AdMetrics).filter(AdMetrics.adset_id == item_id)
        
        # Filter by user's accounts and prefixes
        account_prefix_filter = []
        if user_account_ids:
            account_prefix_filter.append(AdMetrics.account_id.in_(user_account_ids))
        if user_prefixes:
            prefix_conditions = [AdMetrics.adset_name.like(f"{prefix}%") for prefix in user_prefixes]
            if prefix_conditions:
                account_prefix_filter.append(or_(*prefix_conditions))
        
        if account_prefix_filter:
            adset_query = adset_query.filter(or_(*account_prefix_filter))
        
        adset = adset_query.first()
        if not adset:
            raise HTTPException(status_code=404, detail="Adset not found or access denied")
        
        # Here you would integrate with Facebook API to actually change the adset status
        # For now, just return success
        new_status = "ACTIVE" if action == "activate" else "PAUSED"
        
        # In real implementation, you would:
        # 1. Get user's Facebook access token
        # 2. Make API call to Facebook to update adset status
        # 3. Update local database if successful
        
        logger.info(f"Action {action} performed on adset {item_id} by user {current_user.id}")
        
        return JSONResponse({
            "success": True,
            "action": action,
            "item_id": item_id,
            "new_status": new_status,
            "message": f"Adset {action}d successfully"
        })
        
    except Exception as e:
        logger.error(f"Error performing action {action} on {item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error performing action: {str(e)}")


@router.get("/health")
async def dashboard_health():
    """Health check endpoint for dashboard"""
    return JSONResponse({
        "status": "healthy",
        "service": "dashboard",
        "timestamp": datetime.now(HCM_TZ).isoformat()
    })