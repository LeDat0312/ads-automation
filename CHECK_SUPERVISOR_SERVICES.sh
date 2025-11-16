#!/bin/bash
# Script để kiểm tra tên services trong supervisor

echo "📊 Kiểm tra tên services trong supervisor..."
echo ""

# Liệt kê tất cả services
echo "Danh sách tất cả services:"
sudo supervisorctl status

echo ""
echo "📝 Các lệnh hữu ích:"
echo "  - Xem tất cả services: sudo supervisorctl status"
echo "  - Xem config: sudo supervisorctl reread"
echo "  - Restart tất cả: sudo supervisorctl restart all"
echo "  - Xem logs: sudo supervisorctl tail -f <service_name>"


