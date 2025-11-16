# PowerShell script để kiểm tra thông tin server qua SSH
# Cần cài đặt OpenSSH hoặc sử dụng PuTTY's plink command

param(
    [string]$ServerIP = "54.179.208.122",
    [string]$Username = "adsuser",
    [string]$Password = "@Levandat0312",
    [int]$Port = 22
)

Write-Host "🔍 Đang kết nối đến server..." -ForegroundColor Cyan

# Kiểm tra xem OpenSSH Client có được cài đặt không
$sshPath = Get-Command ssh -ErrorAction SilentlyContinue

if (-not $sshPath) {
    Write-Host "❌ OpenSSH Client không được cài đặt!" -ForegroundColor Red
    Write-Host "Vui lòng cài đặt OpenSSH hoặc sử dụng MobaXterm thay vào đó" -ForegroundColor Yellow
    exit 1
}

# Hàm thực thi SSH command (yêu cầu SSH key hoặc sử dụng sshpass)
function Invoke-SSHCommand {
    param(
        [string]$Command,
        [string]$IP,
        [string]$User,
        [string]$Pass,
        [int]$Port
    )
    
    # Cách 1: Nếu có SSH key (khuyến khích)
    # ssh -i "C:\path\to\key.pem" $User@$IP -p $Port $Command
    
    # Cách 2: Sử dụng sshpass (cần cài đặt trước)
    # echo $Pass | sshpass -p - ssh -o StrictHostKeyChecking=no $User@$IP -p $Port $Command
    
    Write-Host "⚠️  PowerShell không hỗ trợ SSH với password trực tiếp (bảo mật)" -ForegroundColor Yellow
    Write-Host "Vui lòng sử dụng một trong các cách sau:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Cách 1: MobaXterm (bạn đã cài đặt)"
    Write-Host "  Mở MobaXterm, SSH vào server, rồi chạy lệnh:"
    Write-Host "    cd /home/adsuser/ads-automation"
    Write-Host "    ps aux | grep -E 'gunicorn|supervisor|uvicorn|nginx'"
    Write-Host "    sudo supervisorctl status"
    Write-Host "    systemctl status --all | grep ads"
    Write-Host ""
    Write-Host "Cách 2: Cài đặt sshpass trên Windows"
    Write-Host "  Hoặc tạo SSH key (.pem) để tôi có thể tạo script tự động"
}

Invoke-SSHCommand -Command "ps aux | grep -E 'gunicorn|supervisor|uvicorn' && sudo supervisorctl status" -IP $ServerIP -User $Username -Pass $Password -Port $Port

Write-Host ""
Write-Host "📋 Thông tin server:" -ForegroundColor Green
Write-Host "  IP: $ServerIP"
Write-Host "  Port: $Port"
Write-Host "  Username: $Username"
Write-Host "  Project Path: /home/adsuser/ads-automation/"
Write-Host ""
Write-Host "💡 Vui lòng kiểm tra thủ công trong MobaXterm để lấy thông tin services" -ForegroundColor Yellow
