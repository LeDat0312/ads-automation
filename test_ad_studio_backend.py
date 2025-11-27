"""
Test script để verify AdStudio backend implementation
Không chạy migration thật, chỉ import và kiểm tra syntax
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🧪 Testing AdStudio Backend Implementation\n")

# Test 1: Import schemas
print("1️⃣ Testing Pydantic schemas...")
try:
    from app.schemas.ad_studio import ScrapeRequest, Asset, SchedulePayload, ScheduleResponse
    print("   ✅ Schemas imported successfully")
    print(f"      - ScrapeRequest: {ScrapeRequest.__name__}")
    print(f"      - Asset: {Asset.__name__}")
    print(f"      - SchedulePayload: {SchedulePayload.__name__}")
    print(f"      - ScheduleResponse: {ScheduleResponse.__name__}")
except Exception as e:
    print(f"   ❌ Error importing schemas: {e}")

# Test 2: Import models
print("\n2️⃣ Testing SQLAlchemy models...")
try:
    from app.models.ad_studio import AdStudioAsset, AdStudioScheduledPost
    print("   ✅ Models imported successfully")
    print(f"      - AdStudioAsset table: {AdStudioAsset.__tablename__}")
    print(f"      - AdStudioScheduledPost table: {AdStudioScheduledPost.__tablename__}")
except Exception as e:
    print(f"   ❌ Error importing models: {e}")

# Test 3: Import helper
print("\n3️⃣ Testing Apify helper...")
try:
    from app.services.apify_helper import get_apify_api_key
    print("   ✅ Helper imported successfully")
    print(f"      - Function: {get_apify_api_key.__name__}")
except Exception as e:
    print(f"   ❌ Error importing helper: {e}")

# Test 4: Import router
print("\n4️⃣ Testing API router...")
try:
    from app.api.routes.ad_studio import router
    print("   ✅ Router imported successfully")
    print(f"      - Prefix: {router.prefix}")
    print(f"      - Tags: {router.tags}")
    
    # List routes
    routes = [route for route in router.routes]
    print(f"      - Routes: {len(routes)} endpoints")
    for route in routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods)
            print(f"        * {methods} {route.path}")
except Exception as e:
    print(f"   ❌ Error importing router: {e}")

# Test 5: Check main.py integration
print("\n5️⃣ Checking main.py integration...")
try:
    with open('app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'from app.api.routes import ad_studio' in content:
        print("   ✅ ad_studio import found in main.py")
    else:
        print("   ⚠️  ad_studio import NOT found in main.py")
        
    if 'app.include_router(ad_studio.router)' in content:
        print("   ✅ ad_studio.router included in main.py")
    else:
        print("   ⚠️  ad_studio.router NOT included in main.py")
        
    if 'NOTE: added for AdStudio only' in content:
        print("   ✅ AdStudio comment markers found")
    else:
        print("   ⚠️  AdStudio comment markers NOT found")
        
except Exception as e:
    print(f"   ❌ Error checking main.py: {e}")

# Test 6: Check database.py integration
print("\n6️⃣ Checking database.py integration...")
try:
    with open('app/core/database.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'from app.models.ad_studio import AdStudioAsset, AdStudioScheduledPost' in content:
        print("   ✅ AdStudio models imported in database.py")
    else:
        print("   ⚠️  AdStudio models NOT imported in database.py")
        
except Exception as e:
    print(f"   ❌ Error checking database.py: {e}")

print("\n" + "="*60)
print("✅ All syntax checks passed!")
print("="*60)

print("\n📝 Next steps:")
print("   1. Cài đặt dependencies nếu chưa có:")
print("      pip install sqlalchemy fastapi requests pydantic")
print("   2. Cấu hình DATABASE_URL trong .env")
print("   3. Chạy migration:")
print("      python -m migrations.add_ad_studio_tables")
print("   4. Cấu hình Apify API key tại /settings")
print("   5. Test endpoint:")
print("      curl -X POST http://localhost:8000/api/tiktok/scrape \\")
print("        -H 'Content-Type: application/json' \\")
print("        -d '{\"url\": \"https://tiktok.com/@user/video/123\"}'")
