# PowerShell Script để commit và push code Dashboard lên GitHub
# Sử dụng: .\PULL_DASHBOARD_VPS.ps1

Write-Host "🚀 Bắt đầu commit và push code Dashboard lên GitHub..." -ForegroundColor Yellow

# Kiểm tra git status
Write-Host "`n📊 Kiểm tra git status..." -ForegroundColor Cyan
git status

# Add các file đã thay đổi
Write-Host "`n➕ Đang add các file đã thay đổi..." -ForegroundColor Cyan
git add app/api/routes/dashboard.py
git add app/core/ui_helpers.py
git add app/api/routes/home.py

# Commit
Write-Host "`n💾 Đang commit..." -ForegroundColor Cyan
$commitMessage = "Cập nhật Dashboard: Cảnh báo E-commerce (% ADS > 25%, Giá DATA > 10k), sắp xếp theo Giá DATA, sửa user menu"
git commit -m $commitMessage

# Push lên GitHub
Write-Host "`n⬆️  Đang push lên GitHub..." -ForegroundColor Cyan
git push origin main

Write-Host "`n✅ Hoàn tất! Code đã được push lên GitHub." -ForegroundColor Green
Write-Host "`n📝 Bước tiếp theo: SSH vào VPS và chạy script PULL_DASHBOARD_VPS.sh" -ForegroundColor Yellow
Write-Host "   hoặc chạy lệnh: cd /root/PythonUpdateMetaAds && git pull origin main && sudo supervisorctl restart api" -ForegroundColor Yellow


