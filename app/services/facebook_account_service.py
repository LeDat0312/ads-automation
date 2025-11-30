"""
Facebook Account Service Layer
Business logic for managing Facebook Accounts (Via tokens)
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException
import logging
from datetime import datetime

from app.models.facebook_account import FacebookAccount, FacebookAccountType
from app.schemas.facebook_account import FacebookAccountCreate, FacebookAccountUpdate

logger = logging.getLogger(__name__)


class FacebookAccountService:
    """Service for managing Facebook Accounts"""
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def list_accounts(
        self,
        token_type: Optional[FacebookAccountType] = None,
        is_active: Optional[bool] = None
    ) -> List[FacebookAccount]:
        """List Facebook accounts for current user"""
        query = self.db.query(FacebookAccount).filter(
            FacebookAccount.user_id == self.user_id
        )
        
        if token_type:
            # If looking for fanpage, include both fanpage and both
            if token_type == FacebookAccountType.FANPAGE:
                query = query.filter(
                    FacebookAccount.token_type.in_([
                        FacebookAccountType.FANPAGE,
                        FacebookAccountType.BOTH
                    ])
                )
            # If looking for ads, include both ads and both
            elif token_type == FacebookAccountType.ADS:
                query = query.filter(
                    FacebookAccount.token_type.in_([
                        FacebookAccountType.ADS,
                        FacebookAccountType.BOTH
                    ])
                )
            else:
                query = query.filter(FacebookAccount.token_type == token_type)
        
        if is_active is not None:
            query = query.filter(FacebookAccount.is_active == is_active)
        
        return query.order_by(FacebookAccount.name).all()
    
    def get_account(self, account_id: int) -> Optional[FacebookAccount]:
        """Get Facebook account by ID (must belong to current user)"""
        return self.db.query(FacebookAccount).filter(
            and_(
                FacebookAccount.id == account_id,
                FacebookAccount.user_id == self.user_id
            )
        ).first()
    
    def create_account(self, account_data: FacebookAccountCreate) -> FacebookAccount:
        """Create a new Facebook account"""
        try:
            # TODO: Encrypt access_token before storing
            # For now, store as-is (should use encrypt_token from security module)
            
            account = FacebookAccount(
                user_id=self.user_id,
                name=account_data.name,
                access_token=account_data.access_token,
                token_type=account_data.token_type,
                facebook_user_id=account_data.facebook_user_id,
                facebook_user_name=account_data.facebook_user_name,
                expires_at=account_data.expires_at,
                is_active=True
            )
            
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
            
            logger.info(f"✅ Created Facebook account: {account.name} (ID: {account.id})")
            return account
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creating Facebook account: {e}")
            raise
    
    def update_account(
        self,
        account_id: int,
        account_data: FacebookAccountUpdate
    ) -> FacebookAccount:
        """Update a Facebook account"""
        account = self.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản Facebook")
        
        try:
            update_data = account_data.dict(exclude_unset=True)
            
            # TODO: Encrypt access_token if being updated
            
            for field, value in update_data.items():
                setattr(account, field, value)
            
            account.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(account)
            
            logger.info(f"✅ Updated Facebook account: {account.name} (ID: {account.id})")
            return account
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error updating Facebook account: {e}")
            raise
    
    def delete_account(self, account_id: int) -> bool:
        """Delete a Facebook account"""
        account = self.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản Facebook")
        
        try:
            self.db.delete(account)
            self.db.commit()
            logger.info(f"✅ Deleted Facebook account: {account_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error deleting Facebook account: {e}")
            raise
    
    def verify_token(self, account_id: int) -> dict:
        """Verify Facebook account token by calling Graph API"""
        account = self.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản Facebook")
        
        import httpx
        from app.core.config import get_settings
        
        settings = get_settings()
        
        try:
            # Verify token with Graph API
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/me",
                    params={
                        "access_token": account.access_token,
                        "fields": "id,name"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Update account info
                    account.facebook_user_id = data.get("id")
                    account.facebook_user_name = data.get("name")
                    account.last_verified_at = datetime.utcnow()
                    self.db.commit()
                    
                    logger.info(f"✅ Verified Facebook account: {account.name}")
                    return {
                        "valid": True,
                        "user_id": data.get("id"),
                        "user_name": data.get("name")
                    }
                else:
                    logger.error(f"❌ Token verification failed: {response.text}")
                    return {
                        "valid": False,
                        "error": "Token không hợp lệ hoặc đã hết hạn"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Error verifying token: {e}")
            return {
                "valid": False,
                "error": str(e)
            }


def get_facebook_account_service(db: Session, user_id: int) -> FacebookAccountService:
    """Dependency to get FacebookAccountService instance"""
    return FacebookAccountService(db, user_id)
