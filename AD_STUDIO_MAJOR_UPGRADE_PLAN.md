# 🎨 AD STUDIO MAJOR UPGRADE - IMPLEMENTATION PLAN

**Date:** December 2, 2025  
**Status:** IN PROGRESS  
**Scope:** 10 major features + UI/UX overhaul

---

## ✅ COMPLETED

### 1. Backend - TikTok Scrape Retry Logic
- ✅ Added `asyncio` import
- ✅ Retry mechanism: 2 attempts with 2s delay between
- ✅ 180s timeout per attempt
- ✅ Detailed error logging
- ✅ User-friendly Vietnamese error messages

**Files changed:**
- `app/api/routes/ad_studio.py` - Added retry loop

---

## 🚧 IN PROGRESS

### 2. Layout Expansion & Preview Rename
**Requirements:**
- Max-width: `1800px` (currently `max-w-[1800px]` ✅ already done)
- Change "Video Preview" → "Xem trước"
- Support multiple media types (Reel, Video, Photo, Album)

**Implementation:**
```tsx
// VideoPreview component rename to MediaPreview
function MediaPreview({
  mediaType, // 'reel' | 'video' | 'photo' | 'album'
  previewMode, // 'mobile' | 'desktop'
  ...
})
```

---

## 📋 PLANNED FEATURES

### 3. Mobile/PC Preview Toggle
```tsx
const [previewMode, setPreviewMode] = useState<'mobile' | 'desktop'>('mobile');

<div className="flex gap-2 mb-4">
  <button onClick={() => setPreviewMode('mobile')}>
    📱 Mobile
  </button>
  <button onClick={() => setPreviewMode('desktop')}>
    🖥️ PC
  </button>
</div>
```

### 4. Auto-Expand Textarea (300px minimum)
```tsx
const [caption, setCaption] = useState('');
const textareaRef = useRef<HTMLTextAreaElement>(null);

useEffect(() => {
  if (textareaRef.current) {
    textareaRef.current.style.height = 'auto';
    textareaRef.current.style.height = `${Math.max(300, textareaRef.current.scrollHeight)}px`;
  }
}, [caption]);

<textarea
  ref={textareaRef}
  value={caption}
  onChange={(e) => setCaption(e.target.value)}
  style={{ minHeight: '300px' }}
  className="resize-none overflow-hidden"
/>
<div className="text-xs text-gray-500">
  {caption.length} / 2200 ký tự
</div>
```

### 5. Comprehensive Spin Content Modal

**3 Tabs with extensive content:**

#### Tab 1: Text Spin
- Syntax: `{A|B|C}`
- 20+ examples with copy buttons
- Live preview

#### Tab 2: Icon Spin (200 icons)
**Categories:**
- ❤️ Love (20 icons): ❤️💖💗💘💕💓💞💝💟💌🫀❣️💋💏💑
- 👍 Reactions (20 icons): 👍👏🙌👌🤝💪🤘✌️🤞👊
- ✨ Magic (20 icons): ✨💫⭐🌟⚡💥🔥💎👑🎯
- 💄 Beauty (20 icons): 💄💅💋👄👁️👀💆💇🧖
- 💉 Medical (20 icons): 💉💊🩹🩺🏥⚕️🔬💉🩸
- 🎁 Gifts (20 icons): 🎁🎀🎊🎉🎈🎂🍰🧁
- 🎯 Target (20 icons): 🎯🔝⬆️📈💹🚀📊💰

**Syntax:**
```
@icon{love} → random from love category
@icon{R1} → random from preset group 1
```

#### Tab 3: Emoji Spin (300 emojis)
**Categories (30 groups × 10 emojis each):**
- 😊 Happy: 😊😃😄😁😆😅🤣😂🙂🙃
- ❤️ Love: ❤️💕💖💗💘💝💞💓💟💌
- 🎉 Celebration: 🎉🎊🥳🎈🎆🎇✨🎁🎀
- 🔥 Fire: 🔥💥⚡✨💫🌟⭐💯🏆
- 😢 Sad: 😢😭😿💔😔😞😓😥
- ... (25 more groups)

**Syntax:**
```
@emoji{happy} → random from happy group
@emoji{love} → random from love group
```

### 6. Fix Drag & Drop + Image Upload
```tsx
const handleDragOver = (e: React.DragEvent) => {
  e.preventDefault();
  e.stopPropagation();
  setIsDragging(true);
};

const handleDrop = (e: React.DragEvent) => {
  e.preventDefault();
  e.stopPropagation();
  setIsDragging(false);
  
  const files = Array.from(e.dataTransfer.files);
  
  // Support both video and images
  const validFiles = files.filter(f => 
    f.type.startsWith('video/') || f.type.startsWith('image/')
  );
  
  if (validFiles.length === 0) {
    toast.error('Chỉ chấp nhận file video hoặc ảnh');
    return;
  }
  
  if (validFiles.length === 1 && validFiles[0].type.startsWith('video/')) {
    setUploadedFile(validFiles[0]);
    setMediaType('video');
  } else {
    setUploadedImages(validFiles);
    setMediaType(validFiles.length > 1 ? 'album' : 'photo');
  }
};
```

### 7. 90% Facebook-like Preview

**Elements to include:**
```tsx
<div className={`preview-container ${previewMode === 'mobile' ? 'w-[375px]' : 'w-[500px]'}`}>
  {/* Header */}
  <div className="flex items-center gap-2 p-3">
    <img src={fanpage.avatar} className="w-10 h-10 rounded-full" />
    <div>
      <div className="flex items-center gap-1">
        <span className="font-semibold">{fanpage.name}</span>
        {fanpage.verified && <img src="/verified-badge.svg" className="w-4 h-4" />}
      </div>
      <span className="text-xs text-gray-500">5 phút trước • 🌎</span>
    </div>
  </div>
  
  {/* Content with line breaks */}
  <div className="px-3 pb-2 whitespace-pre-wrap">{caption}</div>
  
  {/* Media */}
  {mediaType === 'reel' && (
    <div className="relative bg-black aspect-[9/16]">
      <video src={videoUrl} className="w-full h-full object-cover" />
      <div className="absolute bottom-4 left-4">
        <span className="text-white">🎵 {musicTitle}</span>
      </div>
    </div>
  )}
  
  {mediaType === 'photo' && (
    <img src={imageUrl} className="w-full" />
  )}
  
  {mediaType === 'album' && (
    <div className="grid grid-cols-2 gap-0.5">
      {images.map((img, i) => (
        <img key={i} src={img} className="w-full aspect-square object-cover" />
      ))}
    </div>
  )}
  
  {/* CTA Button */}
  {cta && (
    <div className="px-3 pt-2">
      <button className="w-full py-2 bg-blue-100 text-blue-600 rounded-lg font-semibold">
        {cta}
      </button>
    </div>
  )}
  
  {/* Stats */}
  <div className="flex items-center justify-between px-3 py-2 border-t">
    <span className="text-sm text-gray-500">👍❤️😆 1.2K</span>
    <span className="text-sm text-gray-500">50 bình luận • 12 chia sẻ</span>
  </div>
  
  {/* Actions */}
  <div className="flex items-center border-t border-b py-1">
    <button className="flex-1 flex items-center justify-center gap-2 py-2 hover:bg-gray-100">
      <span>👍</span> Thích
    </button>
    <button className="flex-1 flex items-center justify-center gap-2 py-2 hover:bg-gray-100">
      <span>💬</span> Bình luận
    </button>
    <button className="flex-1 flex items-center justify-center gap-2 py-2 hover:bg-gray-100">
      <span>↗️</span> Chia sẻ
    </button>
  </div>
</div>
```

### 8. Channel Group Selector
**Already implemented** in previous refactor ✅
- Group filter pills with colors
- Combine with search

### 9. Video Title Input
```tsx
{postType === 'video' && (
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-2">
      Tiêu đề video
    </label>
    <input
      type="text"
      className="w-full px-4 py-2 border border-gray-200 rounded-xl"
      placeholder="Nhập tiêu đề cho video..."
      value={videoTitle}
      onChange={(e) => setVideoTitle(e.target.value)}
      maxLength={100}
    />
    <p className="text-xs text-gray-500 mt-1">
      {videoTitle.length}/100 ký tự
    </p>
  </div>
)}
```

### 10. Navigation Links
```tsx
<nav className="bg-white border-b border-gray-200">
  <div className="max-w-[1800px] mx-auto px-4 py-3">
    <div className="flex items-center gap-6">
      <Link to="/dashboard" className="flex items-center gap-2 hover:text-violet-600">
        <svg>...</svg> Dashboard
      </Link>
      <Link to="/posts" className="flex items-center gap-2 hover:text-violet-600">
        <svg>...</svg> Quản lý bài đăng
      </Link>
      <Link to="/channels" className="flex items-center gap-2 hover:text-violet-600">
        <svg>...</svg> Quản lý kênh
      </Link>
      <Link to="/channel-groups" className="flex items-center gap-2 hover:text-violet-600">
        <svg>...</svg> Nhóm fanpage
      </Link>
      <Link to="/settings" className="flex items-center gap-2 hover:text-violet-600">
        <svg>...</svg> Cấu hình
      </Link>
      <Link to="/auto-comments" className="flex items-center gap-2 hover:text-violet-600">
        <svg>...</svg> Bình luận tự động
      </Link>
      <Link to="/library" className="flex items-center gap-2 hover:text-violet-600">
        <svg>...</svg> Thư viện chiến lược
      </Link>
    </div>
  </div>
</nav>
```

---

## 📊 IMPLEMENTATION PRIORITY

**Phase 1 - Critical UX (Do first):**
1. ✅ Backend retry logic
2. Auto-expand textarea
3. Fix drag & drop
4. Comprehensive Spin Modal

**Phase 2 - Preview Enhancement:**
5. Mobile/PC preview toggle
6. 90% Facebook preview
7. Image upload support

**Phase 3 - Polish:**
8. Video title field
9. Navigation links
10. Responsive mobile layout

---

## ⚠️ IMPORTANT NOTES

1. **KHÔNG TẠO FILE MỚI** - Refactor trực tiếp `AdStudioCard.tsx`
2. **Spin Modal** phải có đầy đủ 200 icons + 300 emojis với UI đẹp
3. **Preview** phải giống Facebook 90% (avatar, verified, CTA, line-break preserved)
4. **Drag & Drop** phải ngăn browser mở tab mới bằng `e.preventDefault()`
5. **Textarea** tự động mở rộng theo nội dung, min 300px

---

## 🧪 TESTING CHECKLIST

- [ ] TikTok scrape retry khi lỗi lần 1
- [ ] Drag video vào không mở tab mới
- [ ] Drag ảnh vào hiển thị preview ảnh
- [ ] Drag nhiều ảnh tạo album
- [ ] Textarea tự expand khi gõ nhiều dòng
- [ ] Character counter realtime
- [ ] Spin modal mở đầy đủ 3 tabs
- [ ] Copy button trong spin modal hoạt động
- [ ] Preview mode toggle Mobile/PC
- [ ] Facebook preview hiển thị đúng line-break
- [ ] CTA button hiển thị trong preview
- [ ] Verified badge hiển thị
- [ ] Navigation links hoạt động

---

## 📝 NEXT STEPS

Bạn muốn tôi:
1. **Implement từng feature một** (tôi sẽ làm từng phần, bạn test xong mới làm tiếp)
2. **Implement tất cả cùng lúc** (tôi làm hết, push 1 lần, bạn test toàn bộ)
3. **Chỉ implement top 5 features quan trọng nhất** (nhanh hơn)

Lựa chọn nào phù hợp với bạn? 🚀
