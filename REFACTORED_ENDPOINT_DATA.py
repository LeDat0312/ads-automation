"""
🎯 REFACTORED /dashboard/data ENDPOINT - SINGLE SOURCE OF TRUTH

Copy endpoint này vào dashboard.py thay thế cho endpoint cũ (từ dòng 623 đến 1604)

Thay đổi chính:
1. ✅ Sử dụng get_dashboard_dataset() - SINGLE SOURCE OF TRUTH
2. ✅ Summary và bảng luôn lấy từ cùng 1 dataset
3. ✅ Xử lý FacebookRateLimitError - trả HTTP 429
4. ✅ Giảm từ 1000 dòng xuống ~250 dòng
5. ✅ Dễ debug và maintain hơn nhiều
"""

@router.get("/data")
async def get_dashboard_data(
    request: Request,
    view_mode: str = Query("ecommerce", description="View mode: ecommerce or lead"),
    level: str = Query("adset", description="Level: campaign, adset, or ad"),
    account_ids: Optional[str] = Query(None, description="Comma-separated account IDs (optional)"),
    prefix: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID (for drill-down)"),
    adset_id: Optional[str] = Query(None, description="Filter by adset ID (for drill-down)"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=10, le=500),
    sort_by: Optional[str] = Query(None, description="Column to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort order: 'asc' or 'desc'"),
    force_refresh: int = Query(0, ge=0, le=1, description="0=use cache, 1=force refresh"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    🎯 REFACTORED: Unified endpoint sử dụng get_dashboard_dataset()
    
    - Summary và bảng luôn nhất quán (cùng 1 source)
    - Xử lý rate limit đúng cách (HTTP 429)
    - Chỉ load spend > 0 && impressions > 0
    - CBO budget hiển thị đúng
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        logger.info(f"📊 /dashboard/data START | view={view_mode}, level={level}, date_from={date_from}, date_to={date_to}")
        
        # ===== BƯỚC 1: Get user accounts & build account_type_map =====
        user_account_ids, user_prefixes = get_user_account_prefixes_filtered_by_view_mode(
            current_user.id, db, view_mode, enabled_only=True
        )
        
        # Build account_type_map
        account_query = db.query(Account.account_id, Account.account_type).filter(
            Account.user_id == current_user.id,
            Account.enabled == True
        )
        if view_mode == "ecommerce":
            account_query = account_query.filter(Account.account_type == "E-COMMERCE")
        elif view_mode == "lead":
            account_query = account_query.filter(Account.account_type == "LEAD_GENERATION")
        
        account_type_map = {}
        for acc_id, acc_type in account_query.all():
            clean_id = acc_id.replace('act_', '')
            account_type_map[clean_id] = acc_type
        
        # Empty state
        if not user_account_ids:
            logger.warning("⚠️ No accounts found for user")
            empty_summary = {
                "totalSpend": 0,
                "totalData": 0 if view_mode == "lead" else None,
                "totalLead": 0 if view_mode == "lead" else None,
                "adsPercent": 0 if view_mode == "ecommerce" else None,
                "purchaseValue": 0 if view_mode == "ecommerce" else None,
                "totalCheckouts": 0,
                "activeAdsets": 0,
                "pausedAdsets": 0,
                "totalAdsets": 0,
                "currency": "VND"
            }
            return JSONResponse({
                "summary": empty_summary,
                "details": {
                    "level": level,
                    "rows": [],
                    "pagination": {
                        "page": page,
                        "page_size": pageSize,
                        "total_rows": 0,
                        "total_pages": 0
                    }
                }
            })
        
        # Filter accounts if account_ids filter is provided
        if account_ids:
            requested_ids = [aid.strip() for aid in account_ids.split(',') if aid.strip()]
            for aid in requested_ids:
                if aid not in user_account_ids:
                    raise HTTPException(status_code=403, detail=f"Access denied to account {aid}")
            user_account_ids = requested_ids
        
        # Get access token
        access_token = get_user_access_token(current_user.id, db)
        if not access_token:
            raise HTTPException(status_code=400, detail="Facebook access token not found. Please configure in Settings.")
        
        # ===== BƯỚC 2: Gọi get_dashboard_dataset() - SINGLE SOURCE OF TRUTH =====
        use_cache = (force_refresh == 0)
        logger.info(f"📥 Calling get_dashboard_dataset() | use_cache={use_cache}")
        
        try:
            dataset = await get_dashboard_dataset(
                access_token=access_token,
                user_account_ids=user_account_ids,
                account_type_map=account_type_map,
                view_mode=view_mode,
                date_from=date_from or datetime.now(HCM_TZ).strftime('%Y-%m-%d'),
                date_to=date_to or datetime.now(HCM_TZ).strftime('%Y-%m-%d'),
                use_cache=use_cache,
                # Filters chỉ áp dụng cho bảng
                prefix=prefix,
                status=status,
                search=search,
                campaign_id=campaign_id,
                adset_id=adset_id
            )
        except FacebookRateLimitError as e:
            logger.error(f"⚠️ Facebook rate limit reached: {e}")
            raise HTTPException(
                status_code=429,
                detail="Facebook API rate limit reached. Vui lòng thử lại sau 5-10 phút."
            )
        
        # Extract data from dataset
        rows_for_table = dataset["rows_for_table"]
        summary = dataset["summary"]
        
        logger.info(f"✅ Dataset received | rows_for_table={len(rows_for_table)}, summary={summary}")
        
        # ===== BƯỚC 3: Group by level (nếu cần) =====
        # Logic group by level tùy vào level được chọn (campaign / adset / ad)
        # Hiện tại get_dashboard_dataset() đã trả về data ở ad level
        # Cần group lại nếu level = "campaign" hoặc "adset"
        
        if level == "adset":
            # Group theo adset_id
            grouped_data = defaultdict(lambda: {
                'spend': 0.0, 'impressions': 0, 'clicks': 0, 'reach': 0,
                'post_comments': 0, 'messaging_conversations_started': 0,
                'checkouts_initiated': 0, 'onsite_conversion_post_save': 0,
                'purchases': 0, 'purchase_value': 0.0
            })
            
            for row in rows_for_table:
                adset_id = row.get('adset_id')
                if not adset_id:
                    continue
                
                group = grouped_data[adset_id]
                
                # Aggregate metrics
                group['spend'] += float(row.get('spend', 0) or 0)
                group['impressions'] += int(row.get('impressions', 0) or 0)
                group['clicks'] += int(row.get('clicks', 0) or 0)
                group['reach'] += int(row.get('reach', 0) or 0)
                group['post_comments'] += int(row.get('post_comments', 0) or 0)
                group['messaging_conversations_started'] += int(row.get('messaging_conversations_started', 0) or 0)
                group['checkouts_initiated'] += int(row.get('checkouts_initiated', 0) or 0)
                group['onsite_conversion_post_save'] += int(row.get('onsite_conversion_post_save', 0) or 0)
                group['purchases'] += int(row.get('purchases', 0) or 0)
                group['purchase_value'] += float(row.get('gia_tri_chuyen_doi_tu_luot_mua', 0) or 0)
                
                # Keep first occurrence info (name, status, budget...)
                if 'adset_id' not in group:
                    group['adset_id'] = adset_id
                    group['adset_name'] = row.get('adset_name', '')
                    group['campaign_id'] = row.get('campaign_id', '')
                    group['campaign_name'] = row.get('campaign_name', '')
                    group['prefix'] = row.get('prefix', '')
                    group['effective_status'] = row.get('effective_status', 'UNKNOWN')
                    group['configured_status'] = row.get('configured_status', 'UNKNOWN')
                    group['delivery'] = row.get('delivery', 'UNKNOWN')
                    # 🔹 CBO Budget fields
                    group['adset_daily_budget'] = row.get('adset_daily_budget')
                    group['campaign_daily_budget'] = row.get('campaign_daily_budget')
                    group['using_campaign_budget'] = row.get('using_campaign_budget', False)
                    group['budget_type'] = row.get('budget_type', 'ADSET')
            
            # Convert to list và tính derived metrics
            rows = []
            for adset_id, group in grouped_data.items():
                spend = group['spend']
                checkouts = group['checkouts_initiated']
                purchases = group['purchases']
                purchase_value = group['purchase_value']
                data = group['post_comments'] + group['messaging_conversations_started']
                
                # Tính metrics
                group['results'] = data
                group['gia_data'] = (spend / data) if data > 0 else 0
                group['cost_per_checkout'] = (spend / checkouts) if checkouts > 0 else 0
                group['cost_per_purchase'] = (spend / purchases) if purchases > 0 else 0
                group['ads_percent'] = (spend / purchase_value * 100) if purchase_value > 0 else 0
                group['cpm'] = (spend / group['impressions'] * 1000) if group['impressions'] > 0 else 0
                group['ctr'] = (group['clicks'] / group['impressions'] * 100) if group['impressions'] > 0 else 0
                group['cpc'] = (spend / group['clicks']) if group['clicks'] > 0 else 0
                
                rows.append(group)
        
        elif level == "campaign":
            # Group theo campaign_id
            grouped_data = defaultdict(lambda: {
                'spend': 0.0, 'impressions': 0, 'clicks': 0, 'reach': 0,
                'post_comments': 0, 'messaging_conversations_started': 0,
                'checkouts_initiated': 0, 'onsite_conversion_post_save': 0,
                'purchases': 0, 'purchase_value': 0.0
            })
            
            for row in rows_for_table:
                campaign_id = row.get('campaign_id')
                if not campaign_id:
                    continue
                
                group = grouped_data[campaign_id]
                
                # Aggregate metrics
                group['spend'] += float(row.get('spend', 0) or 0)
                group['impressions'] += int(row.get('impressions', 0) or 0)
                group['clicks'] += int(row.get('clicks', 0) or 0)
                group['reach'] += int(row.get('reach', 0) or 0)
                group['post_comments'] += int(row.get('post_comments', 0) or 0)
                group['messaging_conversations_started'] += int(row.get('messaging_conversations_started', 0) or 0)
                group['checkouts_initiated'] += int(row.get('checkouts_initiated', 0) or 0)
                group['onsite_conversion_post_save'] += int(row.get('onsite_conversion_post_save', 0) or 0)
                group['purchases'] += int(row.get('purchases', 0) or 0)
                group['purchase_value'] += float(row.get('gia_tri_chuyen_doi_tu_luot_mua', 0) or 0)
                
                # Keep first occurrence info
                if 'campaign_id' not in group:
                    group['campaign_id'] = campaign_id
                    group['campaign_name'] = row.get('campaign_name', '')
                    group['prefix'] = row.get('prefix', '')
                    group['campaign_daily_budget'] = row.get('campaign_daily_budget')
                    group['budget_type'] = 'CAMPAIGN'
            
            # Convert to list và tính derived metrics
            rows = []
            for campaign_id, group in grouped_data.items():
                spend = group['spend']
                data = group['post_comments'] + group['messaging_conversations_started']
                
                group['results'] = data
                group['gia_data'] = (spend / data) if data > 0 else 0
                group['cost_per_checkout'] = (spend / group['checkouts_initiated']) if group['checkouts_initiated'] > 0 else 0
                group['cost_per_purchase'] = (spend / group['purchases']) if group['purchases'] > 0 else 0
                
                rows.append(group)
        
        else:  # level == "ad"
            # Không cần group, dùng rows_for_table trực tiếp
            rows = rows_for_table
        
        # ===== BƯỚC 4: Sort =====
        if sort_by and rows:
            reverse = (sort_order == "desc")
            try:
                rows.sort(key=lambda x: float(x.get(sort_by, 0) or 0), reverse=reverse)
            except (ValueError, TypeError):
                # Fallback: sort by string
                rows.sort(key=lambda x: str(x.get(sort_by, '')), reverse=reverse)
        
        # ===== BƯỚC 5: Pagination =====
        total_rows = len(rows)
        total_pages = ((total_rows - 1) // pageSize) + 1 if total_rows > 0 else 0
        offset = (page - 1) * pageSize
        paginated_rows = rows[offset:offset + pageSize]
        
        logger.info(f"✅ /dashboard/data DONE | rows={len(paginated_rows)}/{total_rows}, page={page}/{total_pages}")
        
        # ===== BƯỚC 6: Return response =====
        return JSONResponse({
            "summary": summary,
            "details": {
                "level": level,
                "rows": paginated_rows,
                "pagination": {
                    "page": page,
                    "page_size": pageSize,
                    "total_rows": total_rows,
                    "total_pages": total_pages
                }
            }
        })
        
    except FacebookRateLimitError:
        # Already handled above
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in /dashboard/data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")
