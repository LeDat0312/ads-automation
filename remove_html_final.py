#!/usr/bin/env python3
"""Final fix: Remove all HTML code from dashboard.py"""

file_path = "app/api/routes/dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original file: {len(lines)} lines")

# Find the start of HTML code (should be around line 967)
html_start = None
for i in range(965, min(980, len(lines))):
    if '/* Settings Status */' in lines[i] or '.settings-status' in lines[i]:
        html_start = i
        print(f"Found HTML code starting at line {i+1}")
        break

# Find the real get_dashboard_data function (should be around line 4913)
real_function_start = None
for i in range(4910, min(4920, len(lines))):
    if '@router.get("/data")' in lines[i] and 'request: Request' in lines[i+1]:
        real_function_start = i
        print(f"Found real get_dashboard_data at line {i+1}")
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
    print("❌ Could not find boundaries")
    print(f"html_start: {html_start}, real_function_start: {real_function_start}")

