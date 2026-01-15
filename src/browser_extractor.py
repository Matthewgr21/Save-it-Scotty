"""
Browser data extraction module.
Extracts bookmarks, history, and saved credentials from web browsers.
"""

import os
import shutil
import logging
import json
import sqlite3
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class BrowserDataExtractor:
    """Extracts data from Chrome, Edge, and Firefox browsers."""

    # Browser data locations relative to user profile
    BROWSER_PATHS = {
        'chrome': {
            'name': 'Google Chrome',
            'base': 'AppData/Local/Google/Chrome/User Data',
            'profiles': ['Default', 'Profile 1', 'Profile 2'],
            'files': {
                'bookmarks': 'Bookmarks',
                'history': 'History',
                'login_data': 'Login Data',
                'preferences': 'Preferences'
            }
        },
        'edge': {
            'name': 'Microsoft Edge',
            'base': 'AppData/Local/Microsoft/Edge/User Data',
            'profiles': ['Default', 'Profile 1', 'Profile 2'],
            'files': {
                'bookmarks': 'Bookmarks',
                'history': 'History',
                'login_data': 'Login Data',
                'preferences': 'Preferences'
            }
        },
        'firefox': {
            'name': 'Mozilla Firefox',
            'base': 'AppData/Roaming/Mozilla/Firefox/Profiles',
            'profiles': None,  # Firefox uses random profile names
            'files': {
                'bookmarks': 'places.sqlite',
                'history': 'places.sqlite',
                'login_data': 'logins.json',
                'preferences': 'prefs.js'
            }
        }
    }

    def __init__(self, config: Dict, output_dir: Path):
        """
        Initialize the browser data extractor.

        Args:
            config: Configuration dictionary
            output_dir: Output directory for extracted data
        """
        self.config = config
        self.output_dir = output_dir
        self.browsers = config.get('local_extraction', {}).get('browsers', ['chrome', 'edge', 'firefox'])
        self.stats = {
            'browsers_found': 0,
            'profiles_extracted': 0,
            'files_copied': 0,
            'total_size': 0,
            'errors': []
        }

    def extract_all(self, username: str) -> Dict:
        """
        Extract data from all configured browsers.

        Args:
            username: Windows username

        Returns:
            Dictionary with extraction statistics
        """
        logger.info(f"Starting browser data extraction for user: {username}")

        user_profile = Path(f"C:\\Users\\{username}")
        if not user_profile.exists():
            raise FileNotFoundError(f"User profile not found: {user_profile}")

        # Create browser extraction directory
        browser_output = self.output_dir / "browser_data"
        browser_output.mkdir(parents=True, exist_ok=True)

        # Extract each browser
        for browser in self.browsers:
            if browser in self.BROWSER_PATHS:
                self._extract_browser(browser, user_profile, browser_output)

        logger.info(f"Browser data extraction completed. Browsers found: {self.stats['browsers_found']}, "
                   f"Profiles extracted: {self.stats['profiles_extracted']}, "
                   f"Files copied: {self.stats['files_copied']}")

        return self.stats

    def _extract_browser(self, browser_key: str, user_profile: Path, output_dir: Path) -> None:
        """
        Extract data from a specific browser.

        Args:
            browser_key: Browser identifier (chrome, edge, firefox)
            user_profile: User profile path
            output_dir: Output directory
        """
        browser_config = self.BROWSER_PATHS[browser_key]
        browser_name = browser_config['name']
        browser_base = user_profile / browser_config['base']

        if not browser_base.exists():
            logger.debug(f"{browser_name} not found at: {browser_base}")
            return

        logger.info(f"Extracting {browser_name} data")
        self.stats['browsers_found'] += 1

        browser_out = output_dir / browser_key
        browser_out.mkdir(parents=True, exist_ok=True)

        # Handle Firefox separately (different profile structure)
        if browser_key == 'firefox':
            self._extract_firefox_profiles(browser_base, browser_out, browser_config)
        else:
            self._extract_chromium_profiles(browser_base, browser_out, browser_config)

    def _extract_chromium_profiles(self, browser_base: Path, output_dir: Path, config: Dict) -> None:
        """
        Extract profiles from Chromium-based browsers (Chrome, Edge).

        Args:
            browser_base: Browser base directory
            output_dir: Output directory
            config: Browser configuration
        """
        for profile in config['profiles']:
            profile_path = browser_base / profile
            if not profile_path.exists():
                continue

            logger.debug(f"Extracting profile: {profile}")
            profile_out = output_dir / profile
            profile_out.mkdir(parents=True, exist_ok=True)

            # Extract each file type
            for file_type, file_name in config['files'].items():
                source_file = profile_path / file_name
                if source_file.exists():
                    self._copy_browser_file(source_file, profile_out, file_type)

            self.stats['profiles_extracted'] += 1

    def _extract_firefox_profiles(self, browser_base: Path, output_dir: Path, config: Dict) -> None:
        """
        Extract profiles from Firefox (has random profile directory names).

        Args:
            browser_base: Browser base directory
            output_dir: Output directory
            config: Browser configuration
        """
        if not browser_base.exists():
            return

        # Firefox profiles have random names, find all .default or .default-release folders
        try:
            for profile_dir in browser_base.iterdir():
                if profile_dir.is_dir() and ('.default' in profile_dir.name or 'release' in profile_dir.name):
                    logger.debug(f"Extracting Firefox profile: {profile_dir.name}")

                    profile_out = output_dir / profile_dir.name
                    profile_out.mkdir(parents=True, exist_ok=True)

                    # Extract each file type
                    for file_type, file_name in config['files'].items():
                        source_file = profile_dir / file_name
                        if source_file.exists():
                            self._copy_browser_file(source_file, profile_out, file_type)

                    self.stats['profiles_extracted'] += 1

        except PermissionError as e:
            logger.warning(f"Permission denied accessing Firefox profiles: {e}")
        except Exception as e:
            logger.warning(f"Error extracting Firefox profiles: {e}")

    def _copy_browser_file(self, source_file: Path, destination: Path, file_type: str) -> None:
        """
        Copy a browser data file with error handling.

        Args:
            source_file: Source file path
            destination: Destination directory
            file_type: Type of file (for naming)
        """
        try:
            dest_file = destination / source_file.name
            file_size = source_file.stat().st_size

            # For SQLite databases, copy with special handling
            if source_file.suffix == '.sqlite':
                self._copy_sqlite_file(source_file, dest_file)
            else:
                shutil.copy2(source_file, dest_file)

            self.stats['files_copied'] += 1
            self.stats['total_size'] += file_size
            logger.debug(f"Copied browser file: {source_file.name}")

        except PermissionError:
            logger.warning(f"Permission denied (browser may be running): {source_file}")
        except Exception as e:
            error_msg = f"Error copying browser file {source_file}: {e}"
            logger.warning(error_msg)
            self.stats['errors'].append(error_msg)

    def _copy_sqlite_file(self, source: Path, destination: Path) -> None:
        """
        Copy SQLite database file (may be locked if browser is running).

        Args:
            source: Source database file
            destination: Destination file path
        """
        try:
            # Try direct copy first
            shutil.copy2(source, destination)
        except Exception:
            # If locked, try to read and copy via SQLite
            try:
                source_conn = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
                dest_conn = sqlite3.connect(destination)

                # Copy database
                source_conn.backup(dest_conn)

                source_conn.close()
                dest_conn.close()
            except Exception as e:
                raise Exception(f"Could not copy locked database: {e}")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes into human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
