# VPS Deployment Guide - AdStudio
# Quick reference for deploying AdStudio on VPS

## Initial Deployment (when you have conflicts or permission errors)

```bash
cd /home/adsuser/ads-automation

# Method 1: Direct download and run (recommended for permission issues)
curl -O https://raw.githubusercontent.com/LeDat0312/ads-automation/main/fix_permissions_deploy.sh
bash fix_permissions_deploy.sh

# Method 2: If you can git fetch (no permission errors)
git fetch origin main
bash fix_vps_conflicts.sh
```

## Normal Deployment (when no conflicts)

```bash
cd /home/adsuser/ads-automation
git pull origin main
bash deploy_ad_studio.sh
```

## Quick Commands

### Check Status
```bash
# See running processes
ps aux | grep -E "uvicorn|ad_studio_publisher" | grep -v grep

# Check logs
tail -f ~/ads-automation/uvicorn.log
tail -f ~/ads-automation/worker.log
```

### Restart Services
```bash
cd /home/adsuser/ads-automation

# Stop all
pkill -f "uvicorn app.main:app"
pkill -f "app.workers.ad_studio_publisher"

# Start backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

# Start worker
nohup python3 -m app.workers.ad_studio_publisher > worker.log 2>&1 &
```

### Check Media Files
```bash
ls -lh ~/ads-automation/media/ad_studio/
```

### Test Database
```bash
cd /home/adsuser/ads-automation
python3 -c "from app.core.database import SessionLocal; db=SessionLocal(); print('✅ DB OK'); db.close()"
```

## Troubleshooting

### Error: "No module named 'app'"
```bash
# Make sure you're in the right directory
cd /home/adsuser/ads-automation
pwd  # Should show: /home/adsuser/ads-automation
```

### Error: "python: command not found"
```bash
# Use python3 instead
python3 --version  # Should show Python 3.10+
```

### Error: "unable to unlink old 'frontend/dist/...': Permission denied"
```bash
# Fix permissions and deploy
cd /home/adsuser/ads-automation
curl -O https://raw.githubusercontent.com/LeDat0312/ads-automation/main/fix_permissions_deploy.sh
bash fix_permissions_deploy.sh
```

### Error: "git merge conflicts"
```bash
# Use the fix script
bash fix_vps_conflicts.sh
# This will backup your changes and force update
```

### Worker not running
```bash
# Check worker log
tail -50 worker.log

# Common issues:
# 1. Database not connected - check DATABASE_URL in .env
# 2. Import error - make sure all dependencies installed
# 3. Port conflict - kill old process first
```

### Uvicorn not starting
```bash
# Check uvicorn log
tail -50 uvicorn.log

# Common issues:
# 1. Port 8000 already in use
pkill -f uvicorn; sleep 2; nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

# 2. Missing dependencies
pip install -r requirements.txt
```

## Testing After Deployment

1. **Health Check**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

2. **Frontend Access**
```bash
# Open in browser:
https://your-domain/dashboard/
```

3. **Media Directory**
```bash
# Check media is mounted
ls -la media/
# Should have: ad_studio/ directory
```

4. **Test AdStudio Flow**
- Go to Dashboard → Ad Studio tab
- Scrape a TikTok video
- Check media files: `ls media/ad_studio/`
- Schedule a post
- Check worker log: `tail -f worker.log`

## File Locations

- Project: `/home/adsuser/ads-automation/`
- Logs: `uvicorn.log`, `worker.log`
- Media: `media/ad_studio/`
- Database: PostgreSQL (check .env for DATABASE_URL)
- Frontend: `frontend/dist/`

## Environment Variables (.env)

Required:
```
DATABASE_URL=postgresql://user:pass@localhost/dbname
APIFY_API_TOKEN=your_apify_token
```

Optional:
```
MEDIA_ROOT=media
MEDIA_URL_PREFIX=/media
```
