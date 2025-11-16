# Script to copy only Python project files
# From: C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet
# To: C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds

$sourceDir = "C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet"
$destDir = "C:\Users\Foxy\Downloads\File 5h_4_11\PythonUpdateMetaAds"

Write-Host "🚀 Copying Python project files..." -ForegroundColor Green

# Create destination directory if not exists
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir -Force
    Write-Host "✅ Created destination directory" -ForegroundColor Green
}

# Copy app/ folder (entire folder)
if (Test-Path "$sourceDir\app") {
    Write-Host "📁 Copying app/ folder..." -ForegroundColor Yellow
    Copy-Item -Path "$sourceDir\app" -Destination $destDir -Recurse -Force
    Write-Host "✅ Copied app/ folder" -ForegroundColor Green
} else {
    Write-Host "⚠️ app/ folder not found in source" -ForegroundColor Red
}

# Copy scripts/ folder (entire folder)
if (Test-Path "$sourceDir\scripts") {
    Write-Host "📁 Copying scripts/ folder..." -ForegroundColor Yellow
    Copy-Item -Path "$sourceDir\scripts" -Destination $destDir -Recurse -Force
    Write-Host "✅ Copied scripts/ folder" -ForegroundColor Green
} else {
    Write-Host "⚠️ scripts/ folder not found in source" -ForegroundColor Red
}

# Copy requirements.txt
if (Test-Path "$sourceDir\requirements.txt") {
    Write-Host "📄 Copying requirements.txt..." -ForegroundColor Yellow
    Copy-Item -Path "$sourceDir\requirements.txt" -Destination $destDir -Force
    Write-Host "✅ Copied requirements.txt" -ForegroundColor Green
} else {
    Write-Host "⚠️ requirements.txt not found in source" -ForegroundColor Red
}

# Copy env.example
if (Test-Path "$sourceDir\env.example") {
    Write-Host "📄 Copying env.example..." -ForegroundColor Yellow
    Copy-Item -Path "$sourceDir\env.example" -Destination $destDir -Force
    Write-Host "✅ Copied env.example" -ForegroundColor Green
} else {
    Write-Host "⚠️ env.example not found in source" -ForegroundColor Red
}

# Copy .gitignore
if (Test-Path "$sourceDir\.gitignore") {
    Write-Host "📄 Copying .gitignore..." -ForegroundColor Yellow
    Copy-Item -Path "$sourceDir\.gitignore" -Destination $destDir -Force
    Write-Host "✅ Copied .gitignore" -ForegroundColor Green
} else {
    Write-Host "⚠️ .gitignore not found in source" -ForegroundColor Red
}

Write-Host "`n✅ Copy completed!" -ForegroundColor Green
Write-Host "`n📋 Files copied:" -ForegroundColor Cyan
Write-Host "  - app/ (entire folder)" -ForegroundColor White
Write-Host "  - scripts/ (entire folder)" -ForegroundColor White
Write-Host "  - requirements.txt" -ForegroundColor White
Write-Host "  - env.example" -ForegroundColor White
Write-Host "  - .gitignore" -ForegroundColor White

Write-Host "`n📝 Next steps:" -ForegroundColor Cyan
Write-Host "  1. cd `"$destDir`"" -ForegroundColor White
Write-Host "  2. git add ." -ForegroundColor White
Write-Host "  3. git commit -m `"Initial commit`"" -ForegroundColor White
Write-Host "  4. git push -u origin main" -ForegroundColor White


