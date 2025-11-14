#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create an admin user
Usage: python scripts/create_admin_user.py
"""
import sys
import os
from getpass import getpass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db, get_db_session
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.exc import IntegrityError


def create_admin_user():
    """Create an admin user interactively"""
    print("=" * 60)
    print("Create Admin User")
    print("=" * 60)
    
    # Initialize database
    try:
        init_db()
        db = get_db_session()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
    
    try:
        # Get user input
        username = input("Username: ").strip()
        if not username:
            print("❌ Username cannot be empty")
            return False
        
        email = input("Email: ").strip()
        if not email:
            print("❌ Email cannot be empty")
            return False
        
        password = getpass("Password: ")
        if not password:
            print("❌ Password cannot be empty")
            return False
        
        password_confirm = getpass("Confirm Password: ")
        if password != password_confirm:
            print("❌ Passwords do not match")
            return False
        
        display_name = input("Display Name (optional, press Enter for default): ").strip()
        if not display_name:
            display_name = username
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"❌ User with username '{username}' or email '{email}' already exists")
            return False
        
        # Create new user
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            display_name=display_name,
            role="admin",
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("=" * 60)
        print("✅ Admin user created successfully!")
        print(f"   Username: {new_user.username}")
        print(f"   Email: {new_user.email}")
        print(f"   Display Name: {new_user.display_name}")
        print(f"   Role: {new_user.role}")
        print("=" * 60)
        
        return True
        
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Error: User already exists or database constraint violation")
        print(f"   Details: {e}")
        return False
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating user: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = create_admin_user()
    sys.exit(0 if success else 1)

