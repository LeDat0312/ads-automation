#!/usr/bin/env python3
"""Script to remove HTML/CSS/JS code from dashboard.py"""

import re

file_path = "app/api/routes/dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line numbers where HTML code starts and ends
# HTML code starts around line 984 (index 983) and ends before line 4936 (index 4935)
# where the real get_dashboard_data function starts

start_line = 984  # Where HTML code starts
end_line = 4935   # Just before the real get_dashboard_data function

print(f"Original file has {len(lines)} lines")
print(f"Removing lines {start_line} to {end_line} (HTML/CSS/JS code)")

# Keep lines before HTML code and after it
new_lines = lines[:start_line-1] + lines[end_line:]

print(f"New file will have {len(new_lines)} lines")

# Write the cleaned file
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ Removed {end_line - start_line + 1} lines of HTML/CSS/JS code")
print(f"✅ File cleaned successfully!")

