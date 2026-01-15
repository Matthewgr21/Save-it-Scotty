"""
Local file system data extraction module.
Handles extraction of user data from local device folders.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class LocalDataExtractor:
    """Extracts data from local user folders on Windows."""

    def __init__(self, config: Dict, output_dir: Path):
        """
        Initialize the local data extractor.

        Args:
            config: Configuration dictionary
            output_dir: Output directory for extracted data
        """
        self.config = config
        self.output_dir = output_dir
        self.local_config = config.get('local_extraction', {})
        self.skip_extensions = set(config.get('extraction', {}).get('skip_extensions', []))
        self.max_file_size = config.get('extraction', {}).get('max_file_size_mb', 0) * 1024 * 1024
        self.stats = {
            'files_copied': 0,
            'files_skipped': 0,
            'total_size': 0,
            'errors': []
        }

    def extract_all(self, username: str) -> Dict:
        """
        Extract all configured local data sources.

        Args:
            username: Windows username to extract data from

        Returns:
            Dictionary with extraction statistics
        """
        logger.info(f"Starting local data extraction for user: {username}")

        user_profile = Path(f"C:\\Users\\{username}")
        if not user_profile.exists():
            raise FileNotFoundError(f"User profile not found: {user_profile}")

        # Create local extraction directory
        local_output = self.output_dir / "local_data"
        local_output.mkdir(parents=True, exist_ok=True)

        # Extract standard user folders
        if self.local_config.get('include_desktop', True):
            self._extract_folder(user_profile / "Desktop", local_output / "Desktop")

        if self.local_config.get('include_documents', True):
            self._extract_folder(user_profile / "Documents", local_output / "Documents")

        if self.local_config.get('include_downloads', True):
            self._extract_folder(user_profile / "Downloads", local_output / "Downloads")

        # Extract AppData folders
        if self.local_config.get('include_appdata', True):
            self._extract_appdata(user_profile, local_output)

        logger.info(f"Local data extraction completed. Files copied: {self.stats['files_copied']}, "
                   f"Files skipped: {self.stats['files_skipped']}, "
                   f"Total size: {self._format_size(self.stats['total_size'])}")

        return self.stats

    def _extract_folder(self, source: Path, destination: Path) -> None:
        """
        Recursively extract a folder and its contents.

        Args:
            source: Source folder path
            destination: Destination folder path
        """
        if not source.exists():
            logger.warning(f"Source folder does not exist: {source}")
            return

        logger.info(f"Extracting folder: {source}")
        destination.mkdir(parents=True, exist_ok=True)

        try:
            for item in source.rglob('*'):
                if item.is_file():
                    self._copy_file(item, source, destination)
        except PermissionError as e:
            error_msg = f"Permission denied accessing {source}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
        except Exception as e:
            error_msg = f"Error extracting folder {source}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)

    def _extract_appdata(self, user_profile: Path, output_dir: Path) -> None:
        """
        Extract AppData folders (Roaming, Local, LocalLow).

        Args:
            user_profile: User profile path
            output_dir: Output directory
        """
        logger.info("Extracting AppData folders")

        appdata_output = output_dir / "AppData"
        appdata_output.mkdir(parents=True, exist_ok=True)

        appdata_folders = [
            ("AppData\\Roaming", "Roaming"),
            ("AppData\\Local", "Local"),
            ("AppData\\LocalLow", "LocalLow")
        ]

        for folder_name, output_name in appdata_folders:
            source = user_profile / folder_name
            if source.exists():
                self._extract_folder(source, appdata_output / output_name)

    def _copy_file(self, file_path: Path, source_root: Path, dest_root: Path) -> None:
        """
        Copy a single file with filtering and error handling.

        Args:
            file_path: File to copy
            source_root: Root of source directory
            dest_root: Root of destination directory
        """
        # Check file extension
        if file_path.suffix.lower() in self.skip_extensions:
            self.stats['files_skipped'] += 1
            return

        # Check file size
        try:
            file_size = file_path.stat().st_size
            if self.max_file_size > 0 and file_size > self.max_file_size:
                logger.debug(f"Skipping large file: {file_path} ({self._format_size(file_size)})")
                self.stats['files_skipped'] += 1
                return
        except Exception as e:
            logger.warning(f"Could not get size for {file_path}: {e}")

        # Calculate relative path and destination
        try:
            rel_path = file_path.relative_to(source_root)
            dest_path = dest_root / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(file_path, dest_path)
            self.stats['files_copied'] += 1
            self.stats['total_size'] += file_size
            logger.debug(f"Copied: {file_path}")

        except PermissionError:
            logger.warning(f"Permission denied: {file_path}")
            self.stats['files_skipped'] += 1
        except Exception as e:
            error_msg = f"Error copying {file_path}: {e}"
            logger.warning(error_msg)
            self.stats['errors'].append(error_msg)
            self.stats['files_skipped'] += 1

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes into human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
