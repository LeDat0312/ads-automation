# 🔐 PHÂN TÍCH: FACEBOOK OAUTH LOGIN & CUSTOM LOGIC UI

## 📋 TỔNG QUAN

Tích hợp Facebook OAuth để:
1. **Đăng nhập Facebook** → Lấy token full quyền
2. **Quản lý nhiều tài khoản** → Mỗi user có thể kết nối nhiều Facebook accounts
3. **Tùy chỉnh logic** → Mỗi account có thể có logic rules riêng
4. **Giao diện quản lý** → Dashboard để cấu hình từng account/prefix

---

## 🚨 KHÓ KHĂN VÀ THÁCH THỨC

### **1. Facebook OAuth Flow Phức Tạp**

#### **Khó khăn:**
- Facebook OAuth có nhiều bước: Authorization → Callback → Exchange code → Get long-lived token
- Cần quản lý `app_id`, `app_secret`, `redirect_uri`
- Permissions phức tạp: `ads_read`, `ads_management`, `business_management`
- Token types: Short-lived (1-2h) vs Long-lived (60 days) vs Never-expiring

#### **Giải pháp:**
- Sử dụng `facebook-sdk` hoặc `httpx` để xử lý OAuth flow
- Implement token refresh mechanism tự động
- Lưu `refresh_token` để renew khi hết hạn
- Cache tokens trong database với encryption

---

### **2. Security & Token Management**

#### **Khó khăn:**
- **Lưu trữ tokens an toàn**: Không được lưu plain text
- **Encryption**: Cần encrypt tokens trước khi lưu DB
- **Token expiration**: Phải handle refresh tự động
- **Multiple tokens**: Mỗi user có thể có nhiều accounts → nhiều tokens
- **Revoked tokens**: User có thể revoke → cần detect và notify

#### **Giải pháp:**
- Sử dụng `cryptography` library để encrypt tokens
- Lưu encryption key trong environment variable (không commit)
- Implement background job để check và refresh tokens
- Store tokens với metadata: `expires_at`, `last_refreshed`, `status`
- Implement webhook từ Facebook để detect token revocation

---

### **3. Multi-Account Support**

#### **Khó khăn:**
- Mỗi user có thể kết nối nhiều Facebook accounts
- Mỗi account có nhiều Ad Accounts
- Cần phân biệt: User → Facebook Account → Ad Account → Logic Rules
- API calls phải dùng đúng token cho từng account

#### **Giải pháp:**
- Database schema: `User` → `FacebookAccount` → `AdAccount` → `LogicRule`
- Context switching: Mỗi API call phải biết dùng token nào
- UI: Dropdown để chọn account khi xem báo cáo
- Isolation: Data của account này không lẫn với account kia

---

### **4. Logic Customization Per Account**

#### **Khó khăn:**
- Logic rules hiện tại là global (từ `LogicRules` table)
- Cần support: Global rules + Account-specific rules + Prefix-specific rules
- Priority: Account > Prefix > Global
- UI phức tạp: Nhiều levels của configuration

#### **Giải pháp:**
- Extend `LogicRule` model: Thêm `account_id`, `user_id`, `is_global`
- Logic lookup: Check account-specific → prefix-specific → global
- UI: Tabs/Accordion để quản lý rules theo account
- Validation: Đảm bảo không conflict giữa các rules

---

### **5. UI/UX Complexity**

#### **Khó khăn:**
- Dashboard hiện tại chỉ hiển thị data, chưa có authentication
- Cần thêm: Login page, Account management, Rule configuration
- Responsive design cho mobile
- Real-time updates khi thay đổi rules

#### **Giải pháp:**
- Sử dụng JWT tokens cho session management
- React/Vue frontend hoặc server-side rendering với Jinja2
- WebSocket hoặc polling để real-time updates
- Component-based UI: Reusable components cho forms

---

### **6. Facebook API Rate Limits**

#### **Khó khăn:**
- Facebook có rate limits: ~200 calls/hour/user
- Nhiều accounts → nhiều API calls → dễ hit limit
- Cần queue và retry mechanism

#### **Giải pháp:**
- Implement rate limiting per account
- Queue system: Background jobs để spread API calls
- Caching: Cache API responses khi có thể
- Exponential backoff khi hit rate limit

---

### **7. Error Handling & Monitoring**

#### **Khó khăn:**
- Token expired → cần refresh tự động
- Permission denied → cần notify user
- API errors → cần log và retry
- Network issues → cần handle gracefully

#### **Giải pháp:**
- Comprehensive error handling với try-catch
- Logging: Structured logging với levels
- Monitoring: Alert khi token expires hoặc API fails
- User notifications: Telegram/Email khi có issues

---

## 🏗️ KIẾN TRÚC ĐỀ XUẤT

### **Database Schema**

```python
# app/models/user.py
class User(Base):
    """User model - người dùng hệ thống"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)  # Bcrypt hashed
    name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# app/models/facebook_account.py
class FacebookAccount(Base):
    """Facebook Account - tài khoản Facebook đã kết nối"""
    __tablename__ = "facebook_accounts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    facebook_user_id = Column(String, unique=True, index=True)  # Facebook User ID
    facebook_name = Column(String)  # Tên Facebook
    access_token_encrypted = Column(Text)  # Encrypted token
    refresh_token_encrypted = Column(Text)  # Encrypted refresh token
    token_expires_at = Column(DateTime)  # Token expiration
    last_refreshed_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    permissions = Column(JSON)  # List of permissions granted
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# app/models/ad_account.py
class AdAccount(Base):
    """Ad Account - tài khoản quảng cáo Facebook"""
    __tablename__ = "ad_accounts"
    
    id = Column(Integer, primary_key=True)
    facebook_account_id = Column(Integer, ForeignKey("facebook_accounts.id"), index=True)
    account_id = Column(String, unique=True, index=True)  # act_123456789
    account_name = Column(String)
    currency = Column(String)  # VND, USD, etc.
    timezone = Column(String)  # Asia/Ho_Chi_Minh
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# Extend LogicRule model
# app/models/logic_rule.py (existing, extend)
class LogicRule(Base):
    # ... existing fields ...
    
    # NEW FIELDS:
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    facebook_account_id = Column(Integer, ForeignKey("facebook_accounts.id"), nullable=True, index=True)
    ad_account_id = Column(Integer, ForeignKey("ad_accounts.id"), nullable=True, index=True)
    is_global = Column(Boolean, default=False)  # True = global rule, False = account-specific
    priority = Column(Integer, default=0)  # Higher = more priority
```

---

### **API Endpoints**

```python
# app/api/routes/auth.py
@router.post("/auth/login")
async def login(email: str, password: str):
    """Login với email/password"""
    pass

@router.post("/auth/logout")
async def logout():
    """Logout"""
    pass

# app/api/routes/facebook_oauth.py
@router.get("/auth/facebook/login")
async def facebook_login():
    """Redirect to Facebook OAuth"""
    pass

@router.get("/auth/facebook/callback")
async def facebook_callback(code: str, state: str):
    """Handle Facebook OAuth callback"""
    pass

@router.get("/api/facebook/accounts")
async def list_facebook_accounts(user_id: int):
    """List all Facebook accounts của user"""
    pass

@router.post("/api/facebook/accounts/{account_id}/refresh-token")
async def refresh_token(account_id: int):
    """Refresh Facebook token"""
    pass

# app/api/routes/logic_rules.py
@router.get("/api/logic-rules")
async def list_logic_rules(account_id: Optional[int] = None):
    """List logic rules (global + account-specific)"""
    pass

@router.post("/api/logic-rules")
async def create_logic_rule(rule: LogicRuleCreate):
    """Create new logic rule"""
    pass

@router.put("/api/logic-rules/{rule_id}")
async def update_logic_rule(rule_id: int, rule: LogicRuleUpdate):
    """Update logic rule"""
    pass

@router.delete("/api/logic-rules/{rule_id}")
async def delete_logic_rule(rule_id: int):
    """Delete logic rule"""
    pass
```

---

### **Services**

```python
# app/services/facebook_oauth.py
class FacebookOAuthService:
    """Service để xử lý Facebook OAuth"""
    
    def get_authorization_url(self, state: str) -> str:
        """Generate Facebook OAuth URL"""
        pass
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        pass
    
    async def get_long_lived_token(self, short_token: str) -> dict:
        """Exchange short-lived token for long-lived token"""
        pass
    
    async def refresh_token(self, refresh_token: str) -> dict:
        """Refresh long-lived token"""
        pass
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get Facebook user info"""
        pass
    
    async def get_ad_accounts(self, access_token: str) -> list:
        """Get all ad accounts của user"""
        pass

# app/services/token_manager.py
class TokenManager:
    """Service để quản lý tokens (encrypt/decrypt, refresh)"""
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt token trước khi lưu DB"""
        pass
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt token từ DB"""
        pass
    
    async def get_valid_token(self, facebook_account_id: int) -> str:
        """Get valid token (refresh nếu cần)"""
        pass
    
    async def check_and_refresh_tokens(self):
        """Background job: Check và refresh tokens sắp hết hạn"""
        pass
```

---

## 📝 ROADMAP IMPLEMENTATION

### **Phase 1: Foundation (Week 1-2)**

1. **Database Models**
   - [ ] Create `User` model
   - [ ] Create `FacebookAccount` model
   - [ ] Create `AdAccount` model
   - [ ] Extend `LogicRule` model với account-specific fields
   - [ ] Create migrations

2. **Authentication System**
   - [ ] Implement JWT token generation
   - [ ] Create login/logout endpoints
   - [ ] Password hashing với bcrypt
   - [ ] Session management

3. **Facebook OAuth Basic**
   - [ ] Setup Facebook App (trên Facebook Developers)
   - [ ] Implement OAuth flow (login → callback → token)
   - [ ] Store tokens trong database (encrypted)

---

### **Phase 2: Token Management (Week 3)**

1. **Token Encryption**
   - [ ] Implement encryption/decryption service
   - [ ] Store encryption key trong environment
   - [ ] Test token storage và retrieval

2. **Token Refresh**
   - [ ] Implement long-lived token exchange
   - [ ] Background job để refresh tokens
   - [ ] Handle token expiration errors

3. **Multi-Account Support**
   - [ ] UI để list Facebook accounts
   - [ ] Context switching khi gọi API
   - [ ] Test với nhiều accounts

---

### **Phase 3: Logic Customization (Week 4-5)**

1. **Logic Rule Extension**
   - [ ] Update `LogicRule` model
   - [ ] Implement logic lookup (account → prefix → global)
   - [ ] Update automation service để dùng account-specific rules

2. **UI for Rule Management**
   - [ ] Create rule management page
   - [ ] Form để create/edit rules
   - [ ] Visual rule builder (optional)

3. **Testing**
   - [ ] Test với multiple accounts
   - [ ] Test rule priority
   - [ ] Test automation với custom rules

---

### **Phase 4: UI/UX (Week 6-7)**

1. **Dashboard Enhancement**
   - [ ] Add authentication to dashboard
   - [ ] Account selector dropdown
   - [ ] Rule management UI
   - [ ] Real-time updates

2. **Mobile Responsive**
   - [ ] Responsive design
   - [ ] Mobile-friendly forms
   - [ ] Touch-friendly buttons

3. **User Experience**
   - [ ] Loading states
   - [ ] Error messages
   - [ ] Success notifications
   - [ ] Help tooltips

---

### **Phase 5: Production Ready (Week 8)**

1. **Security Hardening**
   - [ ] Security audit
   - [ ] Rate limiting
   - [ ] Input validation
   - [ ] SQL injection prevention

2. **Monitoring & Logging**
   - [ ] Structured logging
   - [ ] Error tracking
   - [ ] Performance monitoring
   - [ ] Alert system

3. **Documentation**
   - [ ] API documentation
   - [ ] User guide
   - [ ] Developer guide
   - [ ] Deployment guide

---

## 🔧 TECHNICAL STACK

### **Backend:**
- **FastAPI** (existing)
- **SQLAlchemy** (existing)
- **JWT** (`python-jose`, `passlib`)
- **Cryptography** (`cryptography`)
- **Facebook SDK** (`facebook-sdk` hoặc `httpx`)

### **Frontend:**
- **React** hoặc **Vue** (SPA)
- Hoặc **Jinja2** templates (server-side rendering)
- **Bootstrap** hoặc **Tailwind CSS**

### **Background Jobs:**
- **Celery** hoặc **APScheduler** (existing job queue)
- Token refresh jobs
- Token expiration checks

---

## 📊 ESTIMATED EFFORT

- **Phase 1**: 2 weeks (Foundation)
- **Phase 2**: 1 week (Token Management)
- **Phase 3**: 2 weeks (Logic Customization)
- **Phase 4**: 2 weeks (UI/UX)
- **Phase 5**: 1 week (Production Ready)

**Total: ~8 weeks** (có thể rút ngắn nếu focus vào core features)

---

## ⚠️ RISKS & MITIGATION

### **Risk 1: Facebook API Changes**
- **Mitigation**: Version pinning, monitor Facebook changelog

### **Risk 2: Token Security Breach**
- **Mitigation**: Encryption, regular security audits, access logging

### **Risk 3: Complex UI**
- **Mitigation**: Start simple, iterate based on feedback

### **Risk 4: Performance với nhiều accounts**
- **Mitigation**: Caching, async processing, rate limiting

---

## ✅ NEXT STEPS

1. **Review và approve** architecture này
2. **Setup Facebook App** trên Facebook Developers
3. **Start Phase 1**: Database models và authentication
4. **Iterate** dựa trên feedback

---

## 📚 REFERENCES

- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login/)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [OAuth 2.0 Flow](https://oauth.net/2/)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)



