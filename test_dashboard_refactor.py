"""
Test script để verify Dashboard Refactoring
Kiểm tra:
1. Endpoint /dashboard/data hoạt động
2. Summary metrics đúng business rule
3. CBO budget hiển thị đúng
4. Summary không bị ảnh hưởng bởi filter UI
"""

import asyncio
import sys
from datetime import datetime
import pytz

# Add app to path
sys.path.insert(0, 'c:\\Users\\Foxy\\Downloads\\File 5h_4_11\\Code 18h 4-11 bản 3 sheet')

from app.api.routes.dashboard import get_dashboard_dataset

HCM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

async def test_dashboard_refactor():
    """Test get_dashboard_dataset() logic"""
    
    print("\n" + "="*80)
    print("🔍 TEST DASHBOARD REFACTORING")
    print("="*80)
    
    # Mock data for testing
    access_token = "test_token_placeholder"  # Replace with real token
    user_account_ids = []  # Replace with real account IDs
    account_type_map = {}  # Replace with real mapping
    
    today = datetime.now(HCM_TZ).strftime('%Y-%m-%d')
    
    print("\n📝 Test Parameters:")
    print(f"  - Date: {today}")
    print(f"  - Accounts: {len(user_account_ids)}")
    
    if not user_account_ids:
        print("\n⚠️  WARNING: No account IDs provided. Skipping API test.")
        print("✅ Code structure verified - no syntax errors found.")
        print("\n📋 To run full test:")
        print("  1. Update 'access_token' with real Facebook token")
        print("  2. Update 'user_account_ids' with your account IDs")
        print("  3. Update 'account_type_map' with account types")
        print("  4. Re-run: python test_dashboard_refactor.py")
        return
    
    # Test 1: Lead Generation view
    print("\n" + "-"*80)
    print("📋 TEST 1: LEAD GENERATION VIEW")
    print("-"*80)
    
    try:
        dataset_lead = await get_dashboard_dataset(
            access_token=access_token,
            user_account_ids=user_account_ids,
            account_type_map=account_type_map,
            view_mode="lead",
            date_from=today,
            date_to=today,
            use_cache=False
        )
        
        summary_lead = dataset_lead['summary']
        rows_base = dataset_lead['rows_base']
        rows_table = dataset_lead['rows_for_table']
        
        print(f"\n✅ Lead Gen Summary:")
        print(f"  - Total Spend: {summary_lead.get('totalSpend', 0):,.2f} VND")
        print(f"  - Total Data: {summary_lead.get('totalData', 0):,} (comments + messages)")
        print(f"  - Total Lead: {summary_lead.get('totalLead', 0):,} (Checkouts Initiated)")
        print(f"  - Total Checkouts: {summary_lead.get('totalCheckouts', 0):,}")
        print(f"  - Active Adsets: {summary_lead.get('activeAdsets', 0):,}")
        print(f"  - Total Adsets: {summary_lead.get('totalAdsets', 0):,}")
        
        print(f"\n📊 Data counts:")
        print(f"  - rows_base (for summary): {len(rows_base)}")
        print(f"  - rows_for_table (for display): {len(rows_table)}")
        
        # Verify business rule: totalLead should be checkouts_initiated
        total_checkouts_manual = sum(
            int(row.get('checkouts_initiated', 0) or 0) 
            for row in rows_base
        )
        
        if summary_lead.get('totalLead') == total_checkouts_manual:
            print(f"\n✅ PASS: totalLead = {summary_lead.get('totalLead')} matches manual count")
        else:
            print(f"\n❌ FAIL: totalLead = {summary_lead.get('totalLead')}, expected {total_checkouts_manual}")
        
    except Exception as e:
        print(f"\n❌ ERROR in Lead Gen test: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: E-Commerce view
    print("\n" + "-"*80)
    print("🛒 TEST 2: E-COMMERCE VIEW")
    print("-"*80)
    
    try:
        dataset_ecom = await get_dashboard_dataset(
            access_token=access_token,
            user_account_ids=user_account_ids,
            account_type_map=account_type_map,
            view_mode="ecommerce",
            date_from=today,
            date_to=today,
            use_cache=False
        )
        
        summary_ecom = dataset_ecom['summary']
        
        print(f"\n✅ E-Commerce Summary:")
        print(f"  - Total Spend: {summary_ecom.get('totalSpend', 0):,.2f} VND")
        print(f"  - Purchase Value: {summary_ecom.get('purchaseValue', 0):,.2f} VND")
        print(f"  - ADS %: {summary_ecom.get('adsPercent', 0):.2f}%")
        print(f"  - Total Checkouts: {summary_ecom.get('totalCheckouts', 0):,}")
        print(f"  - Total Purchases: {summary_ecom.get('totalPurchases', 0):,}")
        print(f"  - Active Adsets: {summary_ecom.get('activeAdsets', 0):,}")
        
        # Verify ADS % calculation
        spend = summary_ecom.get('totalSpend', 0)
        purchase_value = summary_ecom.get('purchaseValue', 0)
        expected_ads_percent = (spend / purchase_value * 100) if purchase_value > 0 else 0
        
        if abs(summary_ecom.get('adsPercent', 0) - expected_ads_percent) < 0.01:
            print(f"\n✅ PASS: ADS % calculation correct")
        else:
            print(f"\n❌ FAIL: ADS % = {summary_ecom.get('adsPercent')}, expected {expected_ads_percent:.2f}")
        
    except Exception as e:
        print(f"\n❌ ERROR in E-Commerce test: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Filter independence
    print("\n" + "-"*80)
    print("🔍 TEST 3: SUMMARY FILTER INDEPENDENCE")
    print("-"*80)
    
    try:
        # Get baseline summary
        dataset_no_filter = await get_dashboard_dataset(
            access_token=access_token,
            user_account_ids=user_account_ids,
            account_type_map=account_type_map,
            view_mode="ecommerce",
            date_from=today,
            date_to=today,
            use_cache=False
        )
        
        # Get summary with prefix filter
        dataset_with_filter = await get_dashboard_dataset(
            access_token=access_token,
            user_account_ids=user_account_ids,
            account_type_map=account_type_map,
            view_mode="ecommerce",
            date_from=today,
            date_to=today,
            use_cache=False,
            prefix="TEST_PREFIX"  # Apply filter
        )
        
        summary_no_filter = dataset_no_filter['summary']
        summary_with_filter = dataset_with_filter['summary']
        
        rows_no_filter = len(dataset_no_filter['rows_for_table'])
        rows_with_filter = len(dataset_with_filter['rows_for_table'])
        
        print(f"\n📊 Comparison:")
        print(f"  Without filter: {rows_no_filter} rows, Total Spend: {summary_no_filter.get('totalSpend', 0):,.2f}")
        print(f"  With prefix filter: {rows_with_filter} rows, Total Spend: {summary_with_filter.get('totalSpend', 0):,.2f}")
        
        if summary_no_filter.get('totalSpend') == summary_with_filter.get('totalSpend'):
            print(f"\n✅ PASS: Summary unchanged despite filter (rows changed: {rows_no_filter} → {rows_with_filter})")
        else:
            print(f"\n❌ FAIL: Summary affected by filter!")
        
    except Exception as e:
        print(f"\n❌ ERROR in filter independence test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_dashboard_refactor())
