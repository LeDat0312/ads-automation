#!/usr/bin/env python3
"""Remove HTML/CSS/JS code from dashboard.py on local machine"""

file_path = "app/api/routes/dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original file: {len(lines)} lines")

# Find where HTML code starts (should be around line 950)
# Look for CSS/HTML patterns
html_start = None
for i in range(940, min(1000, len(lines))):
    line = lines[i]
    if 'gap:' in line or '.back-btn:hover' in line or 'color: rgba' in line:
        html_start = i
        print(f"Found HTML code starting at line {i+1}: {line[:50]}")
        break

# Find where the real get_dashboard_data function starts (should be around line 4904)
real_function_start = None
for i in range(4890, min(4920, len(lines))):
    line = lines[i]
    if '@router.get("/data")' in line or 'async def get_dashboard_data(' in line:
        # Check if this is the real function (not the placeholder)
        if i > 4900:  # The real function should be after line 4900
            real_function_start = i
            print(f"Found real get_dashboard_data at line {i+1}: {line[:50]}")
            break

if html_start and real_function_start:
    # Remove HTML code from html_start to real_function_start-1
    new_lines = lines[:html_start] + lines[real_function_start:]
    print(f"Removed {real_function_start - html_start} lines of HTML/CSS/JS code")
    print(f"New file: {len(new_lines)} lines")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ File cleaned successfully!")
else:
    print("❌ Could not find HTML code boundaries")
    print(f"html_start: {html_start}, real_function_start: {real_function_start}")
    if html_start:
        print(f"Line {html_start+1}: {lines[html_start][:80]}")
    if real_function_start:
        print(f"Line {real_function_start+1}: {lines[real_function_start][:80]}")

