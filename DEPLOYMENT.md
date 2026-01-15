# Save-it-Scotty Deployment Guide for IT Administrators

This guide provides step-by-step instructions for building and deploying the Save-it-Scotty employee data extraction tool as a standalone Windows executable.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Building the Executable](#building-the-executable)
- [Deployment Methods](#deployment-methods)
- [Using the Tool](#using-the-tool)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)

## Overview

Save-it-Scotty is packaged as a standalone Windows executable (SaveItScotty.exe) that:
- Requires no Python installation on target machines
- Contains all dependencies bundled inside
- Has Azure AD credentials embedded during build
- Provides a simple graphical interface for IT administrators

**File Size**: Approximately 50-100 MB
**Target OS**: Windows 10/11 (x64)
**Requires**: Administrator privileges for best results

## Prerequisites

### For Building (One-Time Setup)

You need a Windows machine with Python to build the executable. Once built, the executable can be deployed to any Windows machine.

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```

2. **Git** (to clone the repository)
   ```bash
   git --version
   ```

3. **Azure AD App Registration**
   - Tenant ID
   - Client ID (Application ID)
   - Client Secret
   - Required Graph API Permissions (with admin consent):
     - `User.Read.All`
     - `Files.Read.All`
     - `Sites.Read.All`
     - `Chat.Read.All`
     - `Mail.Read`

### Azure AD App Registration Setup

If you haven't created the Azure AD App Registration yet:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations** → **New registration**
3. Name: "Save-it-Scotty Data Extraction Tool"
4. Supported account types: "Accounts in this organizational directory only"
5. Click **Register**
6. Note the **Tenant ID** and **Client ID** (Application ID)
7. Go to **API permissions**:
   - Click **Add a permission** → **Microsoft Graph** → **Application permissions**
   - Add: `User.Read.All`, `Files.Read.All`, `Sites.Read.All`, `Chat.Read.All`, `Mail.Read`
   - Click **Grant admin consent** (requires Global Administrator)
8. Go to **Certificates & secrets**:
   - Click **New client secret**
   - Description: "Build 2024-01"
   - Expiration: Choose appropriate period
   - Click **Add** and **copy the secret value immediately**

## Building the Executable

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Save-it-Scotty.git
cd Save-it-Scotty
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Azure Credentials

Run the configuration tool to embed your Azure AD credentials:

```bash
python build_config.py
```

You'll be prompted for:
- Azure AD Tenant ID
- Azure AD Client ID
- Azure AD Client Secret
- (Optional) Default archive password

This creates `src/embedded_config.py` with your credentials.

**⚠ WARNING**: The `embedded_config.py` file contains your secrets. Do not commit it to version control!

### Step 4: Build the Executable

```bash
python build_exe.py
```

This will:
1. Check all requirements
2. Clean previous builds
3. Create PyInstaller spec file
4. Build the executable (takes 2-5 minutes)
5. Create `dist/SaveItScotty.exe`

### Step 5: Test the Executable

Before deployment, test the executable:

```bash
cd dist
SaveItScotty.exe
```

Verify:
- GUI launches without errors
- Auto-detect finds current user
- Test extraction on a test account (if possible)

## Deployment Methods

### Method 1: Manual Deployment (Simplest)

**Best for**: Small organizations, ad-hoc usage

1. Copy `SaveItScotty.exe` to a USB drive or network share
2. Navigate to the employee's workstation
3. Copy the executable to the Desktop or a temporary folder
4. Right-click → **Run as Administrator**
5. Follow the GUI instructions
6. After extraction completes, copy the output to secure storage
7. Delete the executable and extracted data from the workstation

### Method 2: Network Share Deployment

**Best for**: Multiple extractions, IT team access

1. Create a shared folder (e.g., `\\fileserver\IT-Tools\OffboardingTool`)
2. Set NTFS permissions: IT Admins = Full Control, Domain Users = No Access
3. Copy `SaveItScotty.exe` to the share
4. Create a shortcut on IT admin workstations
5. IT admins run directly from the network share

### Method 3: Group Policy Deployment

**Best for**: Pre-deployment to IT admin workstations

1. Create a Group Policy Object (GPO)
2. Computer Configuration → Policies → Software Settings → Software Installation
3. Right-click → New → Package
4. Browse to `SaveItScotty.exe` on a DFS or stable network share
5. Select "Assigned" deployment
6. Link GPO to IT Administrators OU
7. Tool will install on next reboot/gpupdate

### Method 4: SCCM/Intune Deployment

**Best for**: Enterprise environments with existing deployment tools

**SCCM**:
1. Create Application in SCCM Console
2. Add Deployment Type: Script Installer
3. Content Location: Folder containing SaveItScotty.exe
4. Installation Program: `copy SaveItScotty.exe "%ProgramData%\CompanyName\Tools\"`
5. Detection Method: File exists at installation path
6. Deploy to IT Admins device collection

**Intune**:
1. Apps → Windows → Add → Line-of-business app
2. Upload SaveItScotty.exe
3. Configure app information
4. Assign to IT Administrators group
5. Publish

## Using the Tool

### Launching the Tool

1. **Run as Administrator** (right-click → Run as Administrator)
   - Required for accessing all user profile folders
   - Required for reading email archives and browser data

2. The GUI will launch with a simple interface

### Step-by-Step Usage

1. **Employee Information**:
   - Click "Auto-Detect Current User" if running on employee's machine
   - OR manually enter Windows username and email address

2. **Output Location**:
   - Default: Desktop\Extracted_Data
   - Click "Browse..." to change location
   - Consider using a network share for large extractions

3. **Extraction Options**:
   - **Local Device**: User folders, email archives, browser data
   - **Microsoft 365**: OneDrive, SharePoint, Teams
   - Check/uncheck options as needed
   - Enable "Create password-protected ZIP archive" for transport

4. **Start Extraction**:
   - Click "Start Extraction"
   - Confirm the details
   - Monitor progress in the log window
   - Wait for completion (may take 10 minutes to several hours)

5. **Review Results**:
   - Check the extraction report in the output folder
   - Verify all required data was extracted
   - Note any errors or missing data

6. **Secure the Data**:
   - Move extracted data to secure storage
   - Delete from local machine
   - Follow data retention policies

### Output Structure

```
Desktop\Extracted_Data\
└── username_20240115_143022\
    ├── local_data\
    ├── email_archives\
    ├── browser_data\
    ├── onedrive\
    ├── sharepoint\
    ├── teams_chats\
    ├── extraction_report.txt
    └── extraction_report.json
```

Plus optional: `username_20240115_143022.zip`

## Troubleshooting

### "Permission Denied" Errors

**Problem**: Cannot access user folders

**Solutions**:
- Run as Administrator
- Ensure you're logged in with domain admin account
- Check NTFS permissions on user profile folder
- Ensure user is logged out (browsers may lock database files)

### "Could Not Authenticate with Microsoft Graph"

**Problem**: Cloud extraction fails

**Solutions**:
- Verify Azure AD credentials are correct
- Check that admin consent was granted for all API permissions
- Verify the client secret hasn't expired
- Check network connectivity to login.microsoftonline.com
- Review firewall/proxy settings

### "No Data Found" for OneDrive/SharePoint

**Problem**: Cloud extraction completes but no files extracted

**Solutions**:
- Verify the email address is correct
- Ensure the user account hasn't been deleted from Azure AD
- Check that the user actually has OneDrive/SharePoint data
- Verify API permissions include Files.Read.All and Sites.Read.All

### Executable Won't Launch

**Problem**: Double-clicking does nothing or shows error

**Solutions**:
- Check Windows antivirus/SmartScreen hasn't blocked it
- Run from command prompt to see error messages: `SaveItScotty.exe`
- Verify Windows version is 10 or 11 (x64)
- Check Windows Event Viewer for application errors

### Extraction is Very Slow

**Problem**: Extraction takes extremely long

**Solutions**:
- Check network speed for cloud extractions
- Large OneDrive/SharePoint sites may take hours
- Consider splitting into multiple extractions (local vs cloud)
- Use `--skip-cloud` or `--skip-local` flags if using CLI mode
- Check disk I/O performance on output location

## Security Considerations

### Embedded Credentials

**Risk**: Azure AD credentials are embedded in the executable

**Mitigations**:
- Only distribute to authorized IT administrators
- Use network access controls to limit who can access the tool
- Monitor Azure AD sign-in logs for the app registration
- Rotate client secrets regularly
- Create separate app registrations for different teams/purposes

### Data Handling

**Requirements**:
- Treat extracted data as highly sensitive
- Use encrypted storage for extraction archives
- Follow data retention and deletion policies
- Document all extractions for compliance
- Ensure GDPR/privacy law compliance

### Access Controls

**Recommendations**:
- Store executable on restricted network share
- Use NTFS permissions to limit access
- Audit who runs the tool (Windows Event Logging)
- Implement 4-eyes principle for sensitive extractions
- Log all extraction activities

### Network Security

**Considerations**:
- Tool makes HTTPS connections to:
  - login.microsoftonline.com (authentication)
  - graph.microsoft.com (data extraction)
- Ensure firewall allows these connections
- Consider proxy configuration if required
- Monitor for unusual API usage patterns

## Best Practices

1. **Pre-Extraction Planning**
   - Verify employee offboarding is authorized
   - Determine what data needs to be preserved
   - Identify data retention requirements
   - Plan for large datasets (>100 GB)

2. **During Extraction**
   - Run on employee's workstation when possible (faster for local data)
   - Ensure stable network connection for cloud data
   - Monitor progress and address errors promptly
   - Document any issues or missing data

3. **Post-Extraction**
   - Review extraction report thoroughly
   - Verify critical data was captured
   - Move data to secure long-term storage
   - Remove extracted data from workstation
   - Update offboarding checklist

4. **Tool Management**
   - Keep Azure AD client secrets secure
   - Rotate secrets every 6-12 months
   - Rebuild executable with new credentials
   - Test new builds before deployment
   - Maintain documentation of builds and deployments

## Support and Updates

### Updating the Tool

To rebuild with updated credentials or new features:

1. Pull latest code from repository
2. Re-run `python build_config.py` with new credentials
3. Re-run `python build_exe.py`
4. Test the new executable
5. Redeploy to IT team

### Logging

Logs are saved to: `./logs/extraction.log` (relative to executable location)

Review logs for:
- Errors during extraction
- API authentication issues
- File access problems
- Performance metrics

### Getting Help

- Check log files for detailed error messages
- Review this documentation
- Contact your Azure AD administrator for permission issues
- Open issue on GitHub repository for bugs

## Compliance and Legal

**Important**: Use this tool only for authorized employee offboarding. Ensure compliance with:
- Company IT policies
- Employment laws
- Data protection regulations (GDPR, CCPA, etc.)
- Industry-specific requirements (HIPAA, SOX, etc.)

Maintain audit logs of:
- Who ran the tool
- Which employee's data was extracted
- When extractions occurred
- Where data is stored
- When data will be deleted

---

## Quick Reference

### Build Commands
```bash
python build_config.py    # Configure Azure credentials
python build_exe.py       # Build executable
```

### Deployment Locations
- Manual: Copy to USB or workstation
- Network: `\\fileserver\IT-Tools\SaveItScotty.exe`
- Local Install: `C:\Program Files\CompanyName\Tools\`

### Running as Administrator
```cmd
# From command line
runas /user:DOMAIN\admin SaveItScotty.exe

# Or right-click → Run as Administrator
```

### Output Locations
- Default: `%USERPROFILE%\Desktop\Extracted_Data`
- Recommended: `\\fileserver\Offboarding\%USERNAME%`

---

**Version**: 1.0.0
**Last Updated**: 2024-01-15
**Questions?**: Contact IT Security Team
