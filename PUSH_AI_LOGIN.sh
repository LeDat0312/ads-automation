#!/bin/bash
# Script để push AI Login Interface lên GitHub

echo "🚀 Pushing AI Login Interface to GitHub..."

# Add changes
git add app/api/routes/auth.py

# Show what will be committed
echo "📝 Changes to be committed:"
git diff --cached --stat

# Commit
git commit -m "feat: Add AI-powered login interface with mouse tracking

- Added interactive AI robot character with gradient design
- Implemented mouse tracking for AI eyes
- Added password protection animation (AI covers eyes)
- Enhanced with floating particles background
- Improved responsive design for mobile
- Added smooth transitions and micro-animations
- Integrated Google Fonts (Inter)
- Enhanced error handling with shake animation
- Improved UX with state-based AI expressions"

# Push to GitHub
echo "📤 Pushing to origin/main..."
git push origin main

echo "✅ Done! Code pushed to GitHub"
echo ""
echo "📋 Next steps - Run on VPS:"
echo "cd /var/www/ads-automation"
echo "git pull origin main"
echo "sudo supervisorctl restart ads-automation-production"
