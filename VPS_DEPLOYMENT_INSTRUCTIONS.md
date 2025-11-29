# VPS Deployment Instructions - Channel Management Backend

## 🚀 Quick Deployment Commands

### Option 1: Using the provided script (Recommended)

```bash
cd /home/adsuser/ads-automation
chmod +x vps_pull_channel_backend.sh
./vps_pull_channel_backend.sh
```

### Option 2: Manual step-by-step commands

```bash
cd /home/adsuser/ads-automation

# 1. Backup and pull code
git stash
sudo rm -rf frontend/dist 2>/dev/null || true
git fetch origin main
git reset --hard origin/main
git clean -fd

# 2. Rebuild frontend
cd frontend
npm install
npm run build
cd ..

# 3. Run database migration
python3 -m migrations.add_channels_management_tables

# 4. Restart services (choose one based on your setup)
sudo systemctl restart ads-automation.service
# OR
sudo systemctl restart uwsgi.service
# OR manually restart your FastAPI process
```

---

## 📋 What Gets Deployed

### Backend Changes:
- ✅ New models: `Channel`, `ChannelGroup`, `ChannelGroupMembership`, `PostingSettings`, `AutoCommentTemplate`
- ✅ New API routes: `/api/channels/*`, `/api/channel-groups/*`, `/api/posting/settings/*`
- ✅ Migration script: Creates 5 new database tables

### Frontend Changes:
- ✅ Updated Settings pages to use real APIs
- ✅ Removed all mock data
- ✅ New SettingsLayout component

---

## 🗄️ Database Migration

The migration will create these new tables:
- `channels`
- `channel_groups`
- `channel_group_memberships`
- `posting_settings`
- `auto_comment_templates`

**Note:** These are separate from existing `facebook_pages` table for backward compatibility.

---

## ✅ Verification Steps

After deployment, verify:

1. **API Endpoints:**
   ```bash
   curl -X GET http://localhost:8000/api/channels \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **Frontend Pages:**
   - Visit: `/settings/channels`
   - Visit: `/settings/channel-groups`
   - Visit: `/settings/posting`

3. **Database Tables:**
   ```bash
   psql -U your_user -d your_db -c "\dt channels*"
   psql -U your_user -d your_db -c "\dt posting_settings"
   ```

---

## ⚠️ Troubleshooting

### If migration fails:
```bash
# Check Python path
which python3
python3 -c "import sys; print(sys.path)"

# Run migration with explicit path
cd /home/adsuser/ads-automation
PYTHONPATH=/home/adsuser/ads-automation python3 -m migrations.add_channels_management_tables
```

### If frontend build fails:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### If services won't restart:
```bash
# Check service status
sudo systemctl status ads-automation.service
sudo journalctl -u ads-automation.service -n 50

# Check for Python errors
sudo journalctl -xe | grep -i error
```

---

## 📝 Rollback Instructions (if needed)

If something goes wrong:

```bash
cd /home/adsuser/ads-automation

# Revert to previous commit
git log --oneline -5  # Find previous commit hash
git reset --hard <previous_commit_hash>

# Rebuild frontend
cd frontend && npm run build && cd ..

# Restart services
sudo systemctl restart ads-automation.service
```

---

## 🎯 Post-Deployment Checklist

- [ ] Migration ran successfully (check logs)
- [ ] All 5 new tables exist in database
- [ ] API endpoints respond correctly
- [ ] Frontend pages load without errors
- [ ] Can create/update/delete channels
- [ ] Can create/update/delete channel groups
- [ ] Can configure posting settings

---

## 📞 Support

If you encounter issues:
1. Check application logs
2. Check database connection
3. Verify environment variables (.env file)
4. Check Python dependencies are installed

