#!/usr/bin/env python3
"""Final cleanup: Remove HTML code from lines 967-4908"""

file_path = "app/api/routes/dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original file: {len(lines)} lines")

# Remove HTML code from line 967 to 4908 (indices 966-4907)
# Keep: lines 1-966 + lines 4909-end
new_lines = lines[:966] + lines[4908:]

print(f"Removed {4908 - 966} lines of HTML/CSS/JS code (lines 967-4908)")
print(f"New file: {len(new_lines)} lines")

# Verify
print(f"\nLine 966 (last kept): {lines[965][:60] if len(lines) > 965 else 'N/A'}")
print(f"Line 4909 (first after cut): {lines[4908][:60] if len(lines) > 4908 else 'N/A'}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("\n✅ File cleaned successfully!")

