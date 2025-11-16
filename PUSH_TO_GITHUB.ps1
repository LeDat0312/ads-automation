# Script PowerShell để push code lên GitHub
# Sử dụng: .\PUSH_TO_GITHUB.ps1

Write-Host "🚀 Bắt đầu push code lên GitHub..." -ForegroundColor Green

# Kiểm tra xem có git repository không
if (-not (Test-Path ".git")) {
    Write-Host "❌ Không tìm thấy git repository!" -ForegroundColor Red
    Write-Host "Vui lòng chạy script này trong thư mục git repository hoặc clone repository trước." -ForegroundColor Yellow
    exit 1
}

# Kiểm tra status
Write-Host "📊 Kiểm tra git status..." -ForegroundColor Cyan
git status

# Add file đã thay đổi
Write-Host "📦 Adding files..." -ForegroundColor Cyan
git add app/api/routes/dashboard.py

# Commit
Write-Host "💾 Committing changes..." -ForegroundColor Cyan
$commitMessage = "Fix dashboard: Replace JS template literals with string concatenation, add stats grid, fix date picker functions"
git commit -m $commitMessage

# Push
Write-Host "⬆️ Pushing to GitHub..." -ForegroundColor Cyan
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Push thành công!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Bước tiếp theo:" -ForegroundColor Yellow
    Write-Host "   1. SSH vào VPS" -ForegroundColor White
    Write-Host "   2. Chạy: bash PULL_VPS_DASHBOARD_FIX.sh" -ForegroundColor White
} else {
    Write-Host "❌ Push thất bại! Vui lòng kiểm tra lại." -ForegroundColor Red
    exit 1
}

