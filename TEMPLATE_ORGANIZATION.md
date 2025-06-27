# Template Organization Plan

## Current Templates (46 total)

### ✅ KEEP - Core Application Templates (React Primary UI)
- `base.html` - Base template for any server-rendered pages
- `base_minimal.html` - Minimal base for simple pages
- `login.html` - Authentication login page

### ✅ KEEP - Organized Subdirectories
- `intelligence/` - AI and intelligence features
- `monique/` - CRM functionality 
- `mobile/` - PWA mobile features
- `coordination/` - Collaboration features
- `discovery/` - Network discovery
- `trust/` - Trust insights system

### ❌ REMOVE - Replaced by React Frontend
- Legacy dashboard templates (React handles all dashboard UI now)
- Old contact/goal management templates (React frontend covers this)
- Redundant signup/auth templates (simplified to essentials)

### 🔧 ORGANIZE - Keep Useful, Archive Others
- Conference mode templates
- Email integration templates  
- CSV import templates
- Settings templates

## Cleanup Actions

1. **Remove Duplicate/Legacy Templates**
   - Old dashboard variants
   - Replaced contact management templates
   - Redundant auth templates

2. **Verify Template Usage**
   - Check which templates are actually referenced in routes
   - Remove orphaned templates

3. **Organize Active Templates**
   - Ensure proper subdirectory structure
   - Verify template inheritance works correctly