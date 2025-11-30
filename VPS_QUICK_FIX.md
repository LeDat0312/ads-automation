# Quick VPS Commands - Fix Permission and Deploy

## Problem: Permission Denied on Git Pull
```
error: unable to unlink old 'frontend/dist/...'
Permission denied
```

## Solution: Run this ONE command on VPS

```bash
curl -sSL https://raw.githubusercontent.com/LeDat0312/ads-automation/main/force_pull.sh | bash
```

Or if already in the repo (but git pull fails):

```bash
# Download force_pull.sh first
wget https://raw.githubusercontent.com/LeDat0312/ads-automation/main/force_pull.sh -O /tmp/force_pull.sh

# Run it
bash /tmp/force_pull.sh
```

## What it does:
1. Stop nginx (releases file locks)
2. Force remove frontend/dist/
3. Fetch latest from GitHub
4. Force reset to origin/main
5. Clean untracked files
6. Restart nginx

## After successful pull, check service:

```bash
cd /home/adsuser/ads-automation
bash VPS_CHECK_AND_FIX_SERVICE.sh
```

## Then restart backend:

```bash
bash VPS_RESTART.sh
```

## Quick deploy (all-in-one):

```bash
cd /home/adsuser/ads-automation
curl -sSL https://raw.githubusercontent.com/LeDat0312/ads-automation/main/force_pull.sh | bash && \
bash VPS_RESTART.sh && \
sudo journalctl -u metaupdate -f
```
