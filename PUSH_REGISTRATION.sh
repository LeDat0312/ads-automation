#!/bin/bash
# Script để push Registration Feature lên GitHub

echo "🚀 Pushing Registration Feature to GitHub..."

# Add changes
git add app/core/captcha.py
git add app/api/routes/auth.py

# Show what will be committed
echo "📝 Changes to be committed:"
git diff --cached --stat

# Commit
git commit -m "feat: Implement User Registration with CAPTCHA

- Added app/core/captcha.py for CAPTCHA generation
- Added GET /auth/register endpoint (HTML page with AI character)
- Added POST /auth/register endpoint (Handle registration)
- Added GET /auth/captcha endpoint
- Updated Login page with link to Register
- Implemented CAPTCHA verification using signed cookies
- Added AI character animations for registration page"

# Push to GitHub
echo "📤 Pushing to origin/main..."
git push origin main

echo "✅ Done! Code pushed to GitHub"
echo ""
echo "📋 Next steps - Run on VPS:"
echo "cd /home/adsuser/ads-automation && git pull origin main && sudo supervisorctl restart ads-automation-production"
