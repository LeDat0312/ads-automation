"""
Facebook Service Layer
Handle Facebook Graph API operations for OAuth and Pages
"""
from typing import List, Dict, Any, Optional
import httpx
import logging
from pydantic import BaseModel

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class FacebookTokenData(BaseModel):
    """Response from Facebook OAuth token exchange"""
    access_token: str
    token_type: str
    expires_in: Optional[int] = None


class FacebookPage(BaseModel):
    """Facebook Page data from /me/accounts"""
    id: str
    name: str
    access_token: str
    category: Optional[str] = None
    tasks: Optional[List[str]] = None


class FacebookUser(BaseModel):
    """Facebook User data from /me"""
    id: str
    name: str
    email: Optional[str] = None


class FacebookService:
    """Service for Facebook Graph API operations"""
    
    def __init__(self):
        self.api_version = settings.FACEBOOK_API_VERSION
        self.app_id = settings.FACEBOOK_APP_ID
        self.app_secret = settings.FACEBOOK_APP_SECRET
        self.redirect_uri = settings.FACEBOOK_REDIRECT_URI
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
    
    async def exchange_code_for_token(self, code: str) -> FacebookTokenData:
        """
        Exchange authorization code for user access token
        
        Args:
            code: Authorization code from Facebook OAuth redirect
            
        Returns:
            FacebookTokenData with access_token
            
        Raises:
            httpx.HTTPStatusError: If Facebook API returns error
        """
        url = f"{self.base_url}/oauth/access_token"
        params = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "redirect_uri": self.redirect_uri,
            "code": code
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ Exchanged code for access token")
                return FacebookTokenData(**data)
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Facebook token exchange failed: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error exchanging token: {e}")
            raise
    
    async def get_long_lived_token(self, short_lived_token: str) -> FacebookTokenData:
        """
        Exchange short-lived token for long-lived token (60 days)
        
        Optional: Can be called after exchange_code_for_token for better UX
        """
        url = f"{self.base_url}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": short_lived_token
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ Got long-lived token (expires in {data.get('expires_in', 'N/A')} seconds)")
                return FacebookTokenData(**data)
        except httpx.HTTPStatusError as e:
            logger.warning(f"⚠️ Could not get long-lived token: {e.response.text}")
            # Return original token if exchange fails
            return FacebookTokenData(access_token=short_lived_token, token_type="bearer")
        except Exception as e:
            logger.error(f"❌ Error getting long-lived token: {e}")
            return FacebookTokenData(access_token=short_lived_token, token_type="bearer")
    
    async def get_user_info(self, access_token: str) -> FacebookUser:
        """
        Get Facebook user information
        
        Args:
            access_token: User access token
            
        Returns:
            FacebookUser with id, name, email
        """
        url = f"{self.base_url}/me"
        params = {
            "access_token": access_token,
            "fields": "id,name,email"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ Got user info: {data.get('name')} (ID: {data.get('id')})")
                return FacebookUser(**data)
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Failed to get user info: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error getting user info: {e}")
            raise
    
    async def get_user_pages(self, user_access_token: str) -> List[FacebookPage]:
        """
        Get list of Facebook Pages managed by user
        
        Args:
            user_access_token: User access token
            
        Returns:
            List of FacebookPage objects
        """
        url = f"{self.base_url}/me/accounts"
        params = {
            "access_token": user_access_token,
            "fields": "id,name,access_token,category,tasks"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                pages = [FacebookPage(**page_data) for page_data in data.get("data", [])]
                logger.info(f"✅ Got {len(pages)} pages for user")
                
                return pages
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Failed to get user pages: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error getting user pages: {e}")
            raise
    
    async def subscribe_page_webhook(self, page_id: str, page_access_token: str) -> Dict[str, Any]:
        """
        Subscribe page to webhook for real-time updates
        
        Args:
            page_id: Facebook Page ID
            page_access_token: Page access token
            
        Returns:
            Response from Facebook API
            
        Note:
            Subscribes to: feed, leadgen, messages
            Requires app to have webhook configured in Facebook App Dashboard
        """
        url = f"{self.base_url}/{page_id}/subscribed_apps"
        params = {
            "access_token": page_access_token,
            "subscribed_fields": "feed,leadgen,messages,messaging_postbacks,message_deliveries,message_reads"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get("success"):
                    logger.info(f"✅ Successfully subscribed page {page_id} to webhook")
                else:
                    logger.warning(f"⚠️ Page {page_id} webhook subscription returned: {data}")
                
                return data
        except httpx.HTTPStatusError as e:
            # Don't fail the whole flow if webhook subscription fails
            logger.error(f"❌ Failed to subscribe page {page_id} to webhook: {e.response.text}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"❌ Unexpected error subscribing webhook for page {page_id}: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
facebook_service = FacebookService()


def get_facebook_service() -> FacebookService:
    """Dependency injection for FacebookService"""
    return facebook_service
