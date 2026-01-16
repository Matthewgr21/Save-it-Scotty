# Save-it-Scotty

**Standalone Employee Offboarding Data Extraction Tool for Windows**

A dead-simple, standalone Windows application for IT administrators to extract local device data during employee offboarding. **No Python, no Azure AD, no configuration required** on endpoints.

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Why Save-it-Scotty?

✅ **Zero Configuration** - No Azure AD setup, no credentials to manage
✅ **One-Click Build** - Single command builds the executable
✅ **Completely Standalone** - No Python or dependencies on endpoints
✅ **Simple GUI** - Point, click, extract
✅ **Auto-Detection** - Automatically detects current Windows user
✅ **Small & Fast** - ~30-50 MB executable

## What It Extracts

### LOCAL DEVICE DATA:
- 📁 **User Folders**: Desktop, Documents, Downloads, AppData
- 📧 **Email Archives**: Outlook PST and OST files
- 🌐 **Browser Data**: Bookmarks, history, saved credentials from Chrome, Edge, Firefox
- 📦 **ZIP Archives**: Optional password-protected archives

### NOT INCLUDED (BY DESIGN):
- ❌ OneDrive → Use Microsoft 365 admin portal
- ❌ SharePoint → Use Microsoft 365 admin portal
- ❌ Teams → Use Microsoft 365 admin portal

**Why local-only?** Maximum simplicity. No Azure AD registration, no credential management, zero configuration.

## Quick Start for IT Admins

### Option 1: Use Pre-Built Executable (Easiest)

If your IT team has already built the executable:

1. Copy `SaveItScotty.exe` to the target machine
2. Right-click → **Run as Administrator**
3. Click "Auto-Detect Current User"
4. Click "Start Extraction"
5. Done!

### Option 2: Build Your Own (5 Minutes)

```bash
# Clone repository
git clone https://github.com/yourusername/Save-it-Scotty.git
cd Save-it-Scotty

# Install dependencies
pip install -r requirements.txt

# Build the executable (NO CONFIGURATION NEEDED!)
python build_exe.py

# Your executable is ready
dist\SaveItScotty.exe
```

That's it! No Azure AD setup, no credentials to configure.

📖 **Detailed instructions**: [BUILD.md](BUILD.md)

## Requirements

### For Building the Executable (One-Time)
- Windows 10/11
- Python 3.8+
- ~5 minutes

### For Running the Executable (Every Time)
- Windows 10/11 (x64)
- Administrator privileges (recommended)
- **That's it!** No Python, no dependencies, no configuration

## Screenshots

### Main Interface
```
┌──────────────────────────────────────────────────────┐
│              Save-it-Scotty                         │
│   Employee Offboarding Data Extraction Tool         │
│              - Local Data Only -                     │
├──────────────────────────────────────────────────────┤
│ Employee Information                                 │
│   Windows Username: [jdoe       ]  [Auto-Detect]    │
│   Email (optional): [jdoe@company.com]              │
├──────────────────────────────────────────────────────┤
│ Output Location                                      │
│   [C:\Users\Admin\Desktop\Extracted_Data] [Browse]  │
├──────────────────────────────────────────────────────┤
│ Extraction Options - Local Device Data               │
│   ☑ User Folders (Desktop, Documents, Downloads...) │
│   ☑ Email Archives (PST/OST files)                  │
│   ☑ Browser Data (Chrome, Edge, Firefox)            │
│                                                      │
│   ☑ Create password-protected ZIP archive           │
│                                                      │
│   Note: Cloud data must be extracted separately     │
│   through Microsoft 365 admin portal.               │
├──────────────────────────────────────────────────────┤
│ Progress                                             │
│   [████████████░░░░░░░░░]  60%                      │
│                                                      │
│   [14:23:15] Starting LOCAL data extraction...      │
│   [14:23:20] ✓ Local files: 1,247 files copied      │
│   [14:24:10] ✓ Email archives: 2 PST found          │
├──────────────────────────────────────────────────────┤
│ [Start Extraction] [Cancel] [Clear Log]    [Exit]   │
└──────────────────────────────────────────────────────┘
```

## Usage

### Step-by-Step

1. **Launch**: Double-click `SaveItScotty.exe` (Run as Administrator)

2. **Auto-Detect**: Click "Auto-Detect Current User"
   - Automatically fills in Windows username
   - Suggests email (optional field)

3. **Configure** (optional):
   - Change output directory
   - Uncheck any extraction options you don't want

4. **Extract**: Click "Start Extraction"
   - Watch real-time progress
   - Wait for completion

5. **Review**: Check the extraction report

6. **Secure**: Move data to secure storage, delete from local machine

## Output Structure

```
Desktop\Extracted_Data\
└── jdoe_20240115_143022\
    ├── local_data\
    │   ├── Desktop\
    │   ├── Documents\
    │   ├── Downloads\
    │   └── AppData\
    ├── email_archives\
    │   ├── mailbox.pst
    │   └── archive.ost
    ├── browser_data\
    │   ├── chrome\
    │   ├── edge\
    │   └── firefox\
    ├── extraction_report.txt
    └── extraction_report.json

Optional: jdoe_20240115_143022.zip (password-protected)
```

## Deployment

### Manual (Simplest)
Copy to USB drive or network share, run on target machine

### Network Share
```
\\fileserver\IT-Tools\SaveItScotty.exe
```

### Group Policy
Deploy via Software Installation GPO to IT Admins OU

### SCCM/Intune
Package as application and deploy to IT admin devices

📖 **Full deployment guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

## Building

### One Command

```bash
python build_exe.py
```

No configuration wizard, no Azure AD setup, no embedded credentials needed.

### What Happens

1. Checks PyInstaller is installed
2. Cleans previous builds
3. Creates PyInstaller spec
4. Builds `dist/SaveItScotty.exe` (~30-50 MB)
5. Done in 2-5 minutes

📖 **Full build guide**: [BUILD.md](BUILD.md)

## Customization

### Change Default Archive Password

Edit `src/gui.py`:
```python
'archive_password': 'YourPassword123',
```

### Add Company Icon

1. Create `icon.ico`
2. Edit `build_exe.py`, set `icon='icon.ico'`
3. Rebuild

## Troubleshooting

### "Permission Denied"
- Run as Administrator
- Ensure target user is logged out

### "Could not find user profile"
- Verify username is correct
- Check `C:\Users\{username}` exists

### Antivirus Blocks Exe
- Add exception for SaveItScotty.exe
- Consider code signing for production

### Extraction is Slow
- Normal for large datasets
- Local data only, no network delays

## Cloud Data Extraction

This tool extracts **local data only**. For cloud data:

### OneDrive
1. Go to Microsoft 365 Admin Center
2. Users → Active Users → Select user
3. OneDrive → Create link to download files
4. Download archive

### SharePoint
1. Go to SharePoint Admin Center
2. Sites → Navigate to user's MySite
3. Site contents → Documents
4. Download as needed

### Teams
1. Go to Microsoft 365 Compliance Center
2. Content search → New search
3. Search user's Teams messages
4. Export results

**Alternative**: There's a cloud-enabled version of this tool (requires Azure AD setup). Contact your IT team.

## FAQ

**Q: Why not include cloud extraction?**
A: Simplicity. No Azure AD setup = faster deployment, no credential management.

**Q: Can I extract cloud data with this?**
A: No, this version is local-only. Use Microsoft 365 admin portal or the cloud-enabled version.

**Q: Do I need Python on the endpoint?**
A: No! The exe is completely standalone.

**Q: How big is the exe?**
A: ~30-50 MB. Small enough for USB or network deployment.

**Q: Does it work on Windows 7?**
A: Designed for Windows 10/11. May work on Windows 7 but untested.

**Q: Can I customize it?**
A: Yes! It's open source. Fork, modify, rebuild.

## Security & Compliance

### Data Protection
- Extracted data contains sensitive personal information
- Use encrypted storage and secure transport
- Follow data retention and deletion policies
- Ensure GDPR/privacy law compliance

### Recommended Practices
1. Store exe on restricted network share
2. Audit all extractions (Windows Event Log)
3. Use password-protected archives
4. Move data to secure storage immediately
5. Delete local copies after transfer

### Legal Use
This tool is designed for **authorized employee offboarding only**. Use only when:
- ✅ Proper authorization is obtained
- ✅ HR offboarding process is initiated
- ✅ Legal requirements are met
- ✅ Privacy laws are followed

## Documentation

- **[BUILD.md](BUILD.md)** - Build the standalone executable (5 minutes)
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deploy and manage the tool
- **[LICENSE](LICENSE)** - MIT License with usage terms

## Version History

### v2.0.0 (2024-01-16) - SIMPLIFIED
- ✨ **ZERO CONFIGURATION** - No Azure AD setup required
- ✨ Local data extraction only (OneDrive/SharePoint/Teams removed)
- ✨ One-command build process
- ✨ Smaller executable (~30-50 MB vs 50-100 MB)
- ✨ Simpler deployment
- ✨ No credential management

### v1.0.0 (2024-01-15)
- Initial release with cloud extraction
- Required Azure AD App Registration
- Configuration wizard for credentials

## Comparison: Local vs Cloud Version

| Feature | v2.0 (Local-Only) | v1.0 (Cloud) |
|---------|-------------------|--------------|
| **Setup** | ⭐ None | ⭐⭐⭐ Azure AD |
| **Build** | 1 command | 2 commands + config |
| **Credentials** | None | Azure AD required |
| **Local Data** | ✅ Yes | ✅ Yes |
| **Cloud Data** | ❌ No | ✅ Yes |
| **File Size** | 30-50 MB | 50-100 MB |
| **Best For** | Most organizations | Advanced cloud needs |

**Recommendation**: Use v2.0 (this version) unless you specifically need automated cloud extraction.

## Support

### Getting Help
1. Check [BUILD.md](BUILD.md) or [DEPLOYMENT.md](DEPLOYMENT.md)
2. Review extraction logs: `logs/extraction.log`
3. Test with a test account first
4. Open GitHub issue for bugs

### Contributing
Contributions welcome! Please:
- Fork the repository
- Create a feature branch
- Submit pull requests
- Follow existing code style

## License

MIT License with important usage restrictions. See [LICENSE](LICENSE) for details.

**Summary**:
- ✅ Use for legitimate IT administration
- ✅ Modify and customize for your needs
- ❌ Do not use without proper authorization
- ❌ Do not use for unauthorized access
- ❌ Authors not liable for misuse

---

**Disclaimer**: This tool is provided for legitimate IT administration purposes. Users are responsible for ensuring compliance with all applicable laws, regulations, and company policies.

**Made with ☕ for IT administrators who want simple tools that just work.**
