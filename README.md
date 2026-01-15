# Save-it-Scotty

**Employee Offboarding Data Extraction Tool**

A comprehensive Python-based tool for IT administrators to extract and preserve employee data during offboarding procedures. This tool automates the collection of data from local devices and Microsoft 365 cloud services before account termination.

## Features

### Local Data Extraction
- **User Folders**: Desktop, Documents, Downloads
- **Application Data**: AppData (Roaming, Local, LocalLow)
- **Email Archives**: Outlook PST and OST files
- **Browser Data**: Bookmarks, history, and saved credentials from Chrome, Edge, and Firefox

### Cloud Data Extraction (Microsoft 365)
- **OneDrive**: All files and folders from user's OneDrive
- **SharePoint**: Documents from SharePoint sites the user has access to
- **Teams**: Chat logs, messages, and attachments

### Data Management
- **Automated Archiving**: Creates password-protected ZIP archives
- **Detailed Reporting**: JSON and text reports with extraction statistics
- **Flexible Configuration**: YAML-based configuration for all extraction options
- **Progress Logging**: Real-time progress updates and comprehensive logging

## Requirements

- Python 3.8+
- Windows OS (for local data extraction)
- Azure AD App Registration with appropriate permissions
- Administrator access to the target device

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Save-it-Scotty.git
   cd Save-it-Scotty
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Azure AD Configuration

To extract cloud data (OneDrive, SharePoint, Teams), you need to set up an Azure AD App Registration:

### Step 1: Create App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations** → **New registration**
3. Name: "Employee Offboarding Tool"
4. Supported account types: "Accounts in this organizational directory only"
5. Click **Register**

### Step 2: Configure API Permissions

Add the following **Microsoft Graph** permissions (Application permissions, not Delegated):

- `User.Read.All` - Read all users' full profiles
- `Files.Read.All` - Read all files in all site collections
- `Sites.Read.All` - Read items in all site collections
- `Chat.Read.All` - Read all chat messages
- `Mail.Read` - Read mail in all mailboxes

After adding permissions, click **Grant admin consent** for your organization.

### Step 3: Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Add description: "Offboarding Tool Secret"
4. Choose expiration period
5. Click **Add**
6. **Copy the secret value immediately** (you won't see it again)

### Step 4: Get Required IDs

- **Tenant ID**: Found on the App Registration overview page
- **Client ID**: Found on the App Registration overview page (also called Application ID)
- **Client Secret**: The value you copied in Step 3

## Configuration

1. **Copy the example configuration**
   ```bash
   copy config.yaml.example config.yaml
   ```

2. **Edit config.yaml** with your settings:

   ```yaml
   azure:
     tenant_id: "your-tenant-id-here"
     client_id: "your-client-id-here"
     client_secret: "your-client-secret-here"

   extraction:
     output_dir: "./extracted_data"
     use_timestamps: true
     create_archive: true
     archive_password: ""  # Optional: set a password for ZIP archives

   local_extraction:
     include_desktop: true
     include_documents: true
     include_downloads: true
     include_appdata: true
     include_email_archives: true
     include_browser_data: true

   cloud_extraction:
     include_onedrive: true
     include_sharepoint: true
     include_teams_chats: true
   ```

## Usage

### Basic Usage

```bash
python save_it_scotty.py --username WINDOWS_USERNAME --email user@company.com
```

### Advanced Options

```bash
# Custom configuration file
python save_it_scotty.py --username jdoe --email jdoe@company.com --config custom_config.yaml

# Custom output directory
python save_it_scotty.py --username jdoe --email jdoe@company.com --output-dir "C:\Offboarding\JDoe"

# Skip local extraction (cloud only)
python save_it_scotty.py --username jdoe --email jdoe@company.com --skip-local

# Skip cloud extraction (local only)
python save_it_scotty.py --username jdoe --email jdoe@company.com --skip-cloud

# Don't create archive (keep extracted files only)
python save_it_scotty.py --username jdoe --email jdoe@company.com --no-archive
```

### Command Line Options

- `--username` (required): Windows username of the employee
- `--email` (required): Email address of the employee
- `--config`: Path to configuration file (default: config.yaml)
- `--output-dir`: Override output directory from config
- `--skip-local`: Skip local file system extraction
- `--skip-cloud`: Skip cloud data extraction
- `--no-archive`: Don't create ZIP archive

## Output Structure

```
extracted_data/
└── username_20240115_143022/
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
    │   └── [SharePoint sites and files]
    ├── teams_chats/
    │   └── [Chat exports]
    ├── extraction_report.txt
    └── extraction_report.json
```

## Security Considerations

1. **Credentials**: Never commit `config.yaml` with real credentials to version control
2. **Archive Passwords**: Use strong passwords for ZIP archives containing sensitive data
3. **Access Control**: Restrict access to extracted data and archives
4. **Azure Permissions**: Use least-privilege principle; only grant necessary permissions
5. **Audit Logging**: Review logs after each extraction for errors or issues
6. **Data Retention**: Follow your organization's data retention policies
7. **Secure Storage**: Store extracted archives in encrypted, access-controlled locations

## Troubleshooting

### Authentication Issues

**Error**: "Authentication failed"
- Verify your tenant_id, client_id, and client_secret in config.yaml
- Ensure admin consent has been granted for all API permissions
- Check that the client secret hasn't expired

### Permission Denied Errors

**Error**: "Permission denied accessing files"
- Run the tool with Administrator privileges
- Ensure the target user is logged out (browser databases may be locked)
- Check that you have access to the user profile directory

### OneDrive/SharePoint Not Found

**Error**: "Could not access OneDrive/SharePoint"
- Verify the user email is correct
- Ensure the user account still exists in Azure AD
- Check that the user has OneDrive/SharePoint access

### Browser Data Locked

**Error**: "Could not copy browser database"
- Close all browser instances for the target user
- The tool will attempt to copy locked databases using SQLite backup

## Best Practices

1. **Run Before Account Deletion**: Execute the tool before disabling the user account in Azure AD
2. **Administrator Rights**: Always run with administrative privileges on the device
3. **Network Connection**: Ensure stable internet connection for cloud data extraction
4. **Storage Space**: Verify sufficient disk space for extracted data
5. **Test First**: Test the tool with a test account before using in production
6. **Document Procedures**: Keep records of what was extracted and when
7. **Review Reports**: Always review the extraction report for completeness

## Logging

Logs are saved to `./logs/extraction.log` by default. Log level can be configured in `config.yaml`:

- `DEBUG`: Detailed debugging information
- `INFO`: General progress information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only

## Limitations

- **Local extraction** requires the tool to run on the target device or have network access to the user profile
- **Teams chat history** may have retention policy limitations
- **SharePoint extraction** is limited to sites the user has access to
- **Large datasets** may take considerable time to extract
- **Deleted cloud data** cannot be recovered if already removed

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.

## License

This tool is provided as-is for legitimate IT administration purposes. Ensure you have proper authorization and comply with all applicable laws and regulations before using this tool.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial release
- Local data extraction (Desktop, Documents, Downloads, AppData)
- Email archive extraction (PST/OST)
- Browser data extraction (Chrome, Edge, Firefox)
- Cloud data extraction (OneDrive, SharePoint, Teams)
- Automated archiving and reporting
- YAML-based configuration
- Rich CLI interface with progress indicators
