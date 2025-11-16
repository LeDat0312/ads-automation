# PowerShell script để commit và push authentication files lên GitHub

Write-Host "🚀 Committing and pushing authentication files to GitHub..." -ForegroundColor Cyan
Write-Host ""

# Vào thư mục project
$projectPath = "C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds"
Set-Location $projectPath

# Kiểm tra git status
Write-Host "📋 Checking git status..." -ForegroundColor Yellow
git status

# Add các file mới
Write-Host ""
Write-Host "➕ Adding new files..." -ForegroundColor Yellow
git add app/models/user.py
git add app/core/security.py
git add scripts/create_admin_user.py
git add app/core/database.py
git add requirements.txt

# Commit
Write-Host ""
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
git commit -m "Add authentication system: User model, security utilities, and create_admin_user script"

# Push
Write-Host ""
Write-Host "⬆️  Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "✅ Done! Files have been pushed to GitHub." -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next step: SSH into VPS and run:" -ForegroundColor Cyan
Write-Host "   cd ~/ads-automation" -ForegroundColor White
Write-Host "   source venv/bin/activate" -ForegroundColor White
Write-Host "   git pull origin main" -ForegroundColor White
Write-Host "   pip install python-jose[cryptography] passlib[bcrypt]" -ForegroundColor White
Write-Host "   python scripts/create_admin_user.py" -ForegroundColor White
Write-Host ""

