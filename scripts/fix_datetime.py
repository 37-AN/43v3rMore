"""Script to fix datetime.utcnow() deprecations."""
import os
import re

def fix_datetime_utcnow(file_path):
    """Fix datetime.utcnow() calls in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Add timezone import if datetime is imported
    if 'from datetime import' in content and 'timezone' not in content:
        content = re.sub(
            r'from datetime import ([^\n]+)',
            lambda m: f"from datetime import {m.group(1)}, timezone" if 'timezone' not in m.group(1) else m.group(0),
            content
        )

    # Replace datetime.utcnow() with datetime.now(timezone.utc)
    content = content.replace('datetime.utcnow()', 'datetime.now(timezone.utc)')

    # Special case for inline imports
    content = content.replace('__import__("datetime").datetime.utcnow()', 'datetime.now(datetime.UTC)')

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {file_path}")
        return True
    return False

# Process all Python files in src
fixed_count = 0
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, files)
            if fix_datetime_utcnow(file_path):
                fixed_count += 1

print(f"\nFixed {fixed_count} files")
