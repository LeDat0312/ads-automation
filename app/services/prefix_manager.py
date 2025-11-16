# -*- coding: utf-8 -*-
"""
Prefix Management Service
Pattern matching, campaign detection, auto-suggestion
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Dict, Any, Tuple, Set
from datetime import datetime
import logging
import re
from collections import Counter

from app.models.account_prefix import Prefix, AccountPrefix, Account
from app.schemas.prefix_response import (
    PatternTypeEnum,
    PrefixFilterRequest,
    PatternTestResult,
    EnhancedPrefixResponse,
    CampaignMatch,
)

logger = logging.getLogger(__name__)


class PrefixPatternService:
    """Service để handle prefix pattern matching"""
    
    @staticmethod
    def match_campaign_to_prefix(
        campaign_name: str,
        prefix: str,
        pattern_type: PatternTypeEnum,
        custom_pattern: str = None
    ) -> bool:
        """
        Check if campaign matches prefix pattern
        
        Args:
            campaign_name: Tên campaign
            prefix: Prefix code
            pattern_type: Loại pattern matching
            custom_pattern: Custom pattern nếu khác prefix
        
        Returns:
            True nếu match
        """
        if not campaign_name:
            return False
        
        # Use custom_pattern nếu có, otherwise use prefix
        pattern = custom_pattern or prefix
        
        try:
            if pattern_type == PatternTypeEnum.EXACT:
                return campaign_name == pattern
            
            elif pattern_type == PatternTypeEnum.CONTAINS:
                return pattern.lower() in campaign_name.lower()
            
            elif pattern_type == PatternTypeEnum.STARTS_WITH:
                return campaign_name.lower().startswith(pattern.lower())
            
            elif pattern_type == PatternTypeEnum.ENDS_WITH:
                return campaign_name.lower().endswith(pattern.lower())
            
            elif pattern_type == PatternTypeEnum.REGEX:
                return bool(re.search(pattern, campaign_name, re.IGNORECASE))
            
            return False
        except Exception as e:
            logger.warning(f"Pattern matching error for '{campaign_name}' with pattern '{pattern}': {e}")
            return False
    
    @staticmethod
    def test_pattern(
        pattern: str,
        pattern_type: PatternTypeEnum,
        test_strings: List[str]
    ) -> PatternTestResult:
        """
        Test pattern against multiple strings
        
        Returns: PatternTestResult with match info
        """
        matches = []
        non_matches = []
        
        for test_str in test_strings:
            if PrefixPatternService.match_campaign_to_prefix(
                test_str, pattern, pattern_type
            ):
                matches.append(test_str)
            else:
                non_matches.append(test_str)
        
        match_rate = (len(matches) / len(test_strings) * 100) if test_strings else 0
        
        return PatternTestResult(
            pattern=pattern,
            pattern_type=pattern_type,
            test_strings=test_strings,
            matches=matches,
            non_matches=non_matches,
            match_rate=match_rate
        )
    
    @staticmethod
    def validate_regex_pattern(pattern: str) -> Tuple[bool, str]:
        """
        Validate regex pattern
        
        Returns: (is_valid, error_message)
        """
        try:
            re.compile(pattern)
            return True, ""
        except re.error as e:
            return False, str(e)


class PrefixFilterService:
    """Service để filter prefixes"""
    
    @staticmethod
    def apply_filters(
        db: Session,
        user_id: int,
        filter_req: PrefixFilterRequest
    ) -> Tuple[List[Prefix], int]:
        """Apply filters and return paginated results"""
        query = db.query(Prefix).filter(Prefix.user_id == user_id)
        
        # Filter by enabled
        if filter_req.enabled_only:
            query = query.filter(Prefix.enabled == True)
        
        # Filter by category (if extended model has it)
        if filter_req.category:
            # TODO: Add category field to Prefix model
            pass
        
        # Search by prefix or name
        if filter_req.search:
            search_term = f"%{filter_req.search}%"
            query = query.filter(
                or_(
                    Prefix.prefix.ilike(search_term),
                    Prefix.prefix_name.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Sorting
        if filter_req.sort_by == "updated_at":
            sort_col = Prefix.updated_at
        elif filter_req.sort_by == "created_at":
            sort_col = Prefix.created_at
        elif filter_req.sort_by == "prefix":
            sort_col = Prefix.prefix
        else:
            sort_col = Prefix.updated_at
        
        sort_direction = desc if filter_req.sort_order == "desc" else desc
        query = query.order_by(sort_direction(sort_col))
        
        # Pagination
        offset = (filter_req.page - 1) * filter_req.page_size
        prefixes = query.offset(offset).limit(filter_req.page_size).all()
        
        return prefixes, total


class PrefixCampaignService:
    """Service để detect campaigns matched by prefixes"""
    
    @staticmethod
    def get_campaigns_by_prefix(
        db: Session,
        prefix: Prefix,
        account_ids: List[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get campaigns matched by prefix
        
        Note: Requires querying ads_metrics table
        TODO: Implement when ads_metrics integration is done
        """
        # Placeholder: return empty list
        return []
    
    @staticmethod
    def get_prefix_coverage(
        db: Session,
        prefix: Prefix,
        account_ids: List[int] = None
    ) -> Dict[str, Any]:
        """
        Get coverage info for prefix
        - Total linked accounts
        - Total matched campaigns
        - Active campaigns
        """
        # Get linked accounts
        linked_accounts = db.query(AccountPrefix).filter(
            AccountPrefix.prefix_id == prefix.id
        ).count()
        
        # Get matched campaigns (TODO: query ads_metrics)
        matched_campaigns = 0
        active_campaigns = 0
        
        return {
            "linked_accounts": linked_accounts,
            "total_campaigns": matched_campaigns,
            "active_campaigns": active_campaigns,
            "coverage_rate": 0  # percentage
        }


class PrefixAutoSuggestService:
    """Service để auto-suggest prefixes từ campaign names"""
    
    @staticmethod
    def extract_prefixes_from_campaigns(
        campaigns: List[Dict[str, str]],
        min_frequency: int = 2,
        min_length: int = 2,
        max_length: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Auto-extract prefixes từ campaign names
        
        Algorithm:
        1. Split campaign names by underscore/dash/space
        2. Count frequency of each segment
        3. Return segments that appear in >= min_frequency campaigns
        
        Args:
            campaigns: [{campaign_name, campaign_id}, ...]
            min_frequency: Minimum campaigns with same prefix
            min_length: Minimum prefix length
            max_length: Maximum prefix length
        
        Returns:
            [{prefix, frequency, examples}, ...]
        """
        segments = Counter()
        segment_examples: Dict[str, Set[str]] = {}
        
        # Extract segments from campaign names
        for campaign in campaigns:
            name = campaign.get("campaign_name", "")
            if not name:
                continue
            
            # Split by common delimiters
            parts = re.split(r'[_\-\s]+', name)
            
            for part in parts:
                if min_length <= len(part) <= max_length and part.isalnum():
                    segments[part] += 1
                    if part not in segment_examples:
                        segment_examples[part] = set()
                    segment_examples[part].add(name)
        
        # Filter by frequency
        suggestions = []
        for segment, count in segments.items():
            if count >= min_frequency:
                suggestions.append({
                    "prefix": segment,
                    "frequency": count,
                    "percentage": round(count / len(campaigns) * 100, 2),
                    "examples": list(segment_examples[segment])[:3]
                })
        
        # Sort by frequency
        suggestions.sort(key=lambda x: x["frequency"], reverse=True)
        
        return suggestions
    
    @staticmethod
    def detect_naming_pattern(
        campaign_names: List[str]
    ) -> Dict[str, Any]:
        """
        Detect naming pattern in campaigns
        
        Returns:
            {
                "pattern": "PRODUCT_PREFIX_TYPE" or "REGION_PRODUCT" etc,
                "examples": [...],
                "confidence": 0.8
            }
        """
        # Analyze structure of campaign names
        # This is a simplified version
        
        if not campaign_names:
            return {"pattern": "UNKNOWN", "examples": [], "confidence": 0}
        
        # Check for common patterns
        underscore_separated = all("_" in name for name in campaign_names)
        dash_separated = all("-" in name for name in campaign_names)
        
        if underscore_separated:
            pattern = "UNDERSCORE_SEPARATED"
        elif dash_separated:
            pattern = "DASH_SEPARATED"
        else:
            pattern = "SPACE_SEPARATED"
        
        return {
            "pattern": pattern,
            "examples": campaign_names[:5],
            "confidence": 0.8
        }


class PrefixBatchService:
    """Service để batch operations trên prefixes"""
    
    @staticmethod
    def bulk_enable(db: Session, user_id: int, prefix_ids: List[int]) -> int:
        """Enable multiple prefixes"""
        updated = db.query(Prefix).filter(
            Prefix.user_id == user_id,
            Prefix.id.in_(prefix_ids)
        ).update({"enabled": True})
        db.commit()
        return updated
    
    @staticmethod
    def bulk_disable(db: Session, user_id: int, prefix_ids: List[int]) -> int:
        """Disable multiple prefixes"""
        updated = db.query(Prefix).filter(
            Prefix.user_id == user_id,
            Prefix.id.in_(prefix_ids)
        ).update({"enabled": False})
        db.commit()
        return updated
    
    @staticmethod
    def bulk_delete(db: Session, user_id: int, prefix_ids: List[int]) -> int:
        """Delete multiple prefixes"""
        # Delete linked accounts first
        db.query(AccountPrefix).filter(
            AccountPrefix.prefix_id.in_(prefix_ids)
        ).delete()
        
        # Delete prefixes
        deleted = db.query(Prefix).filter(
            Prefix.user_id == user_id,
            Prefix.id.in_(prefix_ids)
        ).delete()
        
        db.commit()
        return deleted
