"""
Facebook OAuth Routes
Xử lý đăng nhập bằng Facebook OAuth
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User
from app.core.security import create_access_token, get_password_hash
import httpx
import urllib.parse
import secrets

router = APIRouter(
    prefix="/api/auth/facebook",
    tags=["Facebook OAuth"],
)


@router.get("/login")
async def facebook_login(settings=Depends(get_settings)):
    """
    Redirect user sang Facebook OAuth dialog.
    """
    if not settings.FACEBOOK_APP_ID or not settings.FACEBOOK_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Facebook OAuth chưa được cấu hình")
    
    base_url = "https://www.facebook.com/v19.0/dialog/oauth"
    params = {
        "client_id": settings.FACEBOOK_APP_ID,
        "redirect_uri": str(settings.FACEBOOK_REDIRECT_URI),
        "response_type": "code",
        "scope": settings.FACEBOOK_LOGIN_SCOPES,
        # TODO: có thể thêm state chống CSRF nếu cần
    }
    
    oauth_url = base_url + "?" + urllib.parse.urlencode(params)
    return RedirectResponse(url=oauth_url)


@router.get("/callback")
async def facebook_callback(
    code: str | None = None,
    error: str | None = None,
    settings=Depends(get_settings),
    db: Session = Depends(get_db),
):
    """
    Facebook redirect về đây với ?code=...
    Đổi code -> access_token -> lấy user info -> tạo/tìm user -> JWT -> redirect dashboard
    """
    if error:
        raise HTTPException(status_code=400, detail=f"Facebook error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Thiếu mã ủy quyền (code)")
    
    if not settings.FACEBOOK_APP_ID or not settings.FACEBOOK_APP_SECRET:
        raise HTTPException(status_code=500, detail="Facebook OAuth chưa cấu hình đầy đủ")
    
    # Bước 1: Đổi code -> access_token
    token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
    
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            token_url,
            params={
                "client_id": settings.FACEBOOK_APP_ID,
                "client_secret": settings.FACEBOOK_APP_SECRET,
                "redirect_uri": str(settings.FACEBOOK_REDIRECT_URI),
                "code": code,
            },
        )
    
    if resp.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Không đổi được access_token từ Facebook: {resp.text}",
        )
    
    token_data = resp.json()
    facebook_access_token = token_data.get("access_token")
    
    if not facebook_access_token:
        raise HTTPException(
            status_code=400,
            detail="Không nhận được access_token từ Facebook",
        )
    
    # Bước 2: Gọi /me API để lấy thông tin user
    me_url = "https://graph.facebook.com/v19.0/me"
    
    async with httpx.AsyncClient(timeout=10) as client:
        me_resp = await client.get(
            me_url,
            params={
                "fields": "id,name,email",
                "access_token": facebook_access_token,
            },
        )
    
    if me_resp.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Không lấy được thông tin user từ Facebook: {me_resp.text}",
        )
    
    fb_user_data = me_resp.json()
    facebook_id = fb_user_data.get("id")
    fb_name = fb_user_data.get("name", "")
    fb_email = fb_user_data.get("email")
    
    if not facebook_id:
        raise HTTPException(
            status_code=400,
            detail="Không nhận được Facebook ID",
        )
    
    # Bước 3: Tìm hoặc tạo user trong DB
    user = None
    
    # Thử tìm theo facebook_id trước
    if facebook_id:
        user = db.query(User).filter(User.facebook_id == facebook_id).first()
    
    # Nếu không tìm thấy theo facebook_id, thử tìm theo email
    if not user and fb_email:
        user = db.query(User).filter(User.email == fb_email).first()
        # Nếu tìm thấy user theo email nhưng chưa có facebook_id, cập nhật
        if user and not user.facebook_id:
            user.facebook_id = facebook_id
            db.commit()
            db.refresh(user)
    
    # Nếu vẫn chưa có user, tạo mới
    if not user:
        # Tạo username: dùng email nếu có, nếu không thì dùng fb_<facebook_id>
        if fb_email:
            username = fb_email.split("@")[0]  # Lấy phần trước @
            # Đảm bảo username unique
            base_username = username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}_{counter}"
                counter += 1
        else:
            username = f"fb_{facebook_id}"
            # Đảm bảo username unique
            base_username = username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}_{counter}"
                counter += 1
        
        # Tạo email nếu không có (dùng placeholder)
        email = fb_email if fb_email else f"fb_{facebook_id}@facebook.local"
        # Đảm bảo email unique
        base_email = email
        counter = 1
        while db.query(User).filter(User.email == email).first():
            if "@" in base_email:
                email = f"{base_email.split('@')[0]}_{counter}@{base_email.split('@')[1]}"
            else:
                email = f"{base_email}_{counter}"
            counter += 1
        
        # Tạo password hash random (vì login bằng Facebook, không dùng password này)
        random_password = secrets.token_urlsafe(32)
        hashed_password = get_password_hash(random_password)
        
        # Tạo user mới
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            display_name=fb_name or username,
            facebook_id=facebook_id,
            role="user",  # Luôn là user, không tự tạo admin
            is_active=True,
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Kiểm tra user có bị khóa không
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa"
        )
    
    # Bước 4: Tạo JWT nội bộ (giống login thường)
    token_data = {"sub": user.username}
    access_token = create_access_token(token_data)
    
    # Bước 5: Tạo response với cookie và redirect (giống login thường)
    # Set cookie giống login thường (30 ngày, vì Facebook login coi như "remember")
    max_age = 30 * 24 * 60 * 60  # 30 days
    
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=max_age,
        httponly=False,  # Allow JS to read for localStorage sync (giống login thường)
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return response

