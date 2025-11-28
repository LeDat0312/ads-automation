# Implementation Plan: Ad Studio + Channel Management

## PHASE 1: Complete Ad Studio UI (PRIORITY)

### Task 1.1: Merge 2-step UI into single screen ✅ READY
**File**: `frontend/src/components/AdStudioCard.tsx`

**Current structure**:
```tsx
{currentStep === 1 && (
  <div className="grid grid-cols-1 lg:grid-cols-2">
    <div>/* Left: URL input, caption, video source */</div>
    <div>/* Right: Video preview */</div>
  </div>
)}

{currentStep === 2 && (
  <div className="grid grid-cols-1 lg:grid-cols-2">
    <div>/* Left: Publish form (caption, fanpage, CTA, schedule) */</div>
    <div>/* Right: Preview */</div>
  </div>
)}
```

**New structure** (MERGED):
```tsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  {/* LEFT COLUMN - All forms */}
  <div className="space-y-6">
    {/* Section 1: URL Input */}
    <div className="bg-white border rounded-lg p-4">
      <h3>1. Dán link video</h3>
      <input ... />
      <button>Lấy video TikTok</button>
    </div>

    {/* Section 2: Caption & Video Source (show after fetch) */}
    {selectedAsset && (
      <div className="bg-white border rounded-lg p-4">
        <h3>2. Nội dung & Video</h3>
        <textarea />
        <radio>Video gốc / Upload custom</radio>
      </div>
    )}

    {/* Section 3: Publish Settings (show after fetch) */}
    {selectedAsset && (
      <div className="bg-white border rounded-lg p-4">
        <h3>3. Cấu hình đăng bài</h3>
        <input>Video Title (NEW)</input>
        <select>Fanpages</select>
        <select>CTA (NEW)</select>
        <input>Target URL</input>
        <select>Schedule</select>
        <button>Lưu vào lịch đăng</button>
      </div>
    )}
  </div>

  {/* RIGHT COLUMN - Preview (always visible) */}
  <div className="space-y-4">
    <h3>Video Preview</h3>
    {selectedAsset ? (
      <>
        <video ... />
        <div>HD (No watermark) - {sizeInMB} MB</div> {/* NEW */}
        <a download>📥 Tải video về máy</a> {/* NEW */}
        <div>Caption preview...</div>
      </>
    ) : (
      <div>Dán link để xem preview</div>
    )}
  </div>
</div>
```

**Changes**:
- ✅ Remove Stepper component
- ✅ Remove `currentStep` state dependency
- ✅ Remove "Tiếp tục" and "Quay lại" buttons
- ✅ Show all sections in left column (URL → Caption → Publish form)
- ✅ Sections 2 & 3 only show after `selectedAsset` is fetched

---

### Task 1.2: Add new fields ✅ READY
**File**: `frontend/src/components/AdStudioCard.tsx`

**Add to publish form state**:
```ts
const [publishForm, setPublishForm] = useState({
  videoTitle: '', // NEW
  caption: '',
  language: 'la' as Language,
  ctaText: 'Nhắn tin ngay',
  targetUrl: '',
  pageIds: [] as string[],
  scheduleMode: 'NOW' as ScheduleMode,
  scheduleTime: '',
  thumbnailSource: 'FRAME' as ThumbnailSource,
  thumbnailFile: null as File | null,
});
```

**Add to UI** (Section 3):
```tsx
{/* Video Title - NEW */}
<div className="space-y-2">
  <label className="block text-sm font-medium text-gray-700">
    Tiêu đề video (optional)
  </label>
  <input
    type="text"
    value={publishForm.videoTitle}
    onChange={(e) => setPublishForm({ ...publishForm, videoTitle: e.target.value })}
    placeholder="Nhập tiêu đề cho video..."
    className="w-full px-4 py-2 border rounded-lg"
  />
</div>

{/* CTA Dropdown - Use CTA_OPTIONS from types */}
<div className="space-y-2">
  <label className="block text-sm font-medium text-gray-700">
    Call-to-Action
  </label>
  <select
    value={publishForm.ctaText}
    onChange={(e) => setPublishForm({ ...publishForm, ctaText: e.target.value })}
    className="w-full px-4 py-2 border rounded-lg"
  >
    {CTA_OPTIONS.map((opt) => (
      <option key={opt.value} value={opt.value}>
        {opt.label}
      </option>
    ))}
  </select>
</div>
```

---

### Task 1.3: Add video size badge & download button ✅ READY
**File**: `frontend/src/components/AdStudioCard.tsx`

**Update Asset type** (already done in types):
```ts
type Asset = {
  // ...existing fields
  videoSizeMb?: number; // from backend
};
```

**Add to preview** (right column):
```tsx
{selectedAsset && (
  <>
    <video ... />
    
    {/* Size badge - NEW */}
    {selectedAsset.videoSizeMb && (
      <div className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
        HD (No watermark) - {selectedAsset.videoSizeMb.toFixed(2)} MB
      </div>
    )}

    {/* Download button - NEW */}
    <a
      href={selectedAsset.videoUrl}
      download={`video-${selectedAsset.id}.mp4`}
      className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
    >
      📥 Tải video về máy
    </a>
  </>
)}
```

---

### Task 1.4: Improve error messages ✅ READY
**File**: `frontend/src/components/AdStudioCard.tsx`

**Current**:
```tsx
{fanpagesError && (
  <div className="text-sm text-red-600 mb-2">{fanpagesError}</div>
)}
```

**New** (with link to settings):
```tsx
{fanpagesError && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
    <p className="text-sm text-red-800 mb-2">{fanpagesError}</p>
    <a
      href="/settings"
      className="inline-flex items-center gap-1 text-sm text-red-600 hover:text-red-800 font-medium"
    >
      → Đi tới Cài Đặt
    </a>
  </div>
)}

{/* Error for missing Apify key */}
{error && error.includes('Apify') && (
  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
    <p className="text-sm text-yellow-800 mb-2">{error}</p>
    <a
      href="/settings"
      className="inline-flex items-center gap-1 text-sm text-yellow-600 hover:text-yellow-800 font-medium"
    >
      → Đi tới Cài Đặt → Apify
    </a>
  </div>
)}
```

---

### Task 1.5: Remove ScrapeGraphAI references 🔍 NEED TO CHECK

**Files to check**:
- `frontend/src/pages/ContentStudio.tsx` (old name?)
- `frontend/src/components/` (any old components?)
- `app/api/routes/competitor_research.py` (backend route?)
- `app/models/` (any old models?)
- `app/services/scrapegraphai_service.py` (old service?)

**Actions**:
1. Search for "ScrapeGraphAI" in codebase
2. Remove UI references
3. Keep DB tables/models (don't delete data) but mark as deprecated
4. Remove from Settings page UI

---

## PHASE 2: Channel Management (NEW FEATURE)

### Task 2.1: Database migrations 📝 DESIGN PHASE

**File**: `migrations/add_channel_management.py`

```python
"""
Add tables for multi-channel management and auto-comment
"""

def upgrade():
    # 1. social_accounts
    op.create_table(
        'social_accounts',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('provider', sa.String(20)),  # facebook|tiktok
        sa.Column('access_token', sa.Text()),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    
    # 2. social_pages
    op.create_table(
        'social_pages',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('social_account_id', postgresql.UUID(), sa.ForeignKey('social_accounts.id')),
        sa.Column('provider', sa.String(20)),
        sa.Column('page_id', sa.String(100)),  # External page ID
        sa.Column('name', sa.String(255)),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('is_connected', sa.Boolean(), default=True),
        sa.Column('can_post', sa.Boolean(), default=True),
        sa.Column('timezone', sa.String(50), nullable=True),
        sa.Column('default_language', sa.String(10), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.UniqueConstraint('provider', 'page_id')
    )
    
    # 3. page_settings
    op.create_table(
        'page_settings',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('page_id', postgresql.UUID(), sa.ForeignKey('social_pages.id')),
        sa.Column('auto_share_to_story', sa.Boolean(), default=False),
        sa.Column('default_comment_signature', sa.Text(), nullable=True),
        sa.Column('default_auto_comment_enabled', sa.Boolean(), default=False),
        sa.Column('default_cta_type', sa.String(50), nullable=True),
        sa.Column('default_cta_url', sa.Text(), nullable=True),
        sa.Column('extra', postgresql.JSONB(), default=dict)
    )
    
    # 4. channel_groups
    op.create_table(
        'channel_groups',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('name', sa.String(100)),
        sa.Column('color', sa.String(7)),  # HEX color
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    
    # 5. channel_group_members
    op.create_table(
        'channel_group_members',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('group_id', postgresql.UUID(), sa.ForeignKey('channel_groups.id', ondelete='CASCADE')),
        sa.Column('page_id', postgresql.UUID(), sa.ForeignKey('social_pages.id', ondelete='CASCADE')),
        sa.Column('created_at', sa.DateTime()),
        sa.UniqueConstraint('group_id', 'page_id')
    )
    
    # 6. auto_comment_templates
    op.create_table(
        'auto_comment_templates',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('name', sa.String(100)),
        sa.Column('content', sa.Text()),  # Supports spin syntax {variant1|variant2}
        sa.Column('media_url', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    
    # 7. page_auto_comment_rules
    op.create_table(
        'page_auto_comment_rules',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('page_id', postgresql.UUID(), sa.ForeignKey('social_pages.id')),
        sa.Column('template_id', postgresql.UUID(), sa.ForeignKey('auto_comment_templates.id')),
        sa.Column('delay_seconds', sa.Integer(), default=60),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
```

---

### Task 2.2: Backend models 📝 DESIGN PHASE

**File**: `app/models/channel_management.py` (NEW)

```python
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

class SocialAccount(Base):
    __tablename__ = "social_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider = Column(String(20))  # facebook|tiktok
    access_token = Column(Text)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pages = relationship("SocialPage", back_populates="account", cascade="all, delete-orphan")

class SocialPage(Base):
    __tablename__ = "social_pages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    social_account_id = Column(UUID(as_uuid=True), ForeignKey("social_accounts.id"))
    provider = Column(String(20))
    page_id = Column(String(100))
    name = Column(String(255))
    avatar_url = Column(Text, nullable=True)
    is_connected = Column(Boolean, default=True)
    can_post = Column(Boolean, default=True)
    timezone = Column(String(50), nullable=True)
    default_language = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("SocialAccount", back_populates="pages")
    settings = relationship("PageSettings", back_populates="page", uselist=False)
    group_memberships = relationship("ChannelGroupMember", back_populates="page")

# ... (similar for other models)
```

---

### Task 2.3: Backend APIs 📝 DESIGN PHASE

**File**: `app/api/routes/channel_management.py` (NEW)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.channel_management import SocialPage, ChannelGroup
from app.schemas.channel_management import (
    SocialPageResponse, 
    SocialPageUpdate,
    ChannelGroupCreate,
    ChannelGroupResponse
)

router = APIRouter()

@router.get("/api/social/pages", response_model=List[SocialPageResponse])
async def get_social_pages(db: Session = Depends(get_db)):
    """Get all connected social pages with settings and groups"""
    pages = db.query(SocialPage).filter(SocialPage.is_connected == True).all()
    return pages

@router.patch("/api/social/pages/{id}", response_model=SocialPageResponse)
async def update_social_page(
    id: str,
    update: SocialPageUpdate,
    db: Session = Depends(get_db)
):
    """Update page settings and group assignments"""
    page = db.query(SocialPage).filter(SocialPage.id == id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Update settings
    if page.settings:
        for key, value in update.dict(exclude_unset=True).items():
            setattr(page.settings, key, value)
    
    db.commit()
    db.refresh(page)
    return page

@router.get("/api/channel-groups", response_model=List[ChannelGroupResponse])
async def get_channel_groups(db: Session = Depends(get_db)):
    """Get all channel groups"""
    groups = db.query(ChannelGroup).all()
    return groups

# ... more CRUD endpoints
```

---

### Task 2.4: Auto-comment worker 📝 DESIGN PHASE

**File**: `app/workers/auto_comment_worker.py` (NEW)

```python
import asyncio
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.channel_management import PageAutoCommentRule
from app.services.facebook_api import post_comment_to_facebook

logger = logging.getLogger(__name__)

async def process_auto_comment_job(
    page_id: str,
    post_id: str,
    template_id: str,
    delay_seconds: int
):
    """
    Process a single auto-comment job
    """
    # Wait for delay
    await asyncio.sleep(delay_seconds)
    
    db = SessionLocal()
    try:
        # Get template
        from app.models.channel_management import AutoCommentTemplate
        template = db.query(AutoCommentTemplate).filter(
            AutoCommentTemplate.id == template_id
        ).first()
        
        if not template or not template.enabled:
            logger.warning(f"Template {template_id} not found or disabled")
            return
        
        # Generate content (simple for now, spin syntax later)
        comment_text = template.content
        
        # Post comment via Graph API
        await post_comment_to_facebook(
            post_id=post_id,
            message=comment_text,
            media_url=template.media_url
        )
        
        logger.info(f"✅ Auto-commented on post {post_id}")
        
    except Exception as e:
        logger.error(f"❌ Auto-comment failed for post {post_id}: {e}")
    finally:
        db.close()
```

**Hook into publish flow** in `app/api/routes/ad_studio.py`:
```python
# After successful Facebook post publish
if post_response.get("id"):
    post_id = post_response["id"]
    
    # Check if page has auto-comment rule
    from app.models.channel_management import PageAutoCommentRule
    rule = db.query(PageAutoCommentRule).filter(
        PageAutoCommentRule.page_id == page_id,
        PageAutoCommentRule.is_active == True
    ).first()
    
    if rule:
        # Schedule auto-comment job
        asyncio.create_task(process_auto_comment_job(
            page_id=page_id,
            post_id=post_id,
            template_id=rule.template_id,
            delay_seconds=rule.delay_seconds
        ))
```

---

### Task 2.5: Frontend - Channel Groups page 📝 DESIGN PHASE

**File**: `frontend/src/pages/ChannelGroupsPage.tsx` (NEW)

**Layout** (similar to So9):
```tsx
export default function ChannelGroupsPage() {
  const [groups, setGroups] = useState<ChannelGroup[]>([]);
  const [pages, setPages] = useState<SocialPage[]>([]);
  
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Nhóm kênh</h1>
        <button onClick={() => setShowCreateModal(true)}>
          + Thêm nhóm kênh
        </button>
      </div>
      
      <div className="space-y-4">
        {groups.map((group) => (
          <div key={group.id} className="bg-white border rounded-lg p-4">
            <div className="flex items-center gap-3 mb-3">
              <div 
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: group.color }}
              />
              <h3 className="font-semibold">{group.name}</h3>
              <button>Edit</button>
              <button>Delete</button>
            </div>
            
            {/* Page chips */}
            <div className="flex flex-wrap gap-2">
              {group.members.map((member) => (
                <div key={member.page_id} className="px-3 py-1 bg-gray-100 rounded-full text-sm">
                  {member.page.name}
                  <button onClick={() => removeFromGroup(group.id, member.page_id)}>
                    ×
                  </button>
                </div>
              ))}
              
              <button onClick={() => showAddPageModal(group.id)}>
                + Thêm page
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### Task 2.6: Frontend - Connected Channels page 📝 DESIGN PHASE

**File**: `frontend/src/pages/ConnectedChannelsPage.tsx` (NEW)

Similar to Settings but focused on channel management.

---

### Task 2.7: Integrate with Ad Studio 📝 DESIGN PHASE

**Update**: `frontend/src/components/AdStudioCard.tsx`

In fanpage selection section:
```tsx
{/* NEW: Channel Group selector */}
<div className="space-y-2">
  <label className="block text-sm font-medium text-gray-700">
    Chọn nhanh theo nhóm
  </label>
  <select
    onChange={(e) => {
      const groupId = e.target.value;
      const group = channelGroups.find(g => g.id === groupId);
      if (group) {
        const pageIds = group.members.map(m => m.page_id);
        setPublishForm({ ...publishForm, pageIds });
      }
    }}
    className="w-full px-4 py-2 border rounded-lg"
  >
    <option value="">-- Chọn nhóm kênh --</option>
    {channelGroups.map((group) => (
      <option key={group.id} value={group.id}>
        {group.name} ({group.members.length} pages)
      </option>
    ))}
  </select>
</div>

{/* Existing fanpage checkboxes below */}
```

---

## IMPLEMENTATION ORDER

### Week 1: Complete Ad Studio UI
- Day 1-2: Task 1.1 - Merge UI
- Day 2-3: Task 1.2 & 1.3 - New fields + badges
- Day 3-4: Task 1.4 - Error messages
- Day 4-5: Task 1.5 - Cleanup, testing

### Week 2: Channel Management Backend
- Day 1-2: Task 2.1 - Migrations
- Day 2-3: Task 2.2 - Models
- Day 3-4: Task 2.3 - APIs
- Day 4-5: Task 2.4 - Auto-comment worker

### Week 3: Channel Management Frontend
- Day 1-2: Task 2.5 - Channel Groups page
- Day 2-3: Task 2.6 - Connected Channels page
- Day 3-5: Task 2.7 - Integration + testing

---

## ROLLBACK PLAN

Each phase has clear Git commits:
- Phase 1 complete → Tag `v1-ad-studio-ui-complete`
- Phase 2 backend → Tag `v2-channel-mgmt-backend`
- Phase 2 frontend → Tag `v2-channel-mgmt-frontend`

If any phase fails, `git revert` to previous tag.

---

## TESTING CHECKLIST

### Phase 1
- [ ] UI shows single screen (no stepper)
- [ ] All fields visible after video fetch
- [ ] Video title saves correctly
- [ ] CTA dropdown works
- [ ] Size badge displays MB
- [ ] Download button downloads correct file
- [ ] Error messages show /settings link
- [ ] No ScrapeGraphAI text anywhere

### Phase 2
- [ ] Can create channel groups
- [ ] Can add/remove pages from groups
- [ ] Group selector in Ad Studio works
- [ ] Auto-comment posts after publish
- [ ] Auto-comment respects delay
- [ ] Worker handles errors gracefully

---

**Status**: 📋 READY FOR REVIEW
**Estimated time**: 3 weeks
**Risk level**: Medium (large UI refactor in Phase 1)

Bạn muốn tôi bắt đầu implement Phase 1 Task 1.1 không?
