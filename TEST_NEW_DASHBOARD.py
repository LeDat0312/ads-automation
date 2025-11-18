#!/usr/bin/env python3
"""
Test script cho New Dashboard Implementation
Kiểm tra syntax, imports và API endpoints
"""

import sys
import os
import importlib.util
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dashboard_syntax():
    """Test dashboard.py syntax"""
    logger.info("🔍 Testing dashboard.py syntax...")
    
    try:
        dashboard_path = Path(__file__).parent / "app" / "api" / "routes" / "dashboard.py"
        
        # Read file content
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to compile
        compile(content, str(dashboard_path), 'exec')
        logger.info("✅ Dashboard syntax is valid")
        return True
        
    except SyntaxError as e:
        logger.error(f"❌ Syntax Error in dashboard.py: {e}")
        logger.error(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing syntax: {e}")
        return False

def test_dashboard_imports():
    """Test dashboard imports"""
    logger.info("🔍 Testing dashboard imports...")
    
    try:
        # Add app directory to path
        app_path = Path(__file__).parent
        if str(app_path) not in sys.path:
            sys.path.insert(0, str(app_path))
        
        # Try importing dashboard module
        spec = importlib.util.spec_from_file_location(
            "dashboard", 
            Path(__file__).parent / "app" / "api" / "routes" / "dashboard.py"
        )
        dashboard_module = importlib.util.module_from_spec(spec)
        
        # Mock required modules if not available
        import types
        
        # Mock FastAPI components
        sys.modules['fastapi'] = types.ModuleType('fastapi')
        sys.modules['fastapi.responses'] = types.ModuleType('fastapi.responses')
        sys.modules['sqlalchemy'] = types.ModuleType('sqlalchemy')
        sys.modules['sqlalchemy.orm'] = types.ModuleType('sqlalchemy.orm')
        
        # Mock app modules
        sys.modules['app'] = types.ModuleType('app')
        sys.modules['app.core'] = types.ModuleType('app.core')
        sys.modules['app.core.database'] = types.ModuleType('app.core.database')
        sys.modules['app.models'] = types.ModuleType('app.models')
        sys.modules['app.api'] = types.ModuleType('app.api')
        sys.modules['app.api.routes'] = types.ModuleType('app.api.routes')
        
        # Execute module
        spec.loader.exec_module(dashboard_module)
        logger.info("✅ Dashboard imports successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Import error: {e}")
        return False

def check_api_endpoints():
    """Check API endpoints structure"""
    logger.info("🔍 Checking API endpoints...")
    
    try:
        dashboard_path = Path(__file__).parent / "app" / "api" / "routes" / "dashboard.py"
        
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required endpoints
        required_endpoints = [
            '@router.get("/")',
            '@router.get("/filters")',
            '@router.get("/settings-status")',
            '@router.get("/data")',
            '@router.post("/action/{action}/{item_id}")',
            '@router.get("/health")'
        ]
        
        missing_endpoints = []
        for endpoint in required_endpoints:
            if endpoint not in content:
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            logger.error(f"❌ Missing endpoints: {missing_endpoints}")
            return False
        
        logger.info("✅ All required endpoints found")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking endpoints: {e}")
        return False

def check_html_structure():
    """Check HTML structure"""
    logger.info("🔍 Checking HTML structure...")
    
    try:
        dashboard_path = Path(__file__).parent / "app" / "api" / "routes" / "dashboard.py"
        
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key HTML elements
        html_elements = [
            'class="header"',
            'class="control-panel"',
            'class="overview-grid"',
            'class="table-container"',
            'id="overviewGrid"',
            'id="dataTable"',
            'switchViewMode',
            'loadData()',
            'refreshData()'
        ]
        
        missing_elements = []
        for element in html_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            logger.error(f"❌ Missing HTML elements: {missing_elements}")
            return False
        
        logger.info("✅ HTML structure is complete")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking HTML: {e}")
        return False

def check_javascript_functions():
    """Check JavaScript functions"""
    logger.info("🔍 Checking JavaScript functions...")
    
    try:
        dashboard_path = Path(__file__).parent / "app" / "api" / "routes" / "dashboard.py"
        
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key JavaScript functions
        js_functions = [
            'function switchViewMode(',
            'function updateFilters(',
            'function refreshData(',
            'function loadData(',
            'function toggleSelection(',
            'function bulkAction(',
            'function saveFilters(',
            'function loadSavedFilters(',
            'function checkSettingsStatus(',
            'function updateOverviewCards(',
            'function updateTable('
        ]
        
        missing_functions = []
        for func in js_functions:
            if func not in content:
                missing_functions.append(func)
        
        if missing_functions:
            logger.error(f"❌ Missing JS functions: {missing_functions}")
            return False
        
        logger.info("✅ JavaScript functions are complete")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking JavaScript: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting New Dashboard Tests...")
    logger.info("=" * 60)
    
    tests = [
        ("Syntax Check", test_dashboard_syntax),
        ("Import Check", test_dashboard_imports),
        ("API Endpoints", check_api_endpoints),
        ("HTML Structure", check_html_structure),
        ("JavaScript Functions", check_javascript_functions)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"❌ Test {test_name} crashed: {e}")
            failed += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 Test Results:")
    logger.info(f"   ✅ Passed: {passed}")
    logger.info(f"   ❌ Failed: {failed}")
    logger.info(f"   📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        logger.info("\n🎉 ALL TESTS PASSED! Dashboard is ready!")
        print("\n🚀 Next Steps:")
        print("1. Run the emergency fix script on VPS")
        print("2. Test dashboard in browser")
        print("3. Configure settings if not done")
        print("4. Verify data loading and filters")
    else:
        logger.error(f"\n⚠️ {failed} tests failed. Please fix issues before deployment.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)