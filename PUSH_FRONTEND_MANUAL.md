# Hướng dẫn Push Frontend Code lên GitHub (Thủ công)

## Vấn đề:
Git repository đang ở thư mục home, không phải thư mục project. Cần push từ đúng thư mục.

## Cách thực hiện:

### Bước 1: Mở Git Bash hoặc PowerShell trong thư mục project

Tìm thư mục project (có chứa folder `frontend`):
```
C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet
```

### Bước 2: Kiểm tra git status
```bash
git status
```

### Bước 3: Add các file frontend
```bash
# Add tất cả file frontend
git add frontend/

# Hoặc add từng file cụ thể:
git add frontend/src/components/LevelTabs.tsx
git add frontend/src/components/PaginationControls.tsx
git add frontend/src/components/BudgetEditor.tsx
git add frontend/src/components/FiltersBar.tsx
git add frontend/src/components/AdsetTable.tsx
git add frontend/src/components/SummaryCards.tsx
git add frontend/src/App.tsx
git add frontend/src/services/api.ts
git add frontend/src/types/dashboard.ts
```

### Bước 4: Kiểm tra files đã được staged
```bash
git status --short
```

### Bước 5: Commit
```bash
git commit -m "Add React+Vite frontend: LevelTabs, PaginationControls, BudgetEditor, Status toggle, Account filter, SummaryCards update"
```

### Bước 6: Push
```bash
git push origin main
```

## Nếu gặp lỗi "Everything up-to-date":

Có nghĩa là các file frontend đã được commit và push trước đó. Để kiểm tra:

```bash
# Xem các file frontend đã có trong git
git ls-files frontend/

# Xem commit gần nhất
git log --oneline -5

# Xem các file đã thay đổi nhưng chưa commit
git status
```

## Nếu thư mục project không có git repository:

Cần init git repository mới hoặc clone từ GitHub:

```bash
# Option 1: Clone repository về thư mục project
cd "C:\Users\Foxy\Downloads\File 5h_4-11\Code 18h 4-11 bản 3 sheet"
git clone https://github.com/LeDat0312/ads-automation.git .

# Option 2: Init repository mới và link với remote
git init
git remote add origin https://github.com/LeDat0312/ads-automation.git
git pull origin main
```

