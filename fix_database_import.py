#!/usr/bin/env python3
"""
Fix circular import in database.py
Move model imports from top level into init_db() function
"""
import re
import sys
import os

def fix_database_import(file_path):
    """Fix circular import by moving model imports into init_db()"""
    
    # Read file
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    skip_imports = False
    in_init_db = False
    init_db_indent = 0
    imports_added = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if we're at Base = declarative_base()
        if 'Base = declarative_base()' in line:
            new_lines.append(line)
            new_lines.append('\n')
            new_lines.append('# Models sẽ được import trong init_db() để tránh circular import\n')
            new_lines.append('\n')
            skip_imports = True
            i += 1
            continue
        
        # Skip model imports at top level
        if skip_imports and any(x in line for x in [
            'from app.models.telegram_update import TelegramUpdate',
            'from app.models.job import Job',
            'from app.models.logic_rule import LogicRule'
        ]):
            # Skip this line and any following blank lines
            i += 1
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            continue
        
        # Check if we're entering init_db() function
        if 'def init_db():' in line:
            in_init_db = True
            init_db_indent = len(line) - len(line.lstrip())
            new_lines.append(line)
            i += 1
            continue
        
        # If we're in init_db() and haven't added imports yet
        if in_init_db and not imports_added:
            # Check if we've reached the first statement (not docstring or comment)
            current_indent = len(line) - len(line.lstrip())
            
            # If we see 'global' or 'settings =', add imports before it
            if line.strip().startswith('global') or line.strip().startswith('settings ='):
                # Add imports with proper indentation
                indent = ' ' * (init_db_indent + 4)
                new_lines.append(f'{indent}# Import models ở đây để tránh circular import\n')
                new_lines.append(f'{indent}from app.models.telegram_update import TelegramUpdate\n')
                new_lines.append(f'{indent}from app.models.job import Job\n')
                new_lines.append(f'{indent}from app.models.logic_rule import LogicRule\n')
                new_lines.append(f'{indent}# Import các models khác nếu có\n')
                new_lines.append('\n')
                imports_added = True
            
            # If we see settings = get_settings(), we're past the point to add imports
            if 'settings = get_settings()' in line:
                # Add imports before this line
                indent = ' ' * (init_db_indent + 4)
                new_lines.insert(-1, f'{indent}# Import models ở đây để tránh circular import\n')
                new_lines.insert(-1, f'{indent}from app.models.telegram_update import TelegramUpdate\n')
                new_lines.insert(-1, f'{indent}from app.models.job import Job\n')
                new_lines.insert(-1, f'{indent}from app.models.logic_rule import LogicRule\n')
                new_lines.insert(-1, f'{indent}# Import các models khác nếu có\n')
                new_lines.insert(-1, '\n')
                imports_added = True
        
        # Check if we're leaving init_db() function
        if in_init_db and line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""'):
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= init_db_indent and 'def ' in line:
                in_init_db = False
                imports_added = False
        
        new_lines.append(line)
        i += 1
    
    # Write file
    with open(file_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Fixed {file_path}")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = 'app/core/database.py'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    # Backup
    backup_path = file_path + '.backup'
    with open(file_path, 'r') as f:
        with open(backup_path, 'w') as b:
            b.write(f.read())
    print(f"📋 Backup created: {backup_path}")
    
    # Fix
    try:
        fix_database_import(file_path)
        print("✅ Success!")
    except Exception as e:
        print(f"❌ Error: {e}")
        # Restore backup
        with open(backup_path, 'r') as b:
            with open(file_path, 'w') as f:
                f.write(b.read())
        print(f"🔄 Restored from backup")
        sys.exit(1)


