# Building Save-it-Scotty Standalone Executable

Quick guide to building a standalone Windows executable - **NO CONFIGURATION REQUIRED!**

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/Save-it-Scotty.git
cd Save-it-Scotty
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Build executable (NO CONFIGURATION NEEDED!)
python build_exe.py

# 3. Done! Test it
dist\SaveItScotty.exe
```

## What You Need

### Python Environment

- Python 3.8+ (with pip)
- Windows OS (for building Windows exe)
- ~200 MB disk space

**That's it! No Azure AD setup, no configuration, no credentials needed.**

## Build Process

### One Command Build

Run the build script:

```bash
python build_exe.py
```

This will:
1. Check requirements (PyInstaller)
2. Clean previous builds
3. Create PyInstaller spec file
4. Build the executable (~2-5 minutes)
5. Output: `dist/SaveItScotty.exe` (~30-50 MB)

### Test

```bash
cd dist
SaveItScotty.exe
```

Verify:
- ✅ GUI launches
- ✅ Auto-detect finds your username
- ✅ Can browse for output directory
- ✅ Extraction options are available

## What It Extracts

### LOCAL DATA ONLY:
- ✅ User folders (Desktop, Documents, Downloads, AppData)
- ✅ Email archives (PST/OST files)
- ✅ Browser data (Chrome, Edge, Firefox bookmarks, history)

### NOT INCLUDED:
- ❌ OneDrive (use Microsoft 365 admin portal)
- ❌ SharePoint (use Microsoft 365 admin portal)
- ❌ Teams chats (use Microsoft 365 admin portal)

**Why local only?** No Azure AD App Registration required, no credentials to manage, simpler deployment, zero configuration!

## Troubleshooting Build Issues

### "PyInstaller not found"

```bash
pip install pyinstaller
```

### Build fails with "ImportError"

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Executable is too large (>100 MB)

Normal size is 30-50 MB. If larger, try:
```bash
python build_exe.py  # Script auto-cleans before build
```

### Antivirus blocks executable

- Windows Defender may flag PyInstaller executables
- Add exclusion: `dist/SaveItScotty.exe`
- Sign the executable with your code signing certificate (production)

## Customization

### Change Default Archive Password

Edit `src/gui.py`, find:

```python
'archive_password': '',  # Set a default password here if desired
```

Change to:

```python
'archive_password': 'YourDefaultPassword123',
```

Then rebuild with `python build_exe.py`

### Add Company Logo/Icon

1. Create `icon.ico` (256x256 recommended)
2. Edit `build_exe.py`, find `icon=None` and change to `icon='icon.ico'`
3. Rebuild

### Change Output Name

After build completes, rename the exe:
```bash
ren dist\SaveItScotty.exe "YourCompanyName-DataExtractor.exe"
```

## Distribution

### Single File Deployment

The executable is completely standalone:
- ✅ No Python installation required
- ✅ No DLL dependencies (all bundled)
- ✅ NO config files needed
- ✅ NO Azure credentials needed
- ✅ Runs on Windows 10/11 (x64)

### Deployment Options

**USB Drive**:
```
SaveItScotty.exe → Copy to USB → Run on target machine
```

**Network Share**:
```
\\fileserver\IT-Tools\SaveItScotty.exe
```

**Group Policy**:
- Software Installation GPO
- Deploy to IT Admins OU

**SCCM/Intune**:
- Package as application
- Deploy to IT Administrators group

## Security Notes

### No Embedded Credentials

This version has **NO credentials embedded** because it doesn't connect to any cloud services. It only extracts local device data.

### Recommended Security Practices

1. **Access Control**: Store exe on restricted network share
2. **Auditing**: Log all executions (Windows Event Log)
3. **Archive Passwords**: Use password-protected ZIP for extracted data
4. **Data Handling**: Move extracted data to secure storage immediately

## Rebuilding

To rebuild after making changes:

```bash
# Make your changes to src/gui.py or other modules
python build_exe.py

# Replace old exe in distribution locations
copy dist\SaveItScotty.exe \\fileserver\IT-Tools\
```

## Advanced: Build Variants

### Console Mode (shows terminal window)

Edit the spec content in `build_exe.py`, change:
```python
console=False,  # Change to True
```

### Debug Build (verbose logging)

Edit the spec content in `build_exe.py`, change:
```python
debug=False,  # Change to True
```

## File Locations After Build

```
Save-it-Scotty/
├── dist/
│   └── SaveItScotty.exe          ← Your standalone executable
├── build/                        ← Temporary build files (can delete)
├── SaveItScotty.spec            ← PyInstaller spec file
└── ...
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python build_exe.py` | Build standalone executable |
| `dist\SaveItScotty.exe` | Run the built application |

## Need Help?

- **Build Errors**: Check you have Python 3.8+ and all dependencies installed
- **Runtime Errors**: Run from command prompt to see error messages
- **Size Issues**: Normal exe is 30-50 MB

## Comparison: Local-Only vs Cloud-Enabled

| Feature | This Version (Local-Only) | Cloud-Enabled Version |
|---------|---------------------------|----------------------|
| **Setup Complexity** | ⭐ Simple (no setup) | ⭐⭐⭐ Complex (Azure AD) |
| **Build Process** | 1 command | 2 commands + config |
| **Credentials** | None needed | Azure AD required |
| **Local Data** | ✅ Yes | ✅ Yes |
| **OneDrive** | ❌ No | ✅ Yes |
| **SharePoint** | ❌ No | ✅ Yes |
| **Teams Chats** | ❌ No | ✅ Yes |
| **File Size** | 30-50 MB | 50-100 MB |

**Recommendation**: Use this local-only version unless you specifically need automated cloud extraction.

---

**Next Steps**: See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.
