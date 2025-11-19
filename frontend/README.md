# Facebook Ads Dashboard - React/Vite Frontend

Dashboard quản lý quảng cáo Facebook với React + TypeScript + Vite + TailwindCSS.

## 📁 Cấu trúc thư mục

```
frontend/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.cjs
├── postcss.config.cjs
├── index.html
└── src/
    ├── main.tsx                 # Entry point
    ├── App.tsx                  # Main component
    ├── index.css                # Global styles
    ├── types/
    │   └── dashboard.ts         # TypeScript interfaces
    ├── services/
    │   └── api.ts               # API client (axios)
    ├── utils/
    │   └── formatters.ts        # Utility functions
    └── components/
        ├── SummaryCards.tsx     # Overview cards
        ├── AdsetTable.tsx       # Data table with sort
        ├── FiltersBar.tsx       # Filters (TODO)
        ├── BudgetModal.tsx      # Budget adjustment (TODO)
        └── Pagination.tsx       # Pagination controls (TODO)
```

## 🚀 Development Setup

### 1. Cài đặt dependencies

```bash
cd frontend
npm install
```

### 2. Chạy development server

```bash
npm run dev
```

Frontend sẽ chạy tại: http://localhost:3000

Backend API proxy: http://localhost:8000

### 3. Build cho production

```bash
npm run build
```

Output: `frontend/dist/`

## ⚙️ Backend Integration (FastAPI)

### Option 1: Nginx serve static files (Khuyến nghị cho production)

**1. Build frontend:**
```bash
cd frontend
npm run build
```

**2. Copy build files:**
```bash
cp -r frontend/dist/* /var/www/dashboard/
```

**3. Cấu hình Nginx:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend static files
    location / {
        root /var/www/dashboard;
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /dashboard/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 2: FastAPI serve React build

**1. Update `app/main.py`:**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Mount API routes FIRST
from app.api.routes import dashboard
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# Static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../frontend/dist")

if os.path.exists(FRONTEND_DIR):
    # Serve React assets
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")
    
    # Serve index.html for all other routes (SPA fallback)
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # If path starts with /dashboard or /api, let API handle it
        if full_path.startswith(("dashboard/", "api/")):
            return {"detail": "API endpoint"}
        
        # Otherwise serve React app
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"detail": "Not found"}
```

**2. Build & deploy:**
```bash
# Build frontend
cd frontend
npm run build

# Restart FastAPI
cd ..
sudo systemctl restart your-fastapi-service
```

## 📊 Features

### ✅ Đã implement

- **View Mode Toggle**: Lead Generation / E-Commerce
- **Summary Cards**: 
  - Lead: 6 cards (Tổng chi tiêu, DATA, Checkouts, Active/Paused/Total adsets)
  - Ecom: 6 cards (Tổng chi tiêu, % ADS, Doanh số, Active/Paused/Total adsets)
- **Adset Table**: 
  - Hiển thị toàn bộ metrics theo view mode
  - Client-side sorting (click column header)
  - Checkbox selection
  - Responsive design
- **API Integration**: Axios client với error handling
- **TypeScript**: Full type safety
- **TailwindCSS**: Styling với custom theme

### 🚧 TODO (Chưa implement)

- **FiltersBar**: Date range picker, prefix dropdown, status filter, search
- **BudgetModal**: Bulk budget adjustment với preview
- **Pagination**: Client-side hoặc server-side pagination
- **StatusActions**: Bulk activate/pause adsets
- **Export CSV**: Download table data
- **Real-time updates**: WebSocket hoặc polling
- **Dark mode**: Theme toggle
- **Mobile responsive**: Optimize cho mobile

## 🔧 Configuration

### Environment Variables

Tạo file `.env` trong `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

### API Endpoints

Frontend gọi các endpoint sau:

- `GET /dashboard/data` - Main data endpoint
- `GET /dashboard/settings-status` - Check configuration
- `POST /dashboard/budget/update` - Update budgets
- `POST /dashboard/status/update` - Update adset status

## 📝 Code Style

- **Components**: PascalCase (e.g., `SummaryCards.tsx`)
- **Utilities**: camelCase (e.g., `formatCurrency`)
- **Types**: PascalCase (e.g., `ViewMode`, `DashboardFilters`)
- **Files**: kebab-case hoặc PascalCase
- **UI Text**: 100% tiếng Việt
- **Code**: Tiếng Anh (biến, functions, comments)

## 🐛 Troubleshooting

### Port 3000 đã được sử dụng

```bash
# Thay đổi port trong vite.config.ts
server: {
  port: 3001,  // Đổi port
}
```

### API CORS errors

Backend cần enable CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Build errors

```bash
# Clear cache và rebuild
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 📚 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Axios** - HTTP client
- **date-fns** - Date utilities
- **Lucide React** - Icons

## 🎯 Next Steps

1. Implement FiltersBar component
2. Implement BudgetModal với logic tính ngân sách chính xác
3. Add pagination controls
4. Add export CSV functionality
5. Optimize performance (memoization, virtualization)
6. Add unit tests (Vitest)
7. Add E2E tests (Playwright/Cypress)
8. Setup CI/CD pipeline

## 📞 Support

Nếu có vấn đề, kiểm tra:
1. Backend đang chạy tại port 8000
2. Frontend proxy config đúng
3. API endpoints trả đúng JSON format
4. CORS được enable trên backend
