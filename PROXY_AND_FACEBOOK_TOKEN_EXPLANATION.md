# 🌏 Giải thích về Proxy và Token Facebook Thái Lan

## ❓ Câu hỏi

**Nếu dùng token Facebook Thái Lan (đang được đăng nhập ở Thái Lan) thì có thể sử dụng để tìm kiếm ở Thái Lan không? Hay phải gắn thêm proxy?**

## 📝 Giải thích chi tiết

### 1. **Token Facebook và Location**

#### Token Facebook hoạt động như thế nào?
- **Token Facebook** là một chuỗi mã hóa xác thực quyền truy cập vào Facebook API
- Token **KHÔNG** chứa thông tin về vị trí địa lý (location) của bạn
- Token chỉ xác thực **quyền truy cập** và **quyền hạn** (permissions) của bạn

#### Token Thái Lan có thể tìm kiếm ở Thái Lan không?
✅ **CÓ, nhưng có điều kiện:**

1. **Facebook Ads Library API:**
   - Facebook Ads Library **KHÔNG** giới hạn theo token location
   - Bạn có thể tìm kiếm ads ở **BẤT KỲ QUỐC GIA NÀO** với token bất kỳ
   - API cho phép bạn chỉ định `country` parameter khi search

2. **Ví dụ với ScrapeGraphAI:**
   ```python
   # Bạn có thể search ads ở Thái Lan với token từ bất kỳ đâu
   search_competitor_ads_by_keyword(
       keyword="laptop",
       country="TH",  # Thái Lan
       limit=20
   )
   ```

### 2. **Proxy là gì và khi nào cần?**

#### Proxy là gì?
- **Proxy** là một server trung gian giữa bạn và internet
- Khi bạn gửi request, nó đi qua proxy trước, rồi mới đến đích
- Proxy có thể **ẩn IP thật** của bạn và **thay đổi vị trí địa lý** của request

#### Khi nào cần proxy?

##### ❌ **KHÔNG CẦN PROXY** nếu:
1. **Chỉ dùng Facebook API:**
   - Facebook API (Graph API, Marketing API) **KHÔNG** giới hạn theo IP location
   - Bạn có thể gọi API từ bất kỳ đâu trên thế giới
   - Token là đủ để xác thực

2. **Dùng ScrapeGraphAI:**
   - ScrapeGraphAI là service bên thứ 3, họ tự xử lý proxy/scraping
   - Bạn chỉ cần API key, không cần proxy

3. **Tìm kiếm Ads Library:**
   - Facebook Ads Library API cho phép chỉ định `country` parameter
   - Không cần proxy để search theo quốc gia

##### ✅ **CẦN PROXY** nếu:
1. **Web Scraping trực tiếp:**
   - Nếu bạn tự scrape Facebook website (không dùng API)
   - Facebook có thể block IP nếu detect scraping
   - Proxy giúp rotate IP để tránh block

2. **Rate limiting:**
   - Nếu bạn gọi quá nhiều requests từ cùng 1 IP
   - Proxy giúp phân tán requests

3. **Geo-restricted content:**
   - Một số nội dung chỉ hiển thị ở quốc gia cụ thể
   - Proxy giúp "giả mạo" location để truy cập

### 3. **Trường hợp của bạn**

#### Bạn đang dùng ScrapeGraphAI:
- ✅ **KHÔNG CẦN PROXY**
- ScrapeGraphAI đã tự xử lý scraping và proxy
- Bạn chỉ cần:
  1. Token Facebook (từ bất kỳ đâu)
  2. ScrapeGraphAI API key
  3. Gọi API với `country` parameter nếu muốn search theo quốc gia

#### Token Thái Lan + Tìm kiếm ở Thái Lan:
- ✅ **HOẠT ĐỘNG BÌNH THƯỜNG**
- Token Thái Lan không có nghĩa là bạn chỉ có thể search ở Thái Lan
- Bạn có thể search ở **BẤT KỲ QUỐC GIA NÀO**
- Chỉ cần chỉ định `country` parameter trong API call

### 4. **Ví dụ thực tế**

```python
# Token từ Thái Lan, nhưng search ở Việt Nam
search_competitor_ads_by_keyword(
    keyword="điện thoại",
    country="VN",  # Việt Nam
    limit=20
)

# Token từ Việt Nam, nhưng search ở Thái Lan
search_competitor_ads_by_keyword(
    keyword="laptop",
    country="TH",  # Thái Lan
    limit=20
)

# Cả 2 đều hoạt động bình thường!
```

### 5. **Gói của bạn không cho phép cấu hình proxy**

#### Không sao cả! ✅
- Với ScrapeGraphAI, bạn **KHÔNG CẦN** proxy
- ScrapeGraphAI đã xử lý tất cả:
  - Proxy rotation
  - IP rotation
  - Anti-detection
  - Rate limiting

#### Bạn chỉ cần:
1. ✅ Token Facebook (bất kỳ location nào)
2. ✅ ScrapeGraphAI API key
3. ✅ Gọi API với `country` parameter

### 6. **Tóm tắt**

| Yếu tố | Cần thiết? | Lý do |
|--------|-----------|-------|
| Token Facebook Thái Lan | ✅ Cần | Xác thực quyền truy cập |
| Proxy | ❌ Không cần | ScrapeGraphAI tự xử lý |
| Country parameter | ✅ Nên có | Để search theo quốc gia cụ thể |
| IP từ Thái Lan | ❌ Không cần | API không giới hạn theo IP |

### 7. **Kết luận**

✅ **Bạn có thể:**
- Dùng token Facebook Thái Lan để search ads ở **BẤT KỲ QUỐC GIA NÀO**
- Không cần proxy
- Chỉ cần chỉ định `country` parameter trong API call

❌ **Bạn không cần:**
- Proxy
- IP từ Thái Lan
- Cấu hình phức tạp

🎯 **Cách làm:**
1. Lấy token Facebook (từ bất kỳ đâu)
2. Lấy ScrapeGraphAI API key
3. Gọi API với `country="TH"` để search ở Thái Lan
4. Xong! 🎉

