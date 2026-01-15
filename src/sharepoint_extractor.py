"""
SharePoint data extraction module.
Extracts files from SharePoint sites via Microsoft Graph API.
"""

import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)


class SharePointExtractor:
    """Extracts files from SharePoint sites using Microsoft Graph API."""

    GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"

    def __init__(self, authenticator, config: Dict, output_dir: Path):
        """
        Initialize the SharePoint extractor.

        Args:
            authenticator: GraphAuthenticator instance
            config: Configuration dictionary
            output_dir: Output directory for extracted data
        """
        self.auth = authenticator
        self.config = config
        self.output_dir = output_dir
        self.headers = None
        self.cloud_config = config.get('cloud_extraction', {})
        self.stats = {
            'sites_processed': 0,
            'files_downloaded': 0,
            'folders_created': 0,
            'total_size': 0,
            'errors': []
        }

    def extract_all(self, user_email: str) -> Dict:
        """
        Extract files from SharePoint sites the user has access to.

        Args:
            user_email: User's email address or UPN

        Returns:
            Dictionary with extraction statistics
        """
        logger.info(f"Starting SharePoint extraction for user: {user_email}")

        # Get authentication headers
        self.headers = self.auth.get_headers()

        # Create SharePoint output directory
        sharepoint_output = self.output_dir / "sharepoint"
        sharepoint_output.mkdir(parents=True, exist_ok=True)

        try:
            # Get user ID from email
            user_id = self._get_user_id(user_email)
            if not user_id:
                raise Exception(f"Could not find user: {user_email}")

            # Get SharePoint sites
            configured_sites = self.cloud_config.get('sharepoint_sites', [])

            if configured_sites:
                # Extract specific configured sites
                logger.info(f"Extracting {len(configured_sites)} configured SharePoint sites")
                for site_url in configured_sites:
                    self._extract_site_by_url(site_url, sharepoint_output)
            else:
                # Extract all sites user has access to
                logger.info("Extracting all SharePoint sites user has access to")
                self._extract_user_sites(user_id, sharepoint_output)

            logger.info(f"SharePoint extraction completed. Sites processed: {self.stats['sites_processed']}, "
                       f"Files downloaded: {self.stats['files_downloaded']}, "
                       f"Total size: {self._format_size(self.stats['total_size'])}")

        except Exception as e:
            error_msg = f"SharePoint extraction error: {e}"
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
                logger.error(f"Error getting user ID: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting user ID: {e}")
            return None

    def _extract_user_sites(self, user_id: str, output_dir: Path) -> None:
        """
        Extract all SharePoint sites the user has access to.

        Args:
            user_id: User ID
            output_dir: Output directory
        """
        try:
            # Get sites user follows or has access to
            url = f"{self.GRAPH_ENDPOINT}/users/{user_id}/followedSites"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                sites = data.get('value', [])

                logger.info(f"Found {len(sites)} SharePoint sites")

                for site in sites:
                    site_name = site.get('displayName', site.get('name', 'Unknown'))
                    site_id = site.get('id')

                    if site_id:
                        self._extract_site(site_id, site_name, output_dir)

            else:
                logger.warning(f"Could not get user's SharePoint sites: {response.status_code}")

                # Fallback: try to get all sites in organization (may be limited)
                self._extract_all_organization_sites(output_dir)

        except Exception as e:
            logger.error(f"Error extracting user sites: {e}")

    def _extract_all_organization_sites(self, output_dir: Path) -> None:
        """
        Extract all SharePoint sites in the organization (fallback method).

        Args:
            output_dir: Output directory
        """
        try:
            url = f"{self.GRAPH_ENDPOINT}/sites?search=*"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                sites = data.get('value', [])

                logger.info(f"Found {len(sites)} organization SharePoint sites")

                # Limit to first 10 to avoid overwhelming extraction
                for site in sites[:10]:
                    site_name = site.get('displayName', site.get('name', 'Unknown'))
                    site_id = site.get('id')

                    if site_id:
                        self._extract_site(site_id, site_name, output_dir)

        except Exception as e:
            logger.error(f"Error extracting organization sites: {e}")

    def _extract_site_by_url(self, site_url: str, output_dir: Path) -> None:
        """
        Extract a SharePoint site by its URL.

        Args:
            site_url: SharePoint site URL
            output_dir: Output directory
        """
        try:
            # Parse site URL to get hostname and path
            # Format: https://tenant.sharepoint.com/sites/sitename
            url = f"{self.GRAPH_ENDPOINT}/sites/{quote(site_url)}"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                site = response.json()
                site_name = site.get('displayName', site.get('name', 'Unknown'))
                site_id = site.get('id')

                if site_id:
                    self._extract_site(site_id, site_name, output_dir)
            else:
                logger.error(f"Could not access site {site_url}: {response.status_code}")

        except Exception as e:
            logger.error(f"Error extracting site by URL {site_url}: {e}")

    def _extract_site(self, site_id: str, site_name: str, output_dir: Path) -> None:
        """
        Extract all document libraries from a SharePoint site.

        Args:
            site_id: Site ID
            site_name: Site display name
            output_dir: Output directory
        """
        logger.info(f"Extracting SharePoint site: {site_name}")
        self.stats['sites_processed'] += 1

        # Create site output directory
        safe_site_name = "".join(c for c in site_name if c.isalnum() or c in (' ', '-', '_')).strip()
        site_output = output_dir / safe_site_name
        site_output.mkdir(parents=True, exist_ok=True)

        try:
            # Get document libraries (drives) in the site
            url = f"{self.GRAPH_ENDPOINT}/sites/{site_id}/drives"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                drives = data.get('value', [])

                logger.debug(f"Found {len(drives)} document libraries in {site_name}")

                for drive in drives:
                    drive_name = drive.get('name', 'Documents')
                    drive_id = drive.get('id')

                    if drive_id:
                        drive_output = site_output / drive_name
                        drive_output.mkdir(parents=True, exist_ok=True)
                        self._extract_drive(site_id, drive_id, drive_output)

            else:
                logger.warning(f"Could not get drives for site {site_name}: {response.status_code}")

        except Exception as e:
            error_msg = f"Error extracting site {site_name}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)

    def _extract_drive(self, site_id: str, drive_id: str, output_dir: Path) -> None:
        """
        Extract all files from a SharePoint document library.

        Args:
            site_id: Site ID
            drive_id: Drive (document library) ID
            output_dir: Output directory
        """
        try:
            self._extract_drive_items(site_id, drive_id, "/", output_dir)
        except Exception as e:
            logger.error(f"Error extracting drive: {e}")

    def _extract_drive_items(self, site_id: str, drive_id: str, folder_path: str, output_dir: Path) -> None:
        """
        Recursively extract all items from a drive folder.

        Args:
            site_id: Site ID
            drive_id: Drive ID
            folder_path: Current folder path
            output_dir: Output directory
        """
        try:
            items = self._list_drive_items(site_id, drive_id, folder_path)

            for item in items:
                item_name = item.get('name', 'unknown')
                item_path = f"{folder_path.rstrip('/')}/{item_name}"

                if 'folder' in item:
                    # It's a folder - recurse
                    folder_output = output_dir / item_name
                    folder_output.mkdir(parents=True, exist_ok=True)
                    self.stats['folders_created'] += 1

                    self._extract_drive_items(site_id, drive_id, item_path, folder_output)

                elif 'file' in item:
                    # It's a file - download
                    self._download_file(item, output_dir)

        except Exception as e:
            logger.error(f"Error extracting items from {folder_path}: {e}")

    def _list_drive_items(self, site_id: str, drive_id: str, folder_path: str) -> List[Dict]:
        """
        List all items in a drive folder.

        Args:
            site_id: Site ID
            drive_id: Drive ID
            folder_path: Folder path

        Returns:
            List of item dictionaries
        """
        items = []

        try:
            if folder_path == "/":
                url = f"{self.GRAPH_ENDPOINT}/sites/{site_id}/drives/{drive_id}/root/children"
            else:
                encoded_path = quote(folder_path)
                url = f"{self.GRAPH_ENDPOINT}/sites/{site_id}/drives/{drive_id}/root:{encoded_path}:/children"

            # Handle pagination
            while url:
                response = requests.get(url, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    items.extend(data.get('value', []))
                    url = data.get('@odata.nextLink')
                else:
                    logger.warning(f"Error listing items: {response.status_code}")
                    break

        except Exception as e:
            logger.error(f"Error listing drive items: {e}")

        return items

    def _download_file(self, item: Dict, output_dir: Path) -> None:
        """
        Download a file from SharePoint.

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

            response = requests.get(download_url, stream=True)
            response.raise_for_status()

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
