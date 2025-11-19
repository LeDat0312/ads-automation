"""
Test script for CAPTCHA functionality
"""
import sys
sys.path.insert(0, '.')

from app.core.captcha import generate_captcha_text, generate_captcha_image, hash_captcha, verify_captcha

# Test 1: Generate CAPTCHA text
print("Test 1: Generate CAPTCHA text")
text = generate_captcha_text()
print(f"[OK] Generated text: {text} (length: {len(text)})")
assert len(text) == 5, "Text should be 5 characters"
assert text.isupper() or text.isdigit(), "Text should be uppercase or digits"

# Test 2: Generate CAPTCHA image
print("\nTest 2: Generate CAPTCHA image")
image_bytes = generate_captcha_image(text)
print(f"[OK] Generated image: {len(image_bytes.getvalue())} bytes")
assert len(image_bytes.getvalue()) > 0, "Image should not be empty"

# Test 3: Hash CAPTCHA
print("\nTest 3: Hash CAPTCHA")
secret_key = "test_secret_key_12345"
hashed = hash_captcha(text, secret_key)
print(f"[OK] Hashed: {hashed[:20]}... (length: {len(hashed)})")
assert len(hashed) == 64, "Hash should be 64 characters (SHA256 hex)"

# Test 4: Verify CAPTCHA - Correct
print("\nTest 4: Verify CAPTCHA - Correct")
is_valid = verify_captcha(text, hashed, secret_key)
print(f"[OK] Verification (correct): {is_valid}")
assert is_valid == True, "Should verify correct CAPTCHA"

# Test 5: Verify CAPTCHA - Incorrect
print("\nTest 5: Verify CAPTCHA - Incorrect")
is_valid = verify_captcha("WRONG", hashed, secret_key)
print(f"[OK] Verification (wrong): {is_valid}")
assert is_valid == False, "Should reject incorrect CAPTCHA"

# Test 6: Verify CAPTCHA - Case insensitive
print("\nTest 6: Verify CAPTCHA - Case insensitive")
is_valid = verify_captcha(text.lower(), hashed, secret_key)
print(f"[OK] Verification (lowercase): {is_valid}")
assert is_valid == True, "Should accept lowercase input"

# Test 7: Verify CAPTCHA - Empty
print("\nTest 7: Verify CAPTCHA - Empty")
is_valid = verify_captcha("", hashed, secret_key)
print(f"[OK] Verification (empty): {is_valid}")
assert is_valid == False, "Should reject empty input"

print("\n" + "="*50)
print("[SUCCESS] All tests passed!")
print("="*50)
