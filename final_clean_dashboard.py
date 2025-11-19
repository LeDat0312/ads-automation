#!/usr/bin/env python3
"""Final cleanup: Remove all HTML code from dashboard.py"""

file_path = "app/api/routes/dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original file: {len(lines)} lines")

# Remove HTML code from line 1006 to 4939 (indices 1005-4938)
# Keep: lines 1-1005 + lines 4940-end
new_lines = lines[:1005] + lines[4939:]

print(f"Removed {4939 - 1005} lines of HTML/CSS/JS code (lines 1006-4939)")
print(f"New file: {len(new_lines)} lines")

# Verify
print(f"\nLine 1005 (last kept): {lines[1004][:60] if len(lines) > 1004 else 'N/A'}")
print(f"Line 4940 (first after cut): {lines[4939][:60] if len(lines) > 4939 else 'N/A'}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("\n✅ File cleaned successfully!")

