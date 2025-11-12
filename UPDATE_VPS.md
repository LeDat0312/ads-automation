# Hướng dẫn cập nhật VPS

## Bước 1: Pull code mới từ GitHub

```bash
cd ~/ads-automation
git pull origin main
```

## Bước 2: Xóa Python cache (nếu cần)

```bash
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
```

## Bước 3: Restart Supervisor services

```bash
sudo supervisorctl restart ads-automation-api
sudo supervisorctl restart ads-automation-worker:*
```

## Bước 4: Kiểm tra trạng thái

```bash
sudo supervisorctl status
```

## Bước 5: Kiểm tra logs (nếu có lỗi)

```bash
# Logs API
sudo tail -50 /var/log/ads-automation/api.out.log
sudo tail -50 /var/log/ads-automation/api.err.log

# Logs Worker
sudo tail -50 /var/log/ads-automation/worker.out.log
sudo tail -50 /var/log/ads-automation/worker.err.log
```

## Bước 6: Test Telegram bot

Gửi một lệnh nặng (ví dụ `/statusads`) và kiểm tra xem:
- Bot có trả lời "⏳ Đang xử lý..." ngay không
- Bot có gửi progress updates không
- Bot có trả về kết quả cuối cùng không

