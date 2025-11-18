#!/bin/bash
echo "Đang push code lên GitHub..."
git add app/services/facebook_api.py app/api/routes/dashboard.py
git commit -m "Optimize: Global cache cho objectives/budgets/status, fix filter adset_id, tối ưu tốc độ load"
git push origin main
echo "Hoàn tất!"

