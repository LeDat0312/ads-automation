#!/usr/bin/env python3
"""Remove all HTML/CSS/JS code from dashboard.py between lines 944-4935"""

file_path = "app/api/routes/dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original file: {len(lines)} lines")

# Remove lines 944-4935 (indices 943-4934)
# Keep lines 1-943 and 4936-end
start_idx = 943  # Line 944 (0-indexed: 943)
end_idx = 4934   # Line 4935 (0-indexed: 4934)

new_lines = lines[:start_idx] + lines[end_idx+1:]

print(f"Removed {end_idx - start_idx + 1} lines (HTML/CSS/JS)")
print(f"New file: {len(new_lines)} lines")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ File cleaned successfully!")
print(f"✅ Removed HTML/CSS/JS code from lines {start_idx+1} to {end_idx+1}")

