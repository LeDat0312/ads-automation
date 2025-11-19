import random
import string
import io
import hmac
import hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def generate_captcha_text(length=5):
    """Generate random uppercase string"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_captcha_image(text, width=160, height=60):
    """Generate CAPTCHA image bytes"""
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    font = ImageFont.load_default()
    
    # Create drawing object
    draw = ImageDraw.Draw(image)
    
    # Add noise (lines)
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line(((x1, y1), (x2, y2)), fill=(200, 200, 200), width=2)
        
    # Add noise (points)
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(180, 180, 180))
    
    # Draw text
    # Since we don't have a guaranteed ttf font, we use default and scale it up or draw multiple times
    # For better look without external fonts, we can just draw text in random positions
    # But default font is very small. Let's try to find a system font or just use default for now.
    # To make it bigger without font file, we can draw on small image and resize up
    
    small_image = Image.new('RGB', (int(width/3), int(height/3)), color=(255, 255, 255))
    small_draw = ImageDraw.Draw(small_image)
    
    # Draw text on small image
    small_draw.text((5, 5), text, font=font, fill=(0, 0, 0))
    
    # Resize to actual size (pixelated effect is fine/good for captcha)
    image = small_image.resize((width, height), Image.NEAREST)
    
    # Apply some distortion
    image = image.filter(ImageFilter.SMOOTH)
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def hash_captcha(text: str, secret_key: str) -> str:
    """Create HMAC hash of captcha text"""
    return hmac.new(
        secret_key.encode(),
        text.upper().encode(),
        hashlib.sha256
    ).hexdigest()

def verify_captcha(input_text: str, hashed_text: str, secret_key: str) -> bool:
    """Verify captcha input against hash"""
    if not input_text or not hashed_text:
        return False
    
    current_hash = hash_captcha(input_text, secret_key)
    return hmac.compare_digest(current_hash, hashed_text)
