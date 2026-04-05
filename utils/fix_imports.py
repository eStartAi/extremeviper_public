#!/usr/bin/env python3
# ============================================================
# fix_imports.py — auto-detect & patch incorrect imports
# ============================================================

import os
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TARGET_FOLDERS = ["core", "utils", "notify", "brokers"]

def find_imports(line):
    pattern = r"from\s+(\w+)\s+import"
    match = re.search(pattern, line)
    return match.group(1) if match else None

def correct_import(module_name):
    """Return correct dotted path based on project layout."""
    for folder in TARGET_FOLDERS:
        if (BASE / folder / f"{module_name}.py").exists():
            return f"{folder}.{module_name}"
    return None

def scan_and_fix(pyfile):
    fixed = False
    lines = pyfile.read_text().splitlines()
    for i, line in enumerate(lines):
        mod = find_imports(line)
        if mod:
            correct = correct_import(mod)
            if correct and correct != mod:
                print(f"🔧 {pyfile.name}: fixing 'from {mod}' → 'from {correct}'")
                lines[i] = line.replace(f"from {mod}", f"from {correct}")
                fixed = True
    if fixed:
        pyfile.write_text("\n".join(lines))

def main():
    print(f"🔎 Scanning for import mismatches in {BASE} ...\n")
    for root, _, files in os.walk(BASE):
        for file in files:
            if file.endswith(".py") and "fix_imports" not in file:
                scan_and_fix(Path(root) / file)
    print("\n✅ Import scan complete. All detected issues fixed.")

if __name__ == "__main__":
    main()

