#!/usr/bin/env python3
"""
Build Configuration Tool
Creates embedded configuration for the standalone executable
"""

import sys
import getpass
from pathlib import Path


def get_azure_credentials():
    """Interactively get Azure AD credentials from IT admin"""
    print("\n" + "="*70)
    print("AZURE AD CONFIGURATION")
    print("="*70)
    print("\nYou need to provide Azure AD App Registration credentials.")
    print("These will be embedded into the executable.\n")
    print("If you haven't created an Azure AD App Registration yet, please")
    print("refer to the README.md for setup instructions.\n")

    tenant_id = input("Enter Azure AD Tenant ID: ").strip()
    client_id = input("Enter Azure AD Client (Application) ID: ").strip()
    client_secret = getpass.getpass("Enter Azure AD Client Secret (hidden): ").strip()

    if not all([tenant_id, client_id, client_secret]):
        print("\n✗ Error: All fields are required!")
        sys.exit(1)

    return tenant_id, client_id, client_secret


def get_optional_settings():
    """Get optional configuration settings"""
    print("\n" + "="*70)
    print("OPTIONAL SETTINGS")
    print("="*70)

    archive_password = input("\nEnter default archive password (or press Enter to skip): ").strip()

    return {
        'archive_password': archive_password
    }


def create_embedded_config(tenant_id, client_id, client_secret, optional_settings):
    """Create embedded_config.py file"""
    config_content = f'''"""
Embedded configuration for Save-it-Scotty
AUTO-GENERATED - DO NOT EDIT MANUALLY
"""

def get_config():
    """Return embedded configuration"""
    return {{
        'azure': {{
            'tenant_id': '{tenant_id}',
            'client_id': '{client_id}',
            'client_secret': '{client_secret}'
        }},
        'extraction': {{
            'output_dir': './extracted_data',
            'use_timestamps': True,
            'create_archive': True,
            'archive_password': '{optional_settings.get("archive_password", "")}',
            'max_file_size_mb': 0,
            'skip_extensions': ['.tmp', '.temp', '.cache']
        }},
        'local_extraction': {{
            'include_desktop': True,
            'include_documents': True,
            'include_downloads': True,
            'include_appdata': True,
            'include_email_archives': True,
            'include_browser_data': True,
            'browsers': ['chrome', 'edge', 'firefox']
        }},
        'cloud_extraction': {{
            'include_onedrive': True,
            'include_sharepoint': True,
            'include_teams_chats': True,
            'sharepoint_sites': []
        }},
        'logging': {{
            'level': 'INFO',
            'log_to_file': True,
            'log_file': './logs/extraction.log'
        }}
    }}
'''

    output_path = Path(__file__).parent / 'src' / 'embedded_config.py'
    with open(output_path, 'w') as f:
        f.write(config_content)

    print(f"\n✓ Configuration file created: {output_path}")
    return output_path


def main():
    """Main entry point"""
    print("\n╔═══════════════════════════════════════════════════════════════════╗")
    print("║       Save-it-Scotty - Build Configuration Tool              ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")

    print("\nThis tool will create an embedded configuration file with your")
    print("Azure AD credentials. The configuration will be compiled into the")
    print("executable, so you won't need a separate config file.")

    print("\n⚠ WARNING: The embedded credentials will be visible to anyone who")
    print("decompiles the executable. Only deploy to trusted IT staff.")

    response = input("\nContinue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Cancelled.")
        sys.exit(0)

    # Get credentials
    tenant_id, client_id, client_secret = get_azure_credentials()

    # Get optional settings
    optional_settings = get_optional_settings()

    # Create embedded config
    create_embedded_config(tenant_id, client_id, client_secret, optional_settings)

    print("\n" + "="*70)
    print("CONFIGURATION COMPLETE!")
    print("="*70)
    print("\nYou can now build the executable using:")
    print("  python build_exe.py")
    print("\nThe executable will include your Azure AD credentials.")
    print("\n⚠ Remember: Keep the executable secure and only distribute to")
    print("authorized IT administrators.")
    print()


if __name__ == '__main__':
    main()
