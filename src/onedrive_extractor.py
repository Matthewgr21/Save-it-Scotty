"""
OneDrive data extraction module.
Extracts files from user's OneDrive via Microsoft Graph API.
"""

import os
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)


class OneDriveExtractor:
    """Extracts files from user's OneDrive using Microsoft Graph API."""

    GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"

    def __init__(self, authenticator, config: Dict, output_dir: Path):
        """
        Initialize the OneDrive extractor.

        Args:
            authenticator: GraphAuthenticator instance
            config: Configuration dictionary
            output_dir: Output directory for extracted data
        """
        self.auth = authenticator
        self.config = config
        self.output_dir = output_dir
        self.headers = None
        self.stats = {
            'files_downloaded': 0,
            'folders_created': 0,
            'total_size': 0,
            'errors': []
        }

    def extract_all(self, user_email: str) -> Dict:
        """
        Extract all files from user's OneDrive.

        Args:
            user_email: User's email address or UPN

        Returns:
            Dictionary with extraction statistics
        """
        logger.info(f"Starting OneDrive extraction for user: {user_email}")

        # Get authentication headers
        self.headers = self.auth.get_headers()

        # Create OneDrive output directory
        onedrive_output = self.output_dir / "onedrive"
        onedrive_output.mkdir(parents=True, exist_ok=True)

        try:
            # Get user ID from email
            user_id = self._get_user_id(user_email)
            if not user_id:
                raise Exception(f"Could not find user: {user_email}")

            # Get OneDrive root
            drive_id = self._get_drive_id(user_id)
            if not drive_id:
                raise Exception(f"Could not access OneDrive for user: {user_email}")

            # Extract all files recursively
            self._extract_drive_items(user_id, drive_id, "/", onedrive_output)

            logger.info(f"OneDrive extraction completed. Files downloaded: {self.stats['files_downloaded']}, "
                       f"Folders created: {self.stats['folders_created']}, "
                       f"Total size: {self._format_size(self.stats['total_size'])}")

        except Exception as e:
            error_msg = f"OneDrive extraction error: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)

        return self.stats

    def _get_user_id(self, user_email: str) -> Optional[str]:
        """
        Get user ID from email address.

        Args:
            user_email: User email address

        Returns:
            User ID or None if not found
        """
        try:
            url = f"{self.GRAPH_ENDPOINT}/users/{quote(user_email)}"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                user_data = response.json()
                return user_data.get('id')
            else:
                logger.error(f"Error getting user ID: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting user ID: {e}")
            return None

    def _get_drive_id(self, user_id: str) -> Optional[str]:
        """
        Get user's OneDrive drive ID.

        Args:
            user_id: User ID

        Returns:
            Drive ID or None if not found
        """
        try:
            url = f"{self.GRAPH_ENDPOINT}/users/{user_id}/drive"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                drive_data = response.json()
                return drive_data.get('id')
            else:
                logger.error(f"Error getting drive ID: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting drive ID: {e}")
            return None

    def _extract_drive_items(self, user_id: str, drive_id: str, folder_path: str, output_dir: Path) -> None:
        """
        Recursively extract all items from a OneDrive folder.

        Args:
            user_id: User ID
            drive_id: Drive ID
            folder_path: Current folder path (relative to root)
            output_dir: Output directory for this folder
        """
        try:
            # Get items in current folder
            items = self._list_drive_items(user_id, drive_id, folder_path)

            for item in items:
                item_name = item.get('name', 'unknown')
                item_path = f"{folder_path.rstrip('/')}/{item_name}"

                if 'folder' in item:
                    # It's a folder - recurse
                    folder_output = output_dir / item_name
                    folder_output.mkdir(parents=True, exist_ok=True)
                    self.stats['folders_created'] += 1

                    logger.debug(f"Entering folder: {item_path}")
                    self._extract_drive_items(user_id, drive_id, item_path, folder_output)

                elif 'file' in item:
                    # It's a file - download
                    self._download_file(item, output_dir)

        except Exception as e:
            error_msg = f"Error extracting items from {folder_path}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)

    def _list_drive_items(self, user_id: str, drive_id: str, folder_path: str) -> List[Dict]:
        """
        List all items in a OneDrive folder.

        Args:
            user_id: User ID
            drive_id: Drive ID
            folder_path: Folder path

        Returns:
            List of item dictionaries
        """
        items = []

        try:
            # Encode folder path for URL
            if folder_path == "/":
                url = f"{self.GRAPH_ENDPOINT}/users/{user_id}/drive/root/children"
            else:
                encoded_path = quote(folder_path)
                url = f"{self.GRAPH_ENDPOINT}/users/{user_id}/drive/root:{encoded_path}:/children"

            # Handle pagination
            while url:
                response = requests.get(url, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    items.extend(data.get('value', []))

                    # Check for next page
                    url = data.get('@odata.nextLink')
                else:
                    logger.warning(f"Error listing items in {folder_path}: {response.status_code}")
                    break

        except Exception as e:
            logger.error(f"Error listing drive items: {e}")

        return items

    def _download_file(self, item: Dict, output_dir: Path) -> None:
        """
        Download a file from OneDrive.

        Args:
            item: Item dictionary from Graph API
            output_dir: Output directory
        """
        file_name = item.get('name', 'unknown')
        download_url = item.get('@microsoft.graph.downloadUrl')
        file_size = item.get('size', 0)

        if not download_url:
            logger.warning(f"No download URL for file: {file_name}")
            return

        try:
            logger.debug(f"Downloading: {file_name} ({self._format_size(file_size)})")

            # Download file
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # Save file
            dest_path = output_dir / file_name
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.stats['files_downloaded'] += 1
            self.stats['total_size'] += file_size

        except Exception as e:
            error_msg = f"Error downloading {file_name}: {e}"
            logger.warning(error_msg)
            self.stats['errors'].append(error_msg)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes into human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
