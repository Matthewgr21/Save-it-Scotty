#!/usr/bin/env python3
"""
Build script for creating standalone executable
No configuration required - Local data extraction only
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_requirements():
    """Check if all requirements are met"""
    print("Checking build requirements...")

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("  ✓ PyInstaller is installed")
    except ImportError:
        print("  ✗ PyInstaller is not installed")
        print("\nPlease install PyInstaller:")
        print("  pip install pyinstaller")
        return False

    print("  ✓ All requirements met\n")
    return True


def clean_build_directories():
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")

    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  ✓ Removed {dir_name}/")

    # Clean .spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"  ✓ Removed {spec_file}")

    print()


def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'src.local_extractor',
        'src.email_extractor',
        'src.browser_extractor',
        'src.archiver',
        'requests',
        'pyzipper',
        'yaml',
        'sqlite3',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['msal', 'msgraph', 'azure'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SaveItScotty',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file here if you have one
)
'''

    spec_path = Path('SaveItScotty.spec')
    with open(spec_path, 'w') as f:
        f.write(spec_content)

    print(f"✓ Created PyInstaller spec file: {spec_path}\n")
    return spec_path


def build_executable(spec_file):
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    print("This may take several minutes...\n")

    try:
        # Run PyInstaller
        result = subprocess.run(
            ['pyinstaller', '--clean', str(spec_file)],
            check=True,
            capture_output=True,
            text=True
        )

        print("Build completed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error:\n{e.stderr}")
        return False
    except FileNotFoundError:
        print("\n✗ PyInstaller not found. Please install it:")
        print("  pip install pyinstaller")
        return False


def show_completion_message():
    """Show completion message with instructions"""
    exe_path = Path('dist/SaveItScotty.exe')

    print("\n" + "="*70)
    print("BUILD COMPLETED SUCCESSFULLY!")
    print("="*70)

    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\nExecutable created: {exe_path}")
        print(f"File size: {size_mb:.1f} MB")
    else:
        print(f"\n⚠ Warning: Expected executable not found at {exe_path}")

    print("\n" + "-"*70)
    print("DEPLOYMENT INSTRUCTIONS")
    print("-"*70)
    print("""
1. The executable is completely standalone and requires no Python
   installation on the target machine.

2. NO CONFIGURATION NEEDED - This version extracts local data only.

3. To deploy:
   - Copy SaveItScotty.exe to the target machine
   - Run as Administrator for best results
   - The tool will create extracted data on the Desktop by default

4. Distribution options:
   - Manual: Copy to USB drive or network share
   - Group Policy: Deploy via GPO software deployment
   - SCCM/Intune: Package and deploy through your management tool

5. Usage:
   - Double-click SaveItScotty.exe to launch the GUI
   - Click "Auto-Detect Current User" or enter manually
   - Select extraction options
   - Click "Start Extraction"

6. What it extracts (LOCAL DATA ONLY):
   - User folders (Desktop, Documents, Downloads, AppData)
   - Email archives (PST/OST files)
   - Browser data (Chrome, Edge, Firefox)

7. Cloud data (OneDrive, SharePoint, Teams):
   - Not included in this version
   - Extract separately through Microsoft 365 admin portal
   - Or use the cloud-enabled version (requires Azure AD setup)
""")

    print("="*70)
    print()


def main():
    """Main entry point"""
    print("\n╔═══════════════════════════════════════════════════════════════════╗")
    print("║         Save-it-Scotty - Executable Build Tool               ║")
    print("║              LOCAL DATA EXTRACTION ONLY                      ║")
    print("╚═══════════════════════════════════════════════════════════════════╝\n")

    print("This will create a standalone Windows executable for LOCAL data")
    print("extraction only (no cloud/Microsoft 365 data).")
    print("\nThe executable will be approximately 30-50 MB.")

    response = input("\nProceed with build? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Build cancelled.")
        sys.exit(0)

    print()

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Clean previous builds
    clean_build_directories()

    # Create spec file
    spec_file = create_spec_file()

    # Build executable
    if build_executable(spec_file):
        show_completion_message()
    else:
        print("\n✗ Build failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
