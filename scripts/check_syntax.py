#!/usr/bin/env python3
"""
Script để check syntax errors trong settings.py
"""
import ast
import sys

def check_syntax(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Try to compile
        compile(code, file_path, 'exec')
        print(f"✅ {file_path}: No syntax errors")
        return True
    except SyntaxError as e:
        print(f"❌ {file_path}: Syntax error at line {e.lineno}")
        print(f"   {e.msg}")
        if e.text:
            print(f"   {e.text.strip()}")
            if e.offset:
                print(f"   {' ' * (e.offset - 1)}^")
        return False
    except Exception as e:
        print(f"❌ {file_path}: Error: {e}")
        return False

if __name__ == "__main__":
    file_path = "app/api/routes/settings.py"
    success = check_syntax(file_path)
    sys.exit(0 if success else 1)

