"""
Channels Service Layer
Business logic for Channel Management operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
import logging

from app.models.channels import (
    Channel, ChannelGroup, ChannelGroupMembership, 
    PostingSettings, AutoCommentTemplate
)
from app.schemas.channels import (
    ChannelCreate, ChannelUpdate, FacebookPageImport,
    ChannelGroupCreate, ChannelGroupUpdate,
    PostingSettingsUpdate, AutoCommentTemplateCreate, AutoCommentTemplateUpdate
)
from app.core.security import encrypt_token
from datetime import datetime

logger = logging.getLogger(__name__)


class ChannelsService:
    """Service for managing channels"""
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    # ==================== CHANNEL METHODS ====================
    
    def list_channels(
        self, 
        platform: Optional[str] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Channel]:
        """List channels for current user with optional filters"""
        query = self.db.query(Channel).filter(Channel.user_id == self.user_id)
        
        if platform:
            query = query.filter(Channel.platform == platform.lower())
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Channel.page_name.ilike(search_term),
                    Channel.page_id.ilike(search_term),
                    Channel.page_username.ilike(search_term)
                )
            )
        
        if is_active is not None:
            query = query.filter(Channel.is_active == is_active)
        
        return query.order_by(Channel.page_name).all()
    
    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get channel by ID (must belong to current user)"""
        channel = self.db.query(Channel).filter(
            and_(
                Channel.id == channel_id,
                Channel.user_id == self.user_id
            )
        ).first()
        return channel
    
    def create_channel(self, channel_data: ChannelCreate) -> Channel:
        """Create a new channel"""
        try:
            # Encrypt access token if provided
            access_token_encrypted = None
            if hasattr(channel_data, 'access_token') and channel_data.access_token:
                access_token_encrypted = encrypt_token(channel_data.access_token)
            
            channel = Channel(
                user_id=self.user_id,
                platform=channel_data.platform,
                page_id=channel_data.page_id,
                page_name=channel_data.page_name,
                page_username=channel_data.page_username,
                avatar_url=channel_data.avatar_url,
                access_token_encrypted=access_token_encrypted,
                is_active=channel_data.is_active
            )
            self.db.add(channel)
            self.db.commit()
            self.db.refresh(channel)
            logger.info(f"✅ Created channel: {channel.page_name} (ID: {channel.id})")
            return channel
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"❌ Integrity error creating channel: {e}")
            raise HTTPException(
                status_code=400,
                detail="Channel với platform và page_id này đã tồn tại cho user này"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creating channel: {e}")
            raise
    
    def import_facebook_pages(self, pages: List[FacebookPageImport]) -> List[Channel]:
        """Import/upsert Facebook pages from OAuth flow"""
        from datetime import datetime
        imported_channels = []
        
        for page_data in pages:
            try:
                # Check if channel already exists
                existing = self.db.query(Channel).filter(
                    and_(
                        Channel.user_id == self.user_id,
                        Channel.platform == "facebook",
                        Channel.page_id == page_data.page_id
                    )
                ).first()
                
                # Encrypt access token if provided
                access_token_encrypted = None
                if page_data.access_token:
                    access_token_encrypted = encrypt_token(page_data.access_token)
                
                if existing:
                    # Update existing channel
                    existing.page_name = page_data.name
                    existing.avatar_url = page_data.avatar
                    if access_token_encrypted:
                        existing.access_token_encrypted = access_token_encrypted
                    existing.updated_at = datetime.utcnow()
                    imported_channels.append(existing)
                else:
                    # Create new channel
                    channel = Channel(
                        user_id=self.user_id,
                        platform="facebook",
                        page_id=page_data.page_id,
                        page_name=page_data.name,
                        avatar_url=page_data.avatar,
                        access_token_encrypted=access_token_encrypted,
                        is_active=True
                    )
                    self.db.add(channel)
                    imported_channels.append(channel)
                
                self.db.commit()
                if not existing:
                    self.db.refresh(imported_channels[-1])
            
            except IntegrityError:
                self.db.rollback()
                logger.warning(f"Channel {page_data.page_id} already exists, skipping...")
            except Exception as e:
                self.db.rollback()
                logger.error(f"Error importing page {page_data.page_id}: {e}")
        
        return imported_channels
    
    def update_channel(self, channel_id: str, channel_data: ChannelUpdate) -> Channel:
        """Update an existing channel"""
        channel = self.get_channel(channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Không tìm thấy kênh")
        
        try:
            update_data = channel_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(channel, field, value)
            
            channel.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(channel)
            logger.info(f"✅ Updated channel: {channel.page_name} (ID: {channel.id})")
            return channel
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error updating channel: {e}")
            raise
    
    def delete_channel(self, channel_id: str) -> bool:
        """Delete a channel (cascades to memberships, settings, templates)"""
        channel = self.get_channel(channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Không tìm thấy kênh")
        
        try:
            self.db.delete(channel)
            self.db.commit()
            logger.info(f"✅ Deleted channel: {channel_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error deleting channel: {e}")
            raise
    
    # ==================== CHANNEL GROUP METHODS ====================
    
    def list_groups(self) -> List[ChannelGroup]:
        """List all channel groups for current user"""
        groups = self.db.query(ChannelGroup).filter(
            ChannelGroup.user_id == self.user_id
        ).order_by(ChannelGroup.name).all()
        return groups
    
    def get_group(self, group_id: str) -> Optional[ChannelGroup]:
        """Get channel group by ID (must belong to current user)"""
        group = self.db.query(ChannelGroup).filter(
            and_(
                ChannelGroup.id == group_id,
                ChannelGroup.user_id == self.user_id
            )
        ).first()
        return group
    
    def create_group(self, group_data: ChannelGroupCreate) -> ChannelGroup:
        """Create a new channel group"""
        try:
            group = ChannelGroup(
                user_id=self.user_id,
                name=group_data.name,
                color_hex=group_data.color_hex or "#3B82F6"
            )
            self.db.add(group)
            self.db.flush()  # Get group.id
            
            # Add channels if provided
            if group_data.channel_ids:
                self._validate_channels_ownership(group_data.channel_ids)
                for channel_id in group_data.channel_ids:
                    membership = ChannelGroupMembership(
                        group_id=group.id,
                        channel_id=channel_id
                    )
                    self.db.add(membership)
            
            self.db.commit()
            self.db.refresh(group)
            logger.info(f"✅ Created group: {group.name} (ID: {group.id})")
            return group
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"❌ Integrity error creating group: {e}")
            raise HTTPException(
                status_code=400,
                detail="Nhóm kênh với tên này đã tồn tại"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creating group: {e}")
            raise
    
    def update_group(self, group_id: str, group_data: ChannelGroupUpdate) -> ChannelGroup:
        """Update a channel group (including channel memberships)"""
        group = self.get_group(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Không tìm thấy nhóm kênh")
        
        try:
            # Update group fields
            if group_data.name is not None:
                group.name = group_data.name
            if group_data.color_hex is not None:
                group.color_hex = group_data.color_hex
            group.updated_at = datetime.utcnow()
            
            # Update channel memberships if provided
            if group_data.channel_ids is not None:
                # Validate all channels belong to user
                self._validate_channels_ownership(group_data.channel_ids)
                
                # Delete existing memberships
                self.db.query(ChannelGroupMembership).filter(
                    ChannelGroupMembership.group_id == group_id
                ).delete()
                
                # Create new memberships
                for channel_id in group_data.channel_ids:
                    membership = ChannelGroupMembership(
                        group_id=group_id,
                        channel_id=channel_id
                    )
                    self.db.add(membership)
            
            self.db.commit()
            self.db.refresh(group)
            logger.info(f"✅ Updated group: {group.name} (ID: {group.id})")
            return group
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"❌ Integrity error updating group: {e}")
            raise HTTPException(
                status_code=400,
                detail="Nhóm kênh với tên này đã tồn tại"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error updating group: {e}")
            raise
    
    def delete_group(self, group_id: str) -> bool:
        """Delete a channel group (cascades to memberships)"""
        group = self.get_group(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Không tìm thấy nhóm kênh")
        
        try:
            self.db.delete(group)
            self.db.commit()
            logger.info(f"✅ Deleted group: {group_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error deleting group: {e}")
            raise
    
    def _validate_channels_ownership(self, channel_ids: List[str]) -> None:
        """Validate that all channels belong to current user"""
        channels = self.db.query(Channel).filter(
            and_(
                Channel.id.in_(channel_ids),
                Channel.user_id == self.user_id
            )
        ).all()
        
        found_ids = {ch.id for ch in channels}
        missing_ids = set(channel_ids) - found_ids
        
        if missing_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Các kênh sau không tồn tại hoặc không thuộc về bạn: {', '.join(missing_ids)}"
            )
    
    # ==================== POSTING SETTINGS METHODS ====================
    
    def get_posting_settings_for_all_channels(self) -> List[Dict[str, Any]]:
        """Get posting settings for all channels (for posting settings page)"""
        channels = self.list_channels()
        result = []
        
        for channel in channels:
            # Get settings (create default if not exists)
            settings = self.db.query(PostingSettings).filter(
                PostingSettings.channel_id == channel.id
            ).first()
            
            if not settings:
                settings = PostingSettings(
                    user_id=self.user_id,
                    channel_id=channel.id,
                    default_signature=None,
                    auto_comment_enabled=False,
                    auto_comment_delay_seconds=None
                )
                self.db.add(settings)
                self.db.commit()
                self.db.refresh(settings)
            
            # Get auto-comment templates
            templates = self.db.query(AutoCommentTemplate).filter(
                and_(
                    AutoCommentTemplate.channel_id == channel.id,
                    AutoCommentTemplate.is_active == True
                )
            ).order_by(AutoCommentTemplate.sort_order).all()
            
            result.append({
                "channel": channel,
                "settings": settings,
                "auto_comments": templates
            })
        
        return result
    
    def upsert_posting_settings(
        self, 
        channel_id: str, 
        settings_data: PostingSettingsUpdate,
        auto_comment_templates: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Upsert posting settings and auto-comment templates for a channel"""
        # Validate channel ownership
        channel = self.get_channel(channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Không tìm thấy kênh")
        
        try:
            # Upsert posting settings
            settings = self.db.query(PostingSettings).filter(
                PostingSettings.channel_id == channel_id
            ).first()
            
            if not settings:
                settings = PostingSettings(
                    user_id=self.user_id,
                    channel_id=channel_id
                )
                self.db.add(settings)
            
            # Update settings fields
            update_data = settings_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(settings, field, value)
            settings.updated_at = datetime.utcnow()
            
            # Handle auto-comment templates if provided
            if auto_comment_templates is not None:
                # Get existing template IDs
                existing_template_ids = {
                    t.id for t in self.db.query(AutoCommentTemplate).filter(
                        AutoCommentTemplate.channel_id == channel_id
                    ).all()
                }
                
                # Process templates from request
                new_template_ids = set()
                for template_data in auto_comment_templates:
                    template_id = template_data.get('id')
                    
                    if template_id and template_id in existing_template_ids:
                        # Update existing template
                        template = self.db.query(AutoCommentTemplate).filter(
                            and_(
                                AutoCommentTemplate.id == template_id,
                                AutoCommentTemplate.channel_id == channel_id,
                                AutoCommentTemplate.user_id == self.user_id
                            )
                        ).first()
                        
                        if template:
                            for field, value in template_data.items():
                                if field != 'id' and hasattr(template, field):
                                    setattr(template, field, value)
                            template.updated_at = datetime.utcnow()
                            new_template_ids.add(template_id)
                    else:
                        # Create new template
                        template = AutoCommentTemplate(
                            user_id=self.user_id,
                            channel_id=channel_id,
                            content=template_data.get('content', ''),
                            media_url=template_data.get('media_url'),
                            schedule_type=template_data.get('schedule_type', 'IMMEDIATE'),
                            delay_minutes=template_data.get('delay_minutes'),
                            is_active=template_data.get('is_active', True),
                            sort_order=template_data.get('sort_order', 0)
                        )
                        self.db.add(template)
                        self.db.flush()
                        new_template_ids.add(template.id)
                
                # Delete templates not in new list
                to_delete_ids = existing_template_ids - new_template_ids
                if to_delete_ids:
                    self.db.query(AutoCommentTemplate).filter(
                        AutoCommentTemplate.id.in_(to_delete_ids)
                    ).delete(synchronize_session=False)
            
            self.db.commit()
            self.db.refresh(settings)
            
            # Return updated data
            templates = self.db.query(AutoCommentTemplate).filter(
                AutoCommentTemplate.channel_id == channel_id
            ).order_by(AutoCommentTemplate.sort_order).all()
            
            return {
                "channel": channel,
                "settings": settings,
                "auto_comments": templates
            }
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error upserting posting settings: {e}")
            raise


# Helper function to create service instance
def get_channels_service(db: Session, user_id: int) -> ChannelsService:
    """Factory function to create ChannelsService instance"""
    return ChannelsService(db, user_id)

