# 🚀 PowerShell Deployment Script for ADS Automation
# Yêu cầu: sshpass hoặc SSH key (.pem)
# Usage: .\deploy-remote.ps1 -Action "deploy" -Backup $true -Restart $true

param(
    [string]$ServerIP = "54.179.208.122",
    [string]$Username = "adsuser",
    [string]$Password = "@Levandat0312",
    [int]$Port = 22,
    [string]$Action = "deploy",  # deploy, check, restart
    [switch]$Backup,
    [switch]$Migrate,
    [switch]$Restart,
    [string]$KeyPath  # Path to .pem file if using SSH key
)

# ===== CONFIG =====
$ProjectPath = "/home/adsuser/ads-automation"
$VenvPath = "/home/adsuser/ads-automation/venv"
$DeployScript = "$PSScriptRoot\deploy.sh"
$CheckScript = "$PSScriptRoot\check-services.sh"

# ===== COLORS =====
function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Error-Custom { Write-Host "❌ $args" -ForegroundColor Red }
function Write-Warning-Custom { Write-Host "⚠️  $args" -ForegroundColor Yellow }
function Write-Info { Write-Host "ℹ️  $args" -ForegroundColor Cyan }

# ===== CHECK REQUIREMENTS =====
Write-Host ""
Write-Host "🚀 ADS Automation - Remote Deployment" -ForegroundColor Blue
Write-Host "=====================================" -ForegroundColor Blue
Write-Host ""

# Check if we have sshpass or SSH key
$hasSshPass = $null -ne (Get-Command sshpass -ErrorAction SilentlyContinue)
$hasOpenSSH = $null -ne (Get-Command ssh -ErrorAction SilentlyContinue)

if (-not $hasOpenSSH) {
    Write-Error-Custom "OpenSSH is not installed!"
    Write-Info "Please install OpenSSH for Windows or use PuTTY/MobaXterm instead"
    exit 1
}

Write-Success "OpenSSH is available"

# ===== BUILD SSH COMMAND =====
$SSHBase = "ssh"

if ($KeyPath -and (Test-Path $KeyPath)) {
    $SSHBase += " -i `"$KeyPath`""
    Write-Success "Using SSH key: $KeyPath"
} elseif ($hasSshPass) {
    # Use sshpass for password authentication
    Write-Success "Using sshpass for password authentication"
} else {
    Write-Warning-Custom "No SSH key provided and sshpass not installed"
    Write-Info "For password authentication, install sshpass:"
    Write-Info "  choco install sshpass  (requires Chocolatey)"
    Write-Info "Or provide SSH key via -KeyPath parameter"
    exit 1
}

$SSHBase += " -p $Port $Username@$ServerIP"

# ===== EXECUTE ACTION =====
Write-Info "Server: $ServerIP:$Port"
Write-Info "User: $Username"
Write-Info "Project: $ProjectPath"
Write-Host ""

switch ($Action.ToLower()) {
    "check" {
        Write-Info "Checking server services..."
        Write-Info ""
        
        if ($KeyPath) {
            ssh -i "$KeyPath" -p $Port $Username@$ServerIP "cd /home/adsuser && ls -la check-services.sh 2>/dev/null && bash check-services.sh || echo 'Script not found on server'"
        } else {
            Write-Warning-Custom "Password authentication for this action requires MobaXterm"
            Write-Info "Please use MobaXterm to check services manually"
        }
    }
    
    "deploy" {
        Write-Host "📥 Starting deployment..." -ForegroundColor Yellow
        
        $DeployCmd = "cd $ProjectPath && bash deploy.sh"
        if ($Backup) { $DeployCmd += " --backup" }
        if ($Migrate) { $DeployCmd += " --migrate" }
        if ($Restart) { $DeployCmd += " --restart" }
        
        Write-Info "Command: $DeployCmd"
        Write-Host ""
        
        if ($KeyPath) {
            Invoke-Expression "ssh -i `"$KeyPath`" -p $Port $Username@$ServerIP `"$DeployCmd`""
        } else {
            Write-Warning-Custom "Deployment with password authentication requires MobaXterm"
            Write-Info "Run this command in MobaXterm SSH terminal:"
            Write-Host "  cd $ProjectPath && bash deploy.sh" -ForegroundColor Cyan
        }
    }
    
    "restart" {
        Write-Host "🔄 Restarting services..." -ForegroundColor Yellow
        
        $RestartCmd = "cd $ProjectPath && bash deploy.sh --restart"
        
        if ($KeyPath) {
            Invoke-Expression "ssh -i `"$KeyPath`" -p $Port $Username@$ServerIP `"$RestartCmd`""
        } else {
            Write-Warning-Custom "Restart with password authentication requires MobaXterm"
        }
    }
    
    default {
        Write-Error-Custom "Unknown action: $Action"
        Write-Info "Available actions: check, deploy, restart"
        exit 1
    }
}

Write-Host ""
Write-Host "✅ Command executed" -ForegroundColor Green
Write-Host ""

# ===== USAGE INFO =====
Write-Host "📝 Usage Examples:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check services (requires SSH key):" -ForegroundColor Gray
Write-Host "  .\deploy-remote.ps1 -Action check -KeyPath C:\path\to\key.pem" -ForegroundColor Gray
Write-Host ""
Write-Host "Simple deployment (code pull only):" -ForegroundColor Gray
Write-Host "  .\deploy-remote.ps1 -Action deploy -KeyPath C:\path\to\key.pem" -ForegroundColor Gray
Write-Host ""
Write-Host "Full deployment (backup + migrate + restart):" -ForegroundColor Gray
Write-Host "  .\deploy-remote.ps1 -Action deploy -KeyPath C:\path\to\key.pem -Backup -Migrate -Restart" -ForegroundColor Gray
Write-Host ""
Write-Host "For password authentication, use MobaXterm instead:" -ForegroundColor Gray
Write-Host "  1. Open MobaXterm" -ForegroundColor Gray
Write-Host "  2. SSH: ssh adsuser@54.179.208.122" -ForegroundColor Gray
Write-Host "  3. Run: cd /home/adsuser/ads-automation && bash deploy.sh --backup --migrate --restart" -ForegroundColor Gray
Write-Host ""
