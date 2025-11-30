# VPS Deployment - Error Resolution

## Errors Encountered

```bash
./force_pull.sh
# -bash: ./force_pull.sh: Permission denied

python -m migrations.add_facebook_accounts_table
# No module named migrations.add_facebook_accounts_table

sudo supervisorctl restart backend
# backend: ERROR (no such process)
```

---

## Root Causes

1. **Permission denied**: Scripts don't have execute permission on VPS
2. **Migration not found**: Old code doesn't have the new migration file yet
3. **Service not found**: Supervisor service might have different name than "backend"

---

## Solution 1: Quick Fix (Recommended)

Run the automated quick-fix script:

```bash
cd /home/adsuser/ads-automation

# First, fix permission on this one script manually
chmod +x VPS_QUICK_FIX_ERRORS.sh

# Then run it
./VPS_QUICK_FIX_ERRORS.sh
```

This script will:
- ✅ Fix all script permissions
- ✅ Find the correct supervisor service name
- ✅ Run migration (or skip if not available yet)
- ✅ Restart the backend service

---

## Solution 2: Manual Steps

If you prefer to do it manually:

### Step 1: Fix Permissions
```bash
cd /home/adsuser/ads-automation
chmod +x *.sh
```

### Step 2: Pull Latest Code
```bash
git fetch origin main
git reset --hard origin/main
git clean -fd
```

### Step 3: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 4: Run Migration
```bash
python -m migrations.add_facebook_accounts_table
```

If you get "No module named migrations", the file isn't pulled yet. Check:
```bash
ls migrations/add_facebook_accounts_table.py
```

### Step 5: Find Supervisor Service Name
```bash
# List all supervisor configs
sudo ls /etc/supervisor/conf.d/

# Check which one has our app
grep -r "uvicorn app.main:app" /etc/supervisor/conf.d/
```

Common service names:
- `ads-automation`
- `fastapi`
- `backend`
- `meta-update`

### Step 6: Restart Service
```bash
# Replace SERVICE_NAME with actual name from step 5
sudo supervisorctl restart SERVICE_NAME

# Check status
sudo supervisorctl status

# View logs
sudo supervisorctl tail SERVICE_NAME -f
```

---

## Solution 3: Complete Deployment (Full Reset)

For a complete clean deployment:

```bash
cd /home/adsuser/ads-automation

# Fix permissions first
chmod +x VPS_DEPLOY_FACEBOOK_ACCOUNTS.sh

# Run full deployment
./VPS_DEPLOY_FACEBOOK_ACCOUNTS.sh
```

This comprehensive script does everything:
- Stops all services
- Cleans old files
- Pulls latest code
- Installs dependencies
- Runs migrations
- Finds correct service name automatically
- Restarts services
- Validates deployment

---

## Verification

After running any solution, verify the deployment:

### 1. Check Service Status
```bash
sudo supervisorctl status
```

Expected output:
```
ads-automation                   RUNNING   pid 12345, uptime 0:00:30
```

### 2. Check Port 8000
```bash
sudo lsof -i :8000
```

Should show Python/uvicorn process listening.

### 3. Test Health Endpoint
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 4. Test New API
```bash
# Should return 401 Unauthorized (expected - needs auth)
curl -I http://localhost:8000/api/facebook-accounts
```

Expected: `HTTP/1.1 401 Unauthorized`

### 5. Check Migration
```bash
source venv/bin/activate
python -c "from app.models.facebook_account import FacebookAccount; print('✅ Model imported successfully')"
```

---

## Troubleshooting

### Issue: Service won't start

**Check logs:**
```bash
sudo supervisorctl tail SERVICE_NAME stderr
```

**Common causes:**
- Port 8000 already in use
- Database connection failed
- Import errors in new code

**Fix:**
```bash
# Kill any process on port 8000
sudo lsof -i :8000
sudo kill -9 PID_FROM_ABOVE

# Restart
sudo supervisorctl restart SERVICE_NAME
```

### Issue: Migration fails - "Table already exists"

**This is OK!** It means the migration already ran. Safe to ignore.

### Issue: Import errors after deployment

**Check Python dependencies:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Check model imports:**
```bash
python -c "from app.models.facebook_account import FacebookAccount"
python -c "from app.schemas.facebook_account import FacebookAccountRead"
python -c "from app.services.facebook_account_service import FacebookAccountService"
```

### Issue: 502 Bad Gateway from nginx

**Backend not running:**
```bash
sudo supervisorctl status
# If not RUNNING, check logs:
sudo supervisorctl tail SERVICE_NAME stderr | tail -50
```

**Port not listening:**
```bash
sudo lsof -i :8000
# If empty, service didn't start properly
```

---

## Quick Reference

### Essential Commands

```bash
# View real-time logs
sudo supervisorctl tail SERVICE_NAME -f

# Restart service
sudo supervisorctl restart SERVICE_NAME

# Stop service
sudo supervisorctl stop SERVICE_NAME

# Start service
sudo supervisorctl start SERVICE_NAME

# Check all services
sudo supervisorctl status

# Reload config (after editing .conf files)
sudo supervisorctl reread
sudo supervisorctl update

# Check port 8000
sudo lsof -i :8000

# Check backend process
ps aux | grep uvicorn

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Swagger UI
```

### Log Locations

```bash
# Supervisor logs
/var/log/supervisor/SERVICE_NAME.log

# Or via supervisorctl
sudo supervisorctl tail SERVICE_NAME
sudo supervisorctl tail SERVICE_NAME stderr

# Nginx error log
sudo tail -f /var/log/nginx/error.log

# Nginx access log
sudo tail -f /var/log/nginx/access.log
```

---

## Summary

**Fastest solution:**
```bash
cd /home/adsuser/ads-automation
chmod +x VPS_QUICK_FIX_ERRORS.sh
./VPS_QUICK_FIX_ERRORS.sh
```

**Most thorough solution:**
```bash
cd /home/adsuser/ads-automation
chmod +x VPS_DEPLOY_FACEBOOK_ACCOUNTS.sh
./VPS_DEPLOY_FACEBOOK_ACCOUNTS.sh
```

Both scripts handle all three errors automatically and provide detailed feedback.

---

## Expected Output (Success)

After successful deployment:

```
🎉 DEPLOYMENT SUMMARY
==============================================

✅ Code pulled from GitHub
✅ Migration executed: add_facebook_accounts_table
✅ Supervisor service: ads-automation
✅ Backend process started

📊 Service Status:
ads-automation                   RUNNING   pid 12345, uptime 0:00:15

🔗 New API Endpoints:
  - GET    /api/facebook-accounts
  - POST   /api/facebook-accounts
  - PATCH  /api/facebook-accounts/{id}
  - DELETE /api/facebook-accounts/{id}
  - POST   /api/facebook-accounts/{id}/verify
  - GET    /api/facebook-accounts/{id}/pages
  - POST   /api/channels/facebook/from-saved-account
  - POST   /api/channels/facebook/manual-v2

✅ Deployment complete!
```

Test with:
```bash
curl http://localhost:8000/health
# {"status":"healthy"}

curl -I http://localhost:8000/api/facebook-accounts
# HTTP/1.1 401 Unauthorized  (expected - needs auth token)
```

---

## Next Steps

After successful deployment:

1. **Test the API** using Swagger UI: `http://YOUR_VPS_IP:8000/docs`
2. **Build frontend** (once UI is implemented)
3. **Test end-to-end** flow with real Facebook tokens

**Frontend is NOT yet implemented.** Backend only at this stage.

See `FACEBOOK_VIA_TOKEN_IMPLEMENTATION.md` for complete documentation.
