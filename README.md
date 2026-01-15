# Save-it-Scotty

**Standalone Employee Offboarding Data Extraction Tool for Windows**

A simple, standalone Windows application for IT administrators to extract and preserve employee data during offboarding procedures. No Python installation required on endpoints.

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

### 🖥️ Standalone Executable
- **Single EXE file** - No Python installation required
- **Embedded credentials** - Azure AD credentials baked into the executable
- **Simple GUI** - Easy-to-use graphical interface
- **Auto-detection** - Automatically detects current Windows user
- **~50-100 MB** - Portable and easy to distribute

### 📁 Local Data Extraction
- User folders (Desktop, Documents, Downloads)
- Application data (AppData: Roaming, Local, LocalLow)
- Email archives (Outlook PST and OST files)
- Browser data (Chrome, Edge, Firefox)
  - Bookmarks
  - History
  - Saved credentials

### ☁️ Cloud Data Extraction (Microsoft 365)
- **OneDrive**: All files and folders
- **SharePoint**: Documents from accessible sites
- **Teams**: Chat logs, messages, and attachments

### 📦 Data Management
- Password-protected ZIP archives
- Detailed extraction reports (JSON + Text)
- Progress tracking with real-time logs
- Error handling and recovery

## Quick Start for IT Admins

### Option 1: Use Pre-Built Executable (Easiest)

If your IT team has already built the executable:

1. Copy `SaveItScotty.exe` to the target machine
2. Right-click → **Run as Administrator**
3. Click "Auto-Detect Current User" or enter employee details
4. Select extraction options
5. Click "Start Extraction"
6. Wait for completion and review the report

### Option 2: Build Your Own Executable

To build the executable with your organization's Azure AD credentials:

```bash
# Clone repository
git clone https://github.com/yourusername/Save-it-Scotty.git
cd Save-it-Scotty

# Install dependencies
pip install -r requirements.txt

# Configure your Azure AD credentials
python build_config.py

# Build the standalone executable
python build_exe.py

# Your executable is ready
dist\SaveItScotty.exe
```

📖 **Detailed instructions**: See [BUILD.md](BUILD.md)

## Screenshots

### Main Interface
```
┌─────────────────────────────────────────────────────────┐
│              Save-it-Scotty                            │
│     Employee Offboarding Data Extraction Tool          │
├─────────────────────────────────────────────────────────┤
│ Employee Information                                    │
│   Windows Username: [jdoe          ]  [Auto-Detect]    │
│   Email Address:    [jdoe@company.com]                 │
├─────────────────────────────────────────────────────────┤
│ Output Location                                         │
│   [C:\Users\Admin\Desktop\Extracted_Data] [Browse...]  │
├─────────────────────────────────────────────────────────┤
│ Extraction Options                                      │
│   Local Device:                                         │
│     ☑ User Folders (Desktop, Documents, Downloads...)   │
│     ☑ Email Archives (PST/OST files)                    │
│     ☑ Browser Data (Chrome, Edge, Firefox)              │
│                                                         │
│   Microsoft 365:                                        │
│     ☑ OneDrive Files                                    │
│     ☑ SharePoint Documents                              │
│     ☑ Teams Chat Logs                                   │
│                                                         │
│     ☑ Create password-protected ZIP archive             │
├─────────────────────────────────────────────────────────┤
│ Progress                                                │
│   [████████████████████████████░░░░░░░░░░░]  75%       │
│                                                         │
│   [13:42:15] Starting extraction process...            │
│   [13:42:16] Target user: jdoe (jdoe@company.com)      │
│   [13:42:20] ✓ Local files: 1,247 files copied         │
│   [13:43:15] ✓ Email archives: 2 PST, 1 OST found      │
│   [13:44:30] Extracting OneDrive files...              │
├─────────────────────────────────────────────────────────┤
│ [Start Extraction] [Cancel] [Clear Log]       [Exit]   │
└─────────────────────────────────────────────────────────┘
```

## Requirements

### For Building the Executable
- Windows 10/11
- Python 3.8+
- Azure AD App Registration (see [Azure AD Setup](#azure-ad-setup))

### For Running the Executable
- Windows 10/11 (x64)
- Administrator privileges (recommended)
- Network connectivity (for cloud extraction)
- **No Python installation required**

## Azure AD Setup

To extract cloud data, you need an Azure AD App Registration:

### Quick Setup

1. **Create App Registration**
   - Go to [Azure Portal](https://portal.azure.com) → Azure AD → App registrations
   - Click "New registration"
   - Name: "Save-it-Scotty Data Extraction"
   - Click Register

2. **Configure Permissions**

   Add these **Application permissions** (not Delegated):
   - `User.Read.All` - Read all users' profiles
   - `Files.Read.All` - Read files in all site collections
   - `Sites.Read.All` - Read items in all site collections
   - `Chat.Read.All` - Read all chat messages
   - `Mail.Read` - Read mail in all mailboxes

   Click **Grant admin consent** (requires Global Administrator)

3. **Create Client Secret**
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Copy the secret value immediately

4. **Note Your Credentials**
   - Tenant ID (from Overview page)
   - Client ID (from Overview page)
   - Client Secret (the value you just copied)

These credentials will be embedded into the executable during build.

## Building the Executable

### Step-by-Step Build Process

```bash
# 1. Setup
git clone https://github.com/yourusername/Save-it-Scotty.git
cd Save-it-Scotty
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure Azure Credentials (interactive wizard)
python build_config.py
# Enter your Tenant ID, Client ID, and Client Secret when prompted

# 3. Build Executable
python build_exe.py
# Wait 2-5 minutes for build to complete

# 4. Test
dist\SaveItScotty.exe
```

**Output**: `dist/SaveItScotty.exe` (50-100 MB)

📖 **Full build guide**: [BUILD.md](BUILD.md)

## Deployment

### Deployment Options

**Manual Deployment** (Simplest)
- Copy exe to USB drive or network share
- Run on target machine

**Network Share**
```
\\fileserver\IT-Tools\SaveItScotty.exe
```

**Group Policy**
- Deploy via Software Installation GPO
- Assign to IT Administrators OU

**SCCM/Intune**
- Package as application
- Deploy to IT admin devices

📖 **Full deployment guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

### Security Recommendations

- ✅ Only distribute to authorized IT administrators
- ✅ Store on restricted network shares
- ✅ Monitor Azure AD sign-in logs
- ✅ Rotate client secrets every 6-12 months
- ✅ Use password-protected archives for data transport

## Usage

### GUI Mode (Recommended)

1. **Launch**: Double-click `SaveItScotty.exe` (Run as Administrator)

2. **Configure**:
   - Enter employee username and email
   - Or click "Auto-Detect Current User"
   - Select output directory
   - Choose extraction options

3. **Extract**:
   - Click "Start Extraction"
   - Monitor progress in real-time
   - Wait for completion message

4. **Review**:
   - Check extraction report
   - Verify all data was captured
   - Move data to secure storage

### CLI Mode (Advanced)

The tool also supports command-line operation:

```bash
# Run with Python
python save_it_scotty.py --username jdoe --email jdoe@company.com

# Options
--config config.yaml         # Use specific config file
--output-dir C:\Extractions  # Custom output directory
--skip-local                 # Skip local data extraction
--skip-cloud                 # Skip cloud data extraction
--no-archive                 # Don't create ZIP archive
```

## Output Structure

```
Extracted_Data/
└── jdoe_20240115_143022/
    ├── local_data/
    │   ├── Desktop/
    │   ├── Documents/
    │   ├── Downloads/
    │   └── AppData/
    ├── email_archives/
    │   ├── archive1.pst
    │   └── archive2.ost
    ├── browser_data/
    │   ├── chrome/
    │   ├── edge/
    │   └── firefox/
    ├── onedrive/
    │   └── [OneDrive files]
    ├── sharepoint/
    │   └── [SharePoint sites]
    ├── teams_chats/
    │   ├── 0001_Project_Team/
    │   │   ├── chat_export.json
    │   │   ├── transcript.txt
    │   │   └── attachments/
    │   └── 0002_Direct_Chat/
    ├── extraction_report.txt
    └── extraction_report.json

Optional: jdoe_20240115_143022.zip (password-protected archive)
```

## Troubleshooting

### Common Issues

**"Permission Denied" when accessing files**
- Run as Administrator
- Ensure target user is logged out
- Check NTFS permissions

**"Could not authenticate" with Microsoft Graph**
- Verify Azure AD credentials are correct
- Check admin consent was granted
- Ensure client secret hasn't expired

**Antivirus blocks the executable**
- Windows Defender may flag PyInstaller executables
- Add exception for SaveItScotty.exe
- Consider code signing for production use

**Extraction is very slow**
- Large OneDrive/SharePoint can take hours
- Check network speed
- Consider extracting local and cloud separately

📖 **Full troubleshooting guide**: [DEPLOYMENT.md#troubleshooting](DEPLOYMENT.md#troubleshooting)

## Advanced Features

### Customization

Edit `src/embedded_config.py` (after running `build_config.py`) to customize:
- Default output directory
- Skip file extensions
- Max file size limits
- Archive passwords
- SharePoint site filters

### Automation

For automated/scripted deployments:

```powershell
# PowerShell example
$username = "jdoe"
$email = "jdoe@company.com"

# Run extraction silently (requires CLI mode)
& SaveItScotty.exe --username $username --email $email --output-dir "\\server\Offboarding\$username"
```

## Architecture

```
SaveItScotty.exe (Standalone Executable)
├── GUI Layer (tkinter)
│   ├── User input collection
│   ├── Progress tracking
│   └── Log display
├── Extraction Modules
│   ├── LocalDataExtractor
│   ├── EmailArchiveExtractor
│   ├── BrowserDataExtractor
│   ├── OneDriveExtractor
│   ├── SharePointExtractor
│   └── TeamsExtractor
├── Authentication
│   └── GraphAuthenticator (MSAL)
├── Data Management
│   └── DataArchiver (ZIP + Reports)
└── Embedded Configuration
    └── Azure AD credentials (encrypted in exe)
```

## Security & Compliance

### Data Protection
- Extracted data contains sensitive personal information
- Use encrypted storage and secure transport
- Follow data retention policies
- Ensure GDPR/privacy law compliance

### Access Control
- Limit tool distribution to authorized personnel
- Audit all extractions
- Implement 4-eyes principle for sensitive cases
- Monitor Azure AD sign-in logs

### Legal Use
This tool is designed for **authorized employee offboarding only**. Use only when:
- ✅ Proper authorization is obtained
- ✅ HR offboarding process is initiated
- ✅ Legal requirements are met
- ✅ Privacy laws are followed

## Documentation

- **[BUILD.md](BUILD.md)** - Build the standalone executable
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deploy and manage the tool
- **[LICENSE](LICENSE)** - MIT License with usage terms

## Version History

### v1.0.0 (2024-01-15)
- ✨ Initial standalone executable release
- ✨ GUI interface with auto-detection
- ✨ Embedded Azure AD credentials
- ✨ Local data extraction (files, email, browsers)
- ✨ Cloud extraction (OneDrive, SharePoint, Teams)
- ✨ Password-protected ZIP archives
- ✨ Comprehensive reporting

## Support

### Getting Help

1. Check [DEPLOYMENT.md#troubleshooting](DEPLOYMENT.md#troubleshooting)
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
