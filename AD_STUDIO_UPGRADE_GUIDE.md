# Ad Studio Upgrade Guide

## 📋 Tổng quan

Component `AdStudioCard.tsx` hiện tại đã tốt (3000+ dòng code). Cần nâng cấp theo các yêu cầu:

## ✅ 1. SỬA LỖI BACKEND - `/api/tiktok/scrape` trả 500

### Backend Fix Required

**File:** `app/api/routes/tiktok.py` (hoặc tương đương)

```python
@router.post("/scrape")
async def scrape_tiktok_video(url: str):
    """Scrape TikTok video with proper error handling"""
    try:
        # Validate URL
        if not url or not ("tiktok.com" in url):
            return {
                "success": False,
                "code": "INVALID_URL",
                "message": "Link không hợp lệ, vui lòng kiểm tra lại."
            }
        
        # Call scraper service
        result = await tiktok_scraper.fetch(url)
        
        if not result:
            return {
                "success": False,
                "code": "PRIVATE_VIDEO",
                "message": "Video đã riêng tư hoặc bị xóa."
            }
        
        return {
            "success": True,
            "data": {
                "id": result.id,
                "platform": "tiktok",
                "videoUrl": result.video_url,
                "thumbnailUrl": result.thumbnail_url,
                "captionOriginal": result.caption,
                "duration": result.duration,
                "hashtags": result.hashtags
            }
        }
        
    except requests.Timeout:
        return {
            "success": False,
            "code": "UPSTREAM_ERROR",
            "message": "Hệ thống tạm thời lỗi khi tải video, hãy thử lại sau."
        }
    except Exception as e:
        logger.error(f"TikTok scrape error: {e}", exc_info=True)
        return {
            "success": False,
            "code": "UNKNOWN_ERROR",
            "message": "Có lỗi xảy ra, vui lòng thử lại sau."
        }
```

### Frontend Fix

**File:** `frontend/src/api/adStudio.ts`

```typescript
export async function fetchTiktokAsset(url: string) {
  const response = await api.post('/api/tiktok/scrape', { url });
  
  if (!response.data.success) {
    const errorMessages = {
      'INVALID_URL': 'Link không hợp lệ, vui lòng kiểm tra lại.',
      'PRIVATE_VIDEO': 'Video đã riêng tư hoặc bị xóa.',
      'UPSTREAM_ERROR': 'Hệ thống tạm thời lỗi khi tải video, hãy thử lại sau.',
      'UNKNOWN_ERROR': 'Có lỗi xảy ra, vui lòng thử lại sau.'
    };
    
    const message = errorMessages[response.data.code] || response.data.message;
    throw new Error(message);
  }
  
  return response.data.data;
}
```

## ✅ 2. KÉO THẢ VIDEO HOẠT ĐỘNG

**Thay thế trong `ContentSection`:**

```tsx
// Add drag & drop handlers
const handleDragOver = (e: React.DragEvent) => {
  e.preventDefault();
  e.stopPropagation();
};

const handleDrop = (e: React.DragEvent) => {
  e.preventDefault();
  e.stopPropagation();
  
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    
    // Validate
    if (!file.type.startsWith('video/')) {
      toast.error('Chỉ chấp nhận file video (MP4, MOV, WebM)');
      return;
    }
    
    if (file.size > 100 * 1024 * 1024) { // 100MB
      toast.error('File quá lớn. Tối đa 100MB');
      return;
    }
    
    setUploadedFile(file);
    toast.success(`Đã chọn video: ${file.name}`);
  }
};

// Update button HTML
<button
  onClick={() => fileInputRef.current?.click()}
  onDragOver={handleDragOver}
  onDrop={handleDrop}
  className="w-full p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-violet-400 transition text-center"
>
  {/* ... same content ... */}
</button>
```

## ✅ 3. SPIN CONTENT POPUP ĐẦY ĐỦ

**Tạo component mới:**

```tsx
function SpinContentModal({ open, onClose, onInsert }: {
  open: boolean;
  onClose: () => void;
  onInsert: (text: string) => void;
}) {
  const [tab, setTab] = useState<'text' | 'icon' | 'emoji'>('text');
  const [textInput, setTextInput] = useState('');
  
  const iconPresets = [
    { id: 'R1', name: 'Trái tim & Hoa', icons: ['❤️', '💕', '💗', '💓', '🌹', '🌺', '🌸', '💐'] },
    { id: 'R2', name: 'Cảm xúc vui', icons: ['😍', '🤩', '😘', '😊', '🥰', '😁', '😆', '🤗'] },
    { id: 'R3', name: 'Ngôi sao & Lấp lánh', icons: ['⭐', '✨', '🌟', '💫', '⚡', '🔥', '💥', '🎉'] },
  ];
  
  const emojiPresets = [
    { id: 'happy', name: 'Vui vẻ', emojis: ['😍', '😁', '🤩', '😆', '🥳'] },
    { id: 'love', name: 'Yêu thương', emojis: ['❤️', '💕', '💖', '💗', '💓'] },
    { id: 'fire', name: 'Nóng bỏng', emojis: ['🔥', '💥', '⚡', '💯', '🚀'] },
  ];
  
  const textExample = '{Đặt chỗ để được giảm giá 50% hôm nay.|Đặt lịch ngay để giữ ưu đãi.|Nhắn tin để tư vấn miễn phí.}';
  
  const insertSpin = (snippet: string) => {
    onInsert(snippet);
    onClose();
  };
  
  if (!open) return null;
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-3xl max-h-[80vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">🔄 Spin Nội dung</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setTab('text')}
            className={`flex-1 py-3 text-sm font-medium ${tab === 'text' ? 'text-violet-600 border-b-2 border-violet-600' : 'text-gray-500'}`}
          >
            📝 Spin Text
          </button>
          <button
            onClick={() => setTab('icon')}
            className={`flex-1 py-3 text-sm font-medium ${tab === 'icon' ? 'text-violet-600 border-b-2 border-violet-600' : 'text-gray-500'}`}
          >
            ✨ Spin Icon
          </button>
          <button
            onClick={() => setTab('emoji')}
            className={`flex-1 py-3 text-sm font-medium ${tab === 'emoji' ? 'text-violet-600 border-b-2 border-violet-600' : 'text-gray-500'}`}
          >
            😍 Spin Emoji
          </button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Tab: Spin Text */}
          {tab === 'text' && (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <p className="text-sm text-blue-900 font-medium mb-2">💡 Cú pháp:</p>
                <code className="text-sm text-blue-700 bg-blue-100 px-2 py-1 rounded">
                  {'{'}lựa chọn 1|lựa chọn 2|lựa chọn 3{'}'}
                </code>
                <p className="text-xs text-blue-600 mt-2">
                  Mỗi lần đăng, hệ thống sẽ chọn ngẫu nhiên 1 câu trong ngoặc {'{}'}
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Ví dụ sẵn có:</label>
                <button
                  onClick={() => insertSpin(textExample)}
                  className="w-full text-left p-3 border border-gray-200 rounded-xl hover:bg-gray-50"
                >
                  <code className="text-sm text-violet-600">{textExample}</code>
                </button>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Hoặc tự tạo:</label>
                <textarea
                  className="w-full border border-gray-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-violet-500"
                  rows={3}
                  placeholder="Nhập các lựa chọn, cách nhau bởi dấu |"
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                />
                <button
                  onClick={() => textInput && insertSpin(`{${textInput}}`)}
                  disabled={!textInput.trim()}
                  className="mt-2 w-full py-2 bg-violet-600 text-white rounded-lg disabled:opacity-50"
                >
                  Chèn vào nội dung
                </button>
              </div>
            </div>
          )}
          
          {/* Tab: Spin Icon */}
          {tab === 'icon' && (
            <div className="space-y-4">
              <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
                <p className="text-sm text-purple-900 font-medium mb-2">✨ Cú pháp:</p>
                <code className="text-sm text-purple-700 bg-purple-100 px-2 py-1 rounded">
                  @icon{'{'}R1{'}'}
                </code>
                <p className="text-xs text-purple-600 mt-2">
                  Chọn ngẫu nhiên 1 icon từ bộ preset
                </p>
              </div>
              
              {iconPresets.map(preset => (
                <div key={preset.id} className="border border-gray-200 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">{preset.name}</h4>
                    <button
                      onClick={() => insertSpin(`@icon{${preset.id}}`)}
                      className="px-3 py-1 bg-violet-100 text-violet-700 rounded-lg text-sm hover:bg-violet-200"
                    >
                      Chèn @icon{'{' + preset.id + '}'}
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {preset.icons.map((icon, i) => (
                      <span key={i} className="text-2xl">{icon}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Tab: Spin Emoji */}
          {tab === 'emoji' && (
            <div className="space-y-4">
              <div className="bg-pink-50 border border-pink-200 rounded-xl p-4">
                <p className="text-sm text-pink-900 font-medium mb-2">😍 Cú pháp:</p>
                <code className="text-sm text-pink-700 bg-pink-100 px-2 py-1 rounded">
                  @emoji{'{'}happy{'}'}
                </code>
                <p className="text-xs text-pink-600 mt-2">
                  Chọn ngẫu nhiên 1 emoji từ nhóm cảm xúc
                </p>
              </div>
              
              {emojiPresets.map(preset => (
                <div key={preset.id} className="border border-gray-200 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">{preset.name}</h4>
                    <button
                      onClick={() => insertSpin(`@emoji{${preset.id}}`)}
                      className="px-3 py-1 bg-violet-100 text-violet-700 rounded-lg text-sm hover:bg-violet-200"
                    >
                      Chèn @emoji{'{' + preset.id + '}'}
                    </button>
                  </div>
                  <div className="flex gap-2">
                    {preset.emojis.map((emoji, i) => (
                      <span key={i} className="text-2xl">{emoji}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-600">
              💡 <strong>Kết hợp nhiều spin:</strong> 
              <code className="ml-2 text-xs bg-white px-2 py-1 rounded">
                💖 {'{'}INBOX NOW! 60% OFF|Đặt lịch hôm nay giảm 50%!{'}'} @icon{'{'}R1{'}'} @emoji{'{'}happy{'}'}
              </code>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Thêm vào `AdStudioCard` state:**

```tsx
const [showSpinModal, setShowSpinModal] = useState(false);

// Replace button in ContentSection
<button
  onClick={() => setShowSpinModal(true)}
  className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition flex items-center gap-1"
>
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
  Spin nội dung
</button>

// Add modal before closing </div>
<SpinContentModal
  open={showSpinModal}
  onClose={() => setShowSpinModal(false)}
  onInsert={(text) => {
    setCaption(caption + ' ' + text);
    toast.success('Đã chèn spin!');
  }}
/>
```

## ✅ 4. FILTER NHÓM KÊNH

**Update `SettingsSection` - Channel Drawer:**

```tsx
// Add state
const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);

// Filter logic
const filteredChannels = channels.filter(c => {
  const matchesSearch = c.page_name.toLowerCase().includes(channelSearch.toLowerCase());
  const matchesGroup = !selectedGroupId || c.channel_group_id === selectedGroupId;
  return matchesSearch && matchesGroup;
});

// Add group filter UI before Search
<div className="p-4 border-b border-gray-100">
  <label className="block text-xs font-medium text-gray-600 mb-2">Lọc theo nhóm kênh</label>
  <select
    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 text-sm bg-white"
    value={selectedGroupId || ''}
    onChange={(e) => setSelectedGroupId(e.target.value || null)}
  >
    <option value="">Tất cả nhóm</option>
    {groups.map(g => (
      <option key={g.id} value={g.id}>{g.name}</option>
    ))}
  </select>
</div>

// Update channel list to show group badges
{filteredChannels.map(ch => (
  <label key={ch.id} className="...">
    {/* ... existing content ... */}
    <div className="flex-1 min-w-0">
      <p className="font-medium text-gray-900 truncate">{ch.page_name}</p>
      <div className="flex items-center gap-2 mt-1">
        <p className="text-xs text-gray-500">Fanpage</p>
        {ch.channel_group_id && (() => {
          const group = groups.find(g => g.id === ch.channel_group_id);
          return group ? (
            <span
              className="px-2 py-0.5 rounded text-xs font-medium"
              style={{
                backgroundColor: group.color_hex + '20',
                color: group.color_hex
              }}
            >
              {group.name}
            </span>
          ) : null;
        })()}
      </div>
    </div>
  </label>
))}
```

## ✅ 5. RESPONSIVE & MAX-WIDTH

**Update main container:**

```tsx
// Replace max-w-7xl with max-w-[1800px] for wider screens
<main className="max-w-[1800px] mx-auto px-4 py-6">
  <div className="grid grid-cols-1 lg:grid-cols-10 gap-6">
    {/* Left: 7/10 = 70% */}
    <div className="lg:col-span-7 space-y-4">
      {/* ... */}
    </div>
    
    {/* Right: 3/10 = 30% */}
    <div className="lg:col-span-3">
      {/* ... */}
    </div>
  </div>
</main>
```

## ✅ 6. BACKEND VIDEO TITLE SUPPORT

**API endpoint cần thêm param:**

```python
# app/api/routes/posts.py (hoặc tương đương)

@router.post("/schedule")
async def schedule_post(
    payload: SchedulePostPayload,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    # ...
    
    if payload.post_type == 'reel' and payload.title:
        # Facebook Reels API có thể set title trong một số case
        # Tham khảo: https://developers.facebook.com/docs/video-api/guides/reels
        params['title'] = payload.title
    
    # Post to Facebook Graph API
    # ...
```

## 📝 Checklist Implementation

### Backend
- [ ] Fix `/api/tiktok/scrape` error handling
- [ ] Add video title support for Reels
- [ ] Test all error codes (INVALID_URL, PRIVATE_VIDEO, etc.)

### Frontend
- [ ] Add drag & drop handlers to upload zone
- [ ] Create `SpinContentModal` component
- [ ] Add group filter to channel drawer
- [ ] Show group badges in channel list
- [ ] Update max-width to 1800px
- [ ] Test responsive on mobile/tablet

### Testing
- [ ] Test TikTok scrape with various URLs
- [ ] Test drag & drop video upload
- [ ] Test spin text/icon/emoji insertion
- [ ] Test channel group filtering
- [ ] Test form submission (draft & schedule)
- [ ] Test validation messages

## 🚀 Deployment

1. **Backend:**
   ```bash
   cd /home/adsuser/ads-automation
   git pull origin main
   sudo supervisorctl restart ads-automation
   ```

2. **Frontend:**
   ```bash
   cd /home/adsuser/ads-automation/frontend
   npm run build
   ```

3. **Verify:**
   - Visit `/ad-studio`
   - Test complete flow: Paste link → Edit content → Select channels → Schedule
