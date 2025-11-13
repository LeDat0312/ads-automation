# 🚀 HƯỚNG DẪN TRIỂN KHAI: FACEBOOK OAUTH & CUSTOM LOGIC

## 📋 TÓM TẮT NHANH

Tài liệu này hướng dẫn từng bước để implement Facebook OAuth login và giao diện tùy chỉnh logic.

---

## 🎯 MỤC TIÊU

1. ✅ User đăng nhập Facebook → Lấy token full quyền
2. ✅ Quản lý nhiều Facebook accounts
3. ✅ Tùy chỉnh logic rules cho từng account/prefix
4. ✅ Giao diện web để quản lý

---

## 🔧 BƯỚC 1: SETUP FACEBOOK APP

### **1.1. Tạo Facebook App**

1. Vào [Facebook Developers](https://developers.facebook.com/)
2. Tạo App mới → Chọn "Business" type
3. Thêm "Facebook Login" product
4. Lấy `App ID` và `App Secret`

### **1.2. Cấu hình OAuth Redirect URIs**

Trong Facebook App Settings:
- **Valid OAuth Redirect URIs**: 
  - `https://updatemetaads.site/auth/facebook/callback`
  - `http://localhost:8000/auth/facebook/callback` (dev)

### **1.3. Request Permissions**

Cần các permissions:
- `ads_read` - Đọc quảng cáo
- `ads_management` - Quản lý quảng cáo
- `business_management` - Quản lý Business Manager
- `pages_read_engagement` - Đọc pages

---

## 🗄️ BƯỚC 2: DATABASE MODELS

### **2.1. Tạo Models**

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

```python
# app/models/facebook_account.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from app.core.database import Base
from datetime import datetime

class FacebookAccount(Base):
    __tablename__ = "facebook_accounts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    facebook_user_id = Column(String, unique=True, index=True)
    facebook_name = Column(String)
    access_token_encrypted = Column(Text)
    refresh_token_encrypted = Column(Text)
    token_expires_at = Column(DateTime)
    last_refreshed_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    permissions = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

```python
# app/models/ad_account.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base
from datetime import datetime

class AdAccount(Base):
    __tablename__ = "ad_accounts"
    
    id = Column(Integer, primary_key=True)
    facebook_account_id = Column(Integer, ForeignKey("facebook_accounts.id"), index=True)
    account_id = Column(String, unique=True, index=True)  # act_123456789
    account_name = Column(String)
    currency = Column(String)
    timezone = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

### **2.2. Extend LogicRule Model**

```python
# app/models/logic_rule.py (update existing)
# Thêm các fields:
user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
facebook_account_id = Column(Integer, ForeignKey("facebook_accounts.id"), nullable=True, index=True)
ad_account_id = Column(Integer, ForeignKey("ad_accounts.id"), nullable=True, index=True)
is_global = Column(Boolean, default=False)
priority = Column(Integer, default=0)
```

### **2.3. Run Migrations**

```bash
# Tạo migration
alembic revision --autogenerate -m "Add user and facebook account models"

# Apply migration
alembic upgrade head
```

---

## 🔐 BƯỚC 3: AUTHENTICATION SYSTEM

### **3.1. Install Dependencies**

```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

### **3.2. Create Auth Service**

```python
# app/services/auth.py
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
```

### **3.3. Create Auth Routes**

```python
# app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.services.auth import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register(email: str, password: str, name: str, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=email,
        password_hash=get_password_hash(password),
        name=name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "User created successfully", "user_id": user.id}
```

---

## 📘 BƯỚC 4: FACEBOOK OAUTH

### **4.1. Add Environment Variables**

```bash
# .env
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_REDIRECT_URI=https://updatemetaads.site/auth/facebook/callback
```

### **4.2. Create Facebook OAuth Service**

```python
# app/services/facebook_oauth.py
import httpx
from urllib.parse import urlencode
from app.core.config import get_settings

settings = get_settings()

class FacebookOAuthService:
    def __init__(self):
        self.app_id = settings.FACEBOOK_APP_ID
        self.app_secret = settings.FACEBOOK_APP_SECRET
        self.redirect_uri = settings.FACEBOOK_REDIRECT_URI
    
    def get_authorization_url(self, state: str) -> str:
        """Generate Facebook OAuth URL"""
        params = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": "ads_read,ads_management,business_management,pages_read_engagement",
            "response_type": "code"
        }
        return f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "redirect_uri": self.redirect_uri,
                "code": code
            }
            response = await client.get(url, params=params)
            return response.json()
    
    async def get_long_lived_token(self, short_token: str) -> dict:
        """Exchange short-lived token for long-lived token (60 days)"""
        async with httpx.AsyncClient() as client:
            url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                "grant_type": "fb_exchange_token",
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "fb_exchange_token": short_token
            }
            response = await client.get(url, params=params)
            return response.json()
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get Facebook user info"""
        async with httpx.AsyncClient() as client:
            url = "https://graph.facebook.com/v18.0/me"
            params = {
                "access_token": access_token,
                "fields": "id,name,email"
            }
            response = await client.get(url, params=params)
            return response.json()
    
    async def get_ad_accounts(self, access_token: str) -> list:
        """Get all ad accounts"""
        async with httpx.AsyncClient() as client:
            url = "https://graph.facebook.com/v18.0/me/adaccounts"
            params = {
                "access_token": access_token,
                "fields": "id,name,account_id,currency,timezone_name"
            }
            response = await client.get(url, params=params)
            data = response.json()
            return data.get("data", [])
```

### **4.3. Create OAuth Routes**

```python
# app/api/routes/facebook_oauth.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.facebook_oauth import FacebookOAuthService
from app.services.token_manager import TokenManager
from app.models.facebook_account import FacebookAccount
from app.models.ad_account import AdAccount
import secrets

router = APIRouter(prefix="/auth/facebook", tags=["facebook_oauth"])
oauth_service = FacebookOAuthService()
token_manager = TokenManager()

@router.get("/login")
async def facebook_login():
    """Redirect to Facebook OAuth"""
    state = secrets.token_urlsafe(32)
    # Store state in session/cache để verify sau
    url = oauth_service.get_authorization_url(state)
    return RedirectResponse(url=url)

@router.get("/callback")
async def facebook_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Cần implement
):
    """Handle Facebook OAuth callback"""
    try:
        # Exchange code for token
        token_data = await oauth_service.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        # Get long-lived token
        long_token_data = await oauth_service.get_long_lived_token(access_token)
        long_token = long_token_data.get("access_token")
        expires_in = long_token_data.get("expires_in", 5184000)  # 60 days default
        
        # Get user info
        user_info = await oauth_service.get_user_info(long_token)
        facebook_user_id = user_info.get("id")
        
        # Check if account already exists
        existing = db.query(FacebookAccount).filter(
            FacebookAccount.facebook_user_id == facebook_user_id
        ).first()
        
        if existing:
            # Update token
            existing.access_token_encrypted = token_manager.encrypt_token(long_token)
            existing.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            existing.last_refreshed_at = datetime.now()
        else:
            # Create new account
            facebook_account = FacebookAccount(
                user_id=current_user.id,  # Cần implement get_current_user
                facebook_user_id=facebook_user_id,
                facebook_name=user_info.get("name"),
                access_token_encrypted=token_manager.encrypt_token(long_token),
                token_expires_at=datetime.now() + timedelta(seconds=expires_in),
                last_refreshed_at=datetime.now()
            )
            db.add(facebook_account)
            db.commit()
            db.refresh(facebook_account)
            
            # Get ad accounts
            ad_accounts = await oauth_service.get_ad_accounts(long_token)
            for ad_account_data in ad_accounts:
                ad_account = AdAccount(
                    facebook_account_id=facebook_account.id,
                    account_id=ad_account_data.get("account_id"),
                    account_name=ad_account_data.get("name"),
                    currency=ad_account_data.get("currency"),
                    timezone=ad_account_data.get("timezone_name")
                )
                db.add(ad_account)
            db.commit()
        
        return RedirectResponse(url="/dashboard?connected=success")
    
    except Exception as e:
        return RedirectResponse(url="/dashboard?error=oauth_failed")
```

---

## 🔒 BƯỚC 5: TOKEN ENCRYPTION

### **5.1. Create Token Manager**

```python
# app/services/token_manager.py
from cryptography.fernet import Fernet
from app.core.config import get_settings
import base64
import os

settings = get_settings()

class TokenManager:
    def __init__(self):
        # Lấy encryption key từ environment
        key = settings.TOKEN_ENCRYPTION_KEY.encode()
        # Nếu key chưa có, generate mới (chỉ lần đầu)
        if not key:
            key = Fernet.generate_key()
            # Lưu vào .env
        self.cipher = Fernet(key)
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt token"""
        encrypted = self.cipher.encrypt(token.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt token"""
        encrypted_bytes = base64.b64decode(encrypted_token.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    async def get_valid_token(self, facebook_account_id: int, db: Session) -> str:
        """Get valid token, refresh if needed"""
        account = db.query(FacebookAccount).filter(
            FacebookAccount.id == facebook_account_id
        ).first()
        
        if not account:
            raise ValueError("Facebook account not found")
        
        # Check if token expired
        if account.token_expires_at < datetime.now():
            # Refresh token
            await self.refresh_token(account.id, db)
            db.refresh(account)
        
        return self.decrypt_token(account.access_token_encrypted)
```

### **5.2. Add Encryption Key to .env**

```bash
# Generate key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to .env:
TOKEN_ENCRYPTION_KEY=your_generated_key_here
```

---

## 🎨 BƯỚC 6: UI DASHBOARD

### **6.1. Create Login Page**

```html
<!-- templates/auth/login.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Login - Facebook Ads Automation</title>
</head>
<body>
    <h1>Login</h1>
    <form action="/auth/login" method="post">
        <input type="email" name="username" placeholder="Email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    <a href="/auth/facebook/login">Login with Facebook</a>
</body>
</html>
```

### **6.2. Create Account Management Page**

```html
<!-- templates/dashboard/accounts.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Accounts</title>
</head>
<body>
    <h1>Connected Facebook Accounts</h1>
    <div id="accounts-list">
        <!-- Loaded via JavaScript -->
    </div>
    <button onclick="connectFacebook()">Connect New Facebook Account</button>
    
    <script>
        async function loadAccounts() {
            const response = await fetch('/api/facebook/accounts');
            const accounts = await response.json();
            // Render accounts
        }
        
        function connectFacebook() {
            window.location.href = '/auth/facebook/login';
        }
        
        loadAccounts();
    </script>
</body>
</html>
```

---

## ✅ CHECKLIST

- [ ] Setup Facebook App
- [ ] Create database models
- [ ] Implement authentication
- [ ] Implement Facebook OAuth
- [ ] Implement token encryption
- [ ] Create UI pages
- [ ] Test với real Facebook account
- [ ] Deploy to production

---

## 📚 NEXT STEPS

Sau khi hoàn thành các bước trên, bạn có thể:
1. Extend logic rules với account-specific
2. Create rule management UI
3. Add real-time updates
4. Add monitoring & alerts

Xem file `FACEBOOK_OAUTH_ANALYSIS.md` để biết chi tiết hơn về architecture và challenges.



