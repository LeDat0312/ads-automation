#!/bin/bash

# 🗑️  Clean up trash files from VPS
# Xóa tất cả file rác: .md, .txt, .sh, .py, .gs, .html, .ps1 (ngoại trừ code quan trọng)

set -e

PROJECT_PATH="/home/adsuser/ads-automation"
cd "$PROJECT_PATH"

echo "🗑️  Cleaning up trash files..."
echo ""

# Xóa tất cả .md, .txt ở root
echo "Removing .md and .txt files from root..."
find . -maxdepth 1 -type f \( -name "*.md" -o -name "*.txt" \) -delete

# Xóa các file rác ở root (shell scripts, py scripts, gs scripts, html)
echo "Removing .sh, .py, .gs, .html, .ps1 files from root..."
find . -maxdepth 1 -type f \( -name "*.sh" -o -name "*.py" -o -name "*.gs" -o -name "*.html" -o -name "*.ps1" \) -delete

# Xóa folder Madgicx_files nếu có
if [ -d "Madgicx_files" ]; then
    echo "Removing Madgicx_files folder..."
    rm -rf Madgicx_files
fi

# Xóa Madgicx.html và .rar nếu có
echo "Removing Madgicx files..."
rm -f Madgicx.html Madgicx_files.rar

# Xóa các file .rar, .zip, .tar
echo "Removing archive files..."
find . -maxdepth 1 -type f \( -name "*.rar" -o -name "*.zip" -o -name "*.tar.gz" \) -delete

# Xóa file rác trong scripts folder (giữ lại init_db.py, seed_data.py, create_admin_user.py)
echo "Cleaning scripts folder..."
if [ -d "scripts" ]; then
    cd scripts
    
    # Xóa file migration SQL
    rm -f add_*.sql fix_*.sql verify_*.sql force_*.sql
    
    # Xóa file migration/check Python
    rm -f add_*.py check_*.py fix_*.py run_telegram_migration.py
    
    # Xóa file shell scripts
    rm -f *.sh
    
    cd ..
fi

# Xóa các file rác trong deploy folder (giữ lại DEPLOYMENT_GUIDE.md)
echo "Cleaning deploy folder..."
if [ -d "deploy" ]; then
    cd deploy
    rm -f check-server-info.ps1 deploy-remote.ps1 check-services.sh deploy.sh
    cd ..
fi

echo ""
echo "✅ Cleanup completed!"
echo ""

# Hiển thị cấu trúc project sau cleanup
echo "📁 Project structure:"
ls -la

echo ""
echo "✅ Done! All trash files have been removed."
