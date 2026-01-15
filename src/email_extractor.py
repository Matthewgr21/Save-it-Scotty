"""
Email archive extraction module.
Finds and extracts Outlook PST and OST files.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List
import winreg

logger = logging.getLogger(__name__)


class EmailArchiveExtractor:
    """Finds and extracts Outlook email archives (PST/OST files)."""

    def __init__(self, config: Dict, output_dir: Path):
        """
        Initialize the email archive extractor.

        Args:
            config: Configuration dictionary
            output_dir: Output directory for extracted data
        """
        self.config = config
        self.output_dir = output_dir
        self.stats = {
            'pst_files': 0,
            'ost_files': 0,
            'total_size': 0,
            'errors': []
        }

    def extract_all(self, username: str) -> Dict:
        """
        Find and extract all email archives.

        Args:
            username: Windows username

        Returns:
            Dictionary with extraction statistics
        """
        logger.info(f"Starting email archive extraction for user: {username}")

        user_profile = Path(f"C:\\Users\\{username}")
        if not user_profile.exists():
            raise FileNotFoundError(f"User profile not found: {user_profile}")

        # Create email extraction directory
        email_output = self.output_dir / "email_archives"
        email_output.mkdir(parents=True, exist_ok=True)

        # Find PST/OST files
        archive_files = self._find_email_archives(user_profile)

        # Copy archives
        for archive_file in archive_files:
            self._copy_archive(archive_file, email_output)

        logger.info(f"Email archive extraction completed. PST files: {self.stats['pst_files']}, "
                   f"OST files: {self.stats['ost_files']}, "
                   f"Total size: {self._format_size(self.stats['total_size'])}")

        return self.stats

    def _find_email_archives(self, user_profile: Path) -> List[Path]:
        """
        Find all PST and OST files in the user profile.

        Args:
            user_profile: User profile path

        Returns:
            List of found archive file paths
        """
        archives = []

        # Common Outlook data file locations
        search_paths = [
            user_profile / "Documents" / "Outlook Files",
            user_profile / "AppData" / "Local" / "Microsoft" / "Outlook",
            user_profile / "AppData" / "Roaming" / "Microsoft" / "Outlook",
        ]

        # Search for PST and OST files
        for search_path in search_paths:
            if search_path.exists():
                logger.debug(f"Searching for email archives in: {search_path}")
                archives.extend(search_path.glob("*.pst"))
                archives.extend(search_path.glob("*.ost"))

        # Also try to read Outlook registry settings (Windows only)
        try:
            registry_archives = self._get_archives_from_registry()
            archives.extend(registry_archives)
        except Exception as e:
            logger.warning(f"Could not read Outlook registry settings: {e}")

        # Remove duplicates
        unique_archives = list(set(archives))
        logger.info(f"Found {len(unique_archives)} email archive file(s)")

        return unique_archives

    def _get_archives_from_registry(self) -> List[Path]:
        """
        Get PST/OST file locations from Windows registry.

        Returns:
            List of archive file paths from registry
        """
        archives = []

        try:
            # Try different Outlook versions
            outlook_versions = ["16.0", "15.0", "14.0"]  # Office 2016+, 2013, 2010

            for version in outlook_versions:
                try:
                    # Open Outlook profiles registry key
                    key_path = f"Software\\Microsoft\\Office\\{version}\\Outlook\\Profiles"
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)

                    # Enumerate profiles
                    profile_index = 0
                    while True:
                        try:
                            profile_name = winreg.EnumKey(key, profile_index)
                            profile_key = winreg.OpenKey(key, profile_name)

                            # Look for data file paths in profile
                            self._enumerate_registry_archives(profile_key, archives)

                            winreg.CloseKey(profile_key)
                            profile_index += 1
                        except WindowsError:
                            break

                    winreg.CloseKey(key)
                except WindowsError:
                    continue

        except Exception as e:
            logger.debug(f"Registry search error: {e}")

        return archives

    def _enumerate_registry_archives(self, key, archives: List[Path]) -> None:
        """
        Recursively enumerate registry key for archive file paths.

        Args:
            key: Registry key handle
            archives: List to append found archive paths to
        """
        try:
            # Try to read common value names for data file paths
            value_names = ["001f6610", "001f6700"]  # Common Outlook registry values

            for value_name in value_names:
                try:
                    value, _ = winreg.QueryValueEx(key, value_name)
                    if isinstance(value, str) and (value.endswith('.pst') or value.endswith('.ost')):
                        archive_path = Path(value)
                        if archive_path.exists():
                            archives.append(archive_path)
                except WindowsError:
                    continue

        except Exception as e:
            logger.debug(f"Error enumerating registry key: {e}")

    def _copy_archive(self, archive_file: Path, destination: Path) -> None:
        """
        Copy an email archive file to the destination.

        Args:
            archive_file: Source archive file
            destination: Destination directory
        """
        try:
            file_size = archive_file.stat().st_size
            dest_path = destination / archive_file.name

            logger.info(f"Copying email archive: {archive_file.name} "
                       f"({self._format_size(file_size)})")

            shutil.copy2(archive_file, dest_path)

            # Update statistics
            if archive_file.suffix.lower() == '.pst':
                self.stats['pst_files'] += 1
            elif archive_file.suffix.lower() == '.ost':
                self.stats['ost_files'] += 1

            self.stats['total_size'] += file_size

        except PermissionError:
            error_msg = f"Permission denied: {archive_file}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
        except Exception as e:
            error_msg = f"Error copying {archive_file}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes into human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
