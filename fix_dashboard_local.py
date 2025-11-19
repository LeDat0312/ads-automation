#!/usr/bin/env python3
"""Fix dashboard.py by removing HTML code from lines 953-4903"""

file_path = "app/api/routes/dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original file: {len(lines)} lines")

# Remove HTML code from line 953 to 4903 (indices 952-4902)
# Keep: lines 1-952 + lines 4904-end
new_lines = lines[:952] + lines[4903:]

print(f"Removed {4903 - 952} lines of HTML/CSS/JS code (lines 953-4903)")
print(f"New file: {len(new_lines)} lines")

# Verify the cut points
print(f"\nLine 952 (last kept): {lines[951][:60] if len(lines) > 951 else 'N/A'}")
print(f"Line 4904 (first after cut): {lines[4903][:60] if len(lines) > 4903 else 'N/A'}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("\n✅ File cleaned successfully!")

