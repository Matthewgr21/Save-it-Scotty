# Building Save-it-Scotty Standalone Executable

Quick guide to building a standalone Windows executable with embedded Azure AD credentials.

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/Save-it-Scotty.git
cd Save-it-Scotty
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure Azure credentials (interactive)
python build_config.py

# 3. Build executable
python build_exe.py

# 4. Test it
dist\SaveItScotty.exe
```

## What You Need

### Azure AD App Registration

Create an app registration in Azure AD with these settings:

**API Permissions** (Application, with admin consent):
- `User.Read.All` - Read all users
- `Files.Read.All` - Read all files
- `Sites.Read.All` - Read all sites
- `Chat.Read.All` - Read all chats
- `Mail.Read` - Read all mail

**You'll need**:
- Tenant ID (from app overview)
- Client ID (from app overview)
- Client Secret (from Certificates & secrets)

### Python Environment

- Python 3.8+ (with pip)
- Windows OS (for building Windows exe)
- ~500 MB disk space

## Build Process

### Step 1: Configure

Run the configuration wizard:

```bash
python build_config.py
```

Enter when prompted:
- Azure AD Tenant ID: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Azure AD Client ID: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Azure AD Client Secret: `your~secret~value`
- Archive Password (optional): `YourDefaultPassword123`

This creates `src/embedded_config.py` with your credentials.

**⚠️ IMPORTANT**: Never commit `embedded_config.py` to version control!

### Step 2: Build

Run the build script:

```bash
python build_exe.py
```

This will:
1. Check requirements (PyInstaller, embedded config)
2. Clean previous builds
3. Create PyInstaller spec file
4. Build the executable (~2-5 minutes)
5. Output: `dist/SaveItScotty.exe` (~50-100 MB)

### Step 3: Test

```bash
cd dist
SaveItScotty.exe
```

Verify:
- ✅ GUI launches
- ✅ Auto-detect finds your username
- ✅ Can browse for output directory
- ✅ Extraction options are available

## Troubleshooting Build Issues

### "PyInstaller not found"

```bash
pip install pyinstaller
```

### "embedded_config.py not found"

Run `python build_config.py` first.

### Build fails with "ImportError"

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Executable is too large (>200 MB)

Normal size is 50-100 MB. If larger:
- Check for duplicate dependencies
- Clean build: `python build_exe.py` (it auto-cleans)

### Antivirus blocks executable

- Windows Defender may flag PyInstaller executables
- Add exclusion: `dist/SaveItScotty.exe`
- Sign the executable with your code signing certificate (production)

## Customization

### Change Default Settings

Edit `build_config.py` before running it, or manually edit `src/embedded_config.py` after creation.

### Add Company Logo/Icon

1. Create `icon.ico` (256x256 recommended)
2. Edit `build_exe.py`, find `icon=None` and change to `icon='icon.ico'`
3. Rebuild

### Change Output Name

Edit `SaveItScotty.spec`:
```python
name='SaveItScotty',  # Change this
```

## Distribution

### Single File Deployment

The executable is completely standalone:
- ✅ No Python installation required
- ✅ No DLL dependencies (all bundled)
- ✅ No config files needed (credentials embedded)
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

### Embedded Credentials

The Azure AD credentials are compiled into the exe. They can be extracted with:
- Decompilers (PyInstaller extractors)
- Memory dumps (while running)
- Binary string searches

**Mitigations**:
- Only distribute to authorized IT staff
- Use network access controls
- Monitor Azure AD sign-in logs
- Rotate secrets regularly (rebuild exe)

### Recommended Security Practices

1. **Access Control**: Store exe on restricted network share
2. **Monitoring**: Enable Azure AD sign-in logging
3. **Rotation**: Rebuild with new secrets every 6-12 months
4. **Auditing**: Log all executions (Windows Event Log)
5. **Principle of Least Privilege**: Consider separate app registrations per team

## Rebuilding with New Credentials

When secrets expire or need rotation:

```bash
# 1. Update credentials
python build_config.py

# 2. Rebuild
python build_exe.py

# 3. Replace old exe in distribution locations
copy dist\SaveItScotty.exe \\fileserver\IT-Tools\

# 4. Test with new credentials
```

## Advanced: Build Variants

### Console Mode (shows terminal window)

Edit `SaveItScotty.spec`:
```python
console=True,  # Change from False
```

### Debug Build (verbose logging)

Edit `SaveItScotty.spec`:
```python
debug=True,  # Change from False
```

### Multiple Configurations

Create separate config files:
```bash
python build_config.py  # Creates embedded_config.py
mv src/embedded_config.py src/embedded_config_prod.py
python build_config.py  # Create test config
mv src/embedded_config.py src/embedded_config_test.py

# Switch between them:
cp src/embedded_config_prod.py src/embedded_config.py
python build_exe.py
```

## File Locations After Build

```
Save-it-Scotty/
├── dist/
│   └── SaveItScotty.exe          ← Your standalone executable
├── build/                        ← Temporary build files (can delete)
├── SaveItScotty.spec            ← PyInstaller spec file
├── src/
│   └── embedded_config.py       ← Your Azure credentials (DO NOT COMMIT!)
└── ...
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python build_config.py` | Configure Azure credentials |
| `python build_exe.py` | Build standalone executable |
| `dist\SaveItScotty.exe` | Run the built application |
| `git status` | Check for embedded_config.py (should be ignored) |

## Need Help?

- **Build Errors**: Check you have Python 3.8+ and all dependencies installed
- **Runtime Errors**: Run from command prompt to see error messages
- **Azure Errors**: Verify API permissions and admin consent
- **Size Issues**: Normal exe is 50-100 MB, up to 150 MB is acceptable

---

**Next Steps**: See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.
