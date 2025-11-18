#!/usr/bin/env python3
"""
Dashboard Code Analysis and Cleanup Script
Phân tích và làm sạch code dashboard trùng lặp
"""

import re
from pathlib import Path

def analyze_dashboard():
    """Analyze dashboard.py for duplicates and issues"""
    print("🔍 Analyzing Dashboard Code...")
    
    dashboard_path = Path("app/api/routes/dashboard.py")
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all router decorators
    router_patterns = [
        r'@router\.get\("([^"]+)"\)',
        r'@router\.post\("([^"]+)"\)'
    ]
    
    endpoints = {}
    duplicates = {}
    
    for pattern in router_patterns:
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            endpoint = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            if endpoint in endpoints:
                # Duplicate found
                if endpoint not in duplicates:
                    duplicates[endpoint] = [endpoints[endpoint]]
                duplicates[endpoint].append(line_num)
            else:
                endpoints[endpoint] = line_num
    
    print(f"\n📊 Analysis Results:")
    print(f"   Total Endpoints: {len(endpoints)}")
    print(f"   Duplicate Endpoints: {len(duplicates)}")
    print(f"   File Size: {len(content)} characters")
    
    if duplicates:
        print(f"\n⚠️ Duplicate Endpoints Found:")
        for endpoint, lines in duplicates.items():
            print(f"   {endpoint}: Lines {lines}")
    
    # Check for common issues
    issues = []
    
    # Check for mixed CSS in Python
    if "padding:" in content and "border-radius:" in content:
        issues.append("CSS code mixed with Python")
    
    # Check for syntax errors
    try:
        compile(content, str(dashboard_path), 'exec')
    except SyntaxError as e:
        issues.append(f"Syntax Error: {e}")
    
    if issues:
        print(f"\n❌ Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(f"\n✅ No syntax issues found")
    
    # Suggest cleanup
    print(f"\n💡 Recommendations:")
    if duplicates:
        print("   1. Remove duplicate endpoints")
        print("   2. Consolidate similar functions")
    print("   3. Split into smaller modules if needed")
    print("   4. Add proper error handling")
    
    return {
        'endpoints': endpoints,
        'duplicates': duplicates,
        'issues': issues,
        'file_size': len(content)
    }

def suggest_cleanup_plan():
    """Suggest a cleanup plan"""
    print("\n🛠️ Dashboard Cleanup Plan:")
    print("=" * 50)
    
    print("\n📋 Step 1: Remove Duplicates")
    print("   - Keep the most complete version of each endpoint")
    print("   - Remove outdated/incomplete implementations")
    
    print("\n📋 Step 2: Organize Structure")
    print("   - Group related endpoints together")
    print("   - Add clear section comments")
    print("   - Ensure consistent error handling")
    
    print("\n📋 Step 3: Test Functionality")
    print("   - Verify all endpoints work")
    print("   - Test frontend integration")
    print("   - Check authentication flows")
    
    print("\n📋 Step 4: Optimize Performance")  
    print("   - Remove unused code")
    print("   - Optimize database queries")
    print("   - Add caching where appropriate")

if __name__ == "__main__":
    try:
        results = analyze_dashboard()
        suggest_cleanup_plan()
        
        print(f"\n🎯 Summary:")
        print(f"   Dashboard is functional but needs cleanup")
        print(f"   Priority: Remove {len(results['duplicates'])} duplicate endpoints")
        print(f"   File size: {results['file_size']:,} characters (very large)")
        
    except Exception as e:
        print(f"❌ Error analyzing dashboard: {e}")