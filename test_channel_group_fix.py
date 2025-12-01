"""
Test script for Channel Group color_hex fix

Tests:
1. Migration runs successfully
2. Can create channel group with color_hex
3. Can create channel group without color_hex (uses default)
4. Database schema is correct
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db, get_db_session
from app.models.channels import ChannelGroup
from sqlalchemy import text
import uuid


def test_migration():
    """Test that migration runs successfully"""
    print("🧪 Test 1: Running migration...")
    
    try:
        from migrations.fix_channel_groups_color_column import run_migration
        run_migration()
        print("✅ Migration completed successfully\n")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}\n")
        return False


def test_schema():
    """Test database schema"""
    print("🧪 Test 2: Checking database schema...")
    
    init_db()
    db = get_db_session()
    
    try:
        # Check columns
        query = text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name='channel_groups' 
            AND column_name IN ('color', 'color_hex')
            ORDER BY column_name
        """)
        
        columns = db.execute(query).fetchall()
        
        print(f"   Found {len(columns)} color-related columns:")
        for col in columns:
            print(f"   - {col[0]}: {col[1]}, nullable={col[2]}, default={col[3]}")
        
        # Verify expectations
        has_color = any(col[0] == 'color' for col in columns)
        has_color_hex = any(col[0] == 'color_hex' for col in columns)
        
        if has_color:
            print("❌ Old 'color' column still exists!")
            return False
        
        if not has_color_hex:
            print("❌ 'color_hex' column doesn't exist!")
            return False
        
        # Check if color_hex is NOT NULL
        color_hex_col = next(col for col in columns if col[0] == 'color_hex')
        if color_hex_col[2] == 'YES':
            print("⚠️  Warning: 'color_hex' is nullable (should be NOT NULL)")
        
        print("✅ Schema is correct\n")
        return True
        
    except Exception as e:
        print(f"❌ Schema check failed: {e}\n")
        return False
    finally:
        db.close()


def test_create_with_color():
    """Test creating channel group with color_hex"""
    print("🧪 Test 3: Creating channel group with color_hex...")
    
    init_db()
    db = get_db_session()
    
    try:
        # Create test group with color
        group = ChannelGroup(
            id=str(uuid.uuid4()),
            user_id=1,  # Assuming user 1 exists
            name=f"Test Group With Color {uuid.uuid4().hex[:8]}",
            color_hex="#FF5733"
        )
        
        db.add(group)
        db.commit()
        db.refresh(group)
        
        print(f"   Created group: {group.name}")
        print(f"   Color: {group.color_hex}")
        
        # Verify
        if group.color_hex != "#FF5733":
            print(f"❌ Color mismatch! Expected #FF5733, got {group.color_hex}")
            return False
        
        # Clean up
        db.delete(group)
        db.commit()
        
        print("✅ Create with color_hex works\n")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Create with color failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_create_without_color():
    """Test creating channel group without color_hex (should use default)"""
    print("🧪 Test 4: Creating channel group without color_hex...")
    
    init_db()
    db = get_db_session()
    
    try:
        # Create test group without color (should use default from DB)
        group = ChannelGroup(
            id=str(uuid.uuid4()),
            user_id=1,
            name=f"Test Group No Color {uuid.uuid4().hex[:8]}"
            # No color_hex specified
        )
        
        db.add(group)
        db.commit()
        db.refresh(group)
        
        print(f"   Created group: {group.name}")
        print(f"   Color (should be default): {group.color_hex}")
        
        # Verify default was applied
        if not group.color_hex:
            print("❌ No default color applied!")
            return False
        
        if group.color_hex != "#3B82F6":
            print(f"⚠️  Warning: Default color is {group.color_hex}, expected #3B82F6")
        
        # Clean up
        db.delete(group)
        db.commit()
        
        print("✅ Create without color_hex works (default applied)\n")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Create without color failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_api_create():
    """Test creating via service layer"""
    print("🧪 Test 5: Creating via service layer...")
    
    init_db()
    db = get_db_session()
    
    try:
        from app.services.channels_service import ChannelsService
        from app.schemas.channels import ChannelGroupCreate
        
        service = ChannelsService(db, user_id=1)
        
        # Test 1: With color
        group_data = ChannelGroupCreate(
            name=f"Service Test With Color {uuid.uuid4().hex[:8]}",
            color_hex="#22C55E"
        )
        
        group1 = service.create_group(group_data)
        print(f"   Created via service (with color): {group1.name} - {group1.color_hex}")
        
        if group1.color_hex != "#22C55E":
            print(f"❌ Color mismatch! Expected #22C55E, got {group1.color_hex}")
            return False
        
        # Test 2: Without color (should use default)
        group_data2 = ChannelGroupCreate(
            name=f"Service Test No Color {uuid.uuid4().hex[:8]}"
            # No color_hex
        )
        
        group2 = service.create_group(group_data2)
        print(f"   Created via service (no color): {group2.name} - {group2.color_hex}")
        
        if group2.color_hex != "#3B82F6":
            print(f"⚠️  Warning: Default color is {group2.color_hex}, expected #3B82F6")
        
        # Clean up
        service.delete_group(group1.id)
        service.delete_group(group2.id)
        
        print("✅ Service layer works correctly\n")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Service layer test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """Run all tests"""
    print("=" * 60)
    print("CHANNEL GROUP COLOR_HEX FIX - TEST SUITE")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Migration", test_migration()))
    results.append(("Schema Check", test_schema()))
    results.append(("Create with color", test_create_with_color()))
    results.append(("Create without color", test_create_without_color()))
    results.append(("Service layer", test_api_create()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("🎉 All tests passed! Channel Group fix is working correctly.")
        print()
        print("Next steps:")
        print("1. Deploy migration to VPS: python -m migrations.fix_channel_groups_color_column")
        print("2. Test creating channel groups in UI")
        print("3. Verify no more 'color' column errors")
    else:
        print("❌ Some tests failed. Please review the errors above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
