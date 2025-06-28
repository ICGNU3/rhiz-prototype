import os
import re
import glob

def get_all_python_files():
    """Get all Python files in the root directory"""
    return [f for f in glob.glob("*.py") if not f.startswith("analyze_")]

def get_imports_from_file(filepath):
    """Extract all imports from a Python file"""
    imports = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find import statements
        import_patterns = [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.update(matches)
            
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    
    return imports

def analyze_usage():
    """Analyze which files are actually used"""
    python_files = get_all_python_files()
    all_imports = set()
    
    # Core entry points
    entry_points = ['main.py', 'app.py', 'api_routes.py', 'api_routes_mobile.py']
    
    print("=== RHIZ APP - UNUSED FILES ANALYSIS ===\n")
    
    # Get all imports from all files
    for file in python_files:
        imports = get_imports_from_file(file)
        all_imports.update(imports)
        
    # Convert file names to module names for comparison
    module_names = {f.replace('.py', '') for f in python_files}
    
    # Find unused files
    unused_files = []
    used_files = []
    
    for file in python_files:
        module_name = file.replace('.py', '')
        if module_name in all_imports or file in entry_points:
            used_files.append(file)
        else:
            unused_files.append(file)
    
    print(f"📊 TOTAL PYTHON FILES: {len(python_files)}")
    print(f"✅ USED FILES: {len(used_files)}")
    print(f"❌ UNUSED FILES: {len(unused_files)}")
    print(f"📈 USAGE RATE: {len(used_files)/len(python_files)*100:.1f}%\n")
    
    print("=== USED FILES ===")
    for file in sorted(used_files):
        print(f"  ✓ {file}")
    
    print(f"\n=== UNUSED FILES ({len(unused_files)}) ===")
    for file in sorted(unused_files):
        print(f"  ✗ {file}")
    
    # Categorize unused files
    print(f"\n=== UNUSED FILE CATEGORIES ===")
    
    demo_files = [f for f in unused_files if 'demo' in f or 'seed' in f or 'test' in f]
    script_files = [f for f in unused_files if 'script' in f or 'fix' in f or 'init' in f]
    legacy_files = [f for f in unused_files if any(word in f for word in ['old', 'backup', 'legacy', 'temp'])]
    other_files = [f for f in unused_files if f not in demo_files + script_files + legacy_files]
    
    if demo_files:
        print(f"🧪 DEMO/TEST FILES ({len(demo_files)}):")
        for f in demo_files:
            print(f"  - {f}")
    
    if script_files:
        print(f"🔧 UTILITY SCRIPTS ({len(script_files)}):")
        for f in script_files:
            print(f"  - {f}")
            
    if legacy_files:
        print(f"📦 LEGACY FILES ({len(legacy_files)}):")
        for f in legacy_files:
            print(f"  - {f}")
            
    if other_files:
        print(f"❓ OTHER UNUSED ({len(other_files)}):")
        for f in other_files:
            print(f"  - {f}")

if __name__ == "__main__":
    analyze_usage()
