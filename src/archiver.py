"""
Data archival and reporting module.
Creates ZIP archives and generates extraction reports.
"""

import os
import json
import logging
import pyzipper
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataArchiver:
    """Creates archives and reports for extracted data."""

    def __init__(self, config: Dict):
        """
        Initialize the data archiver.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.extraction_config = config.get('extraction', {})

    def create_archive(self, source_dir: Path, output_path: Path, password: Optional[str] = None) -> bool:
        """
        Create a password-protected ZIP archive of extracted data.

        Args:
            source_dir: Directory containing extracted data
            output_path: Output path for the ZIP file
            password: Optional password for the archive

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Creating archive: {output_path}")

        try:
            # Use password if provided
            if password:
                logger.info("Creating password-protected archive")
                compression = pyzipper.ZIP_LZMA
                encryption = pyzipper.WZ_AES

                with pyzipper.AESZipFile(
                    output_path,
                    'w',
                    compression=compression,
                    encryption=encryption
                ) as zipf:
                    zipf.setpassword(password.encode('utf-8'))
                    self._add_directory_to_zip(zipf, source_dir, source_dir)
            else:
                # Create regular ZIP file
                import zipfile
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    self._add_directory_to_zip(zipf, source_dir, source_dir)

            archive_size = output_path.stat().st_size
            logger.info(f"Archive created successfully: {self._format_size(archive_size)}")
            return True

        except Exception as e:
            logger.error(f"Error creating archive: {e}")
            return False

    def _add_directory_to_zip(self, zipf, directory: Path, base_path: Path) -> None:
        """
        Recursively add directory contents to ZIP file.

        Args:
            zipf: ZIP file handle
            directory: Directory to add
            base_path: Base path for calculating relative paths
        """
        for item in directory.rglob('*'):
            if item.is_file():
                arcname = item.relative_to(base_path)
                zipf.write(item, arcname)

    def generate_report(
        self,
        username: str,
        user_email: str,
        output_dir: Path,
        stats: Dict,
        duration: float
    ) -> Path:
        """
        Generate extraction report.

        Args:
            username: Windows username
            user_email: User email address
            output_dir: Output directory
            stats: Statistics from all extractors
            duration: Total extraction duration in seconds

        Returns:
            Path to generated report file
        """
        logger.info("Generating extraction report")

        report_path = output_dir / "extraction_report.txt"

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                # Header
                f.write("=" * 80 + "\n")
                f.write("EMPLOYEE DATA EXTRACTION REPORT\n")
                f.write("=" * 80 + "\n\n")

                # Metadata
                f.write(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Username: {username}\n")
                f.write(f"Email: {user_email}\n")
                f.write(f"Duration: {self._format_duration(duration)}\n\n")

                f.write("=" * 80 + "\n\n")

                # Local data statistics
                f.write("LOCAL DATA EXTRACTION\n")
                f.write("-" * 80 + "\n")
                local_stats = stats.get('local', {})
                if local_stats:
                    f.write(f"Files Copied: {local_stats.get('files_copied', 0)}\n")
                    f.write(f"Files Skipped: {local_stats.get('files_skipped', 0)}\n")
                    f.write(f"Total Size: {self._format_size(local_stats.get('total_size', 0))}\n")
                    if local_stats.get('errors'):
                        f.write(f"Errors: {len(local_stats['errors'])}\n")
                else:
                    f.write("Not performed\n")
                f.write("\n")

                # Email archives
                f.write("EMAIL ARCHIVES\n")
                f.write("-" * 80 + "\n")
                email_stats = stats.get('email', {})
                if email_stats:
                    f.write(f"PST Files: {email_stats.get('pst_files', 0)}\n")
                    f.write(f"OST Files: {email_stats.get('ost_files', 0)}\n")
                    f.write(f"Total Size: {self._format_size(email_stats.get('total_size', 0))}\n")
                    if email_stats.get('errors'):
                        f.write(f"Errors: {len(email_stats['errors'])}\n")
                else:
                    f.write("Not performed\n")
                f.write("\n")

                # Browser data
                f.write("BROWSER DATA\n")
                f.write("-" * 80 + "\n")
                browser_stats = stats.get('browser', {})
                if browser_stats:
                    f.write(f"Browsers Found: {browser_stats.get('browsers_found', 0)}\n")
                    f.write(f"Profiles Extracted: {browser_stats.get('profiles_extracted', 0)}\n")
                    f.write(f"Files Copied: {browser_stats.get('files_copied', 0)}\n")
                    f.write(f"Total Size: {self._format_size(browser_stats.get('total_size', 0))}\n")
                    if browser_stats.get('errors'):
                        f.write(f"Errors: {len(browser_stats['errors'])}\n")
                else:
                    f.write("Not performed\n")
                f.write("\n")

                # OneDrive
                f.write("ONEDRIVE\n")
                f.write("-" * 80 + "\n")
                onedrive_stats = stats.get('onedrive', {})
                if onedrive_stats:
                    f.write(f"Files Downloaded: {onedrive_stats.get('files_downloaded', 0)}\n")
                    f.write(f"Folders Created: {onedrive_stats.get('folders_created', 0)}\n")
                    f.write(f"Total Size: {self._format_size(onedrive_stats.get('total_size', 0))}\n")
                    if onedrive_stats.get('errors'):
                        f.write(f"Errors: {len(onedrive_stats['errors'])}\n")
                else:
                    f.write("Not performed\n")
                f.write("\n")

                # SharePoint
                f.write("SHAREPOINT\n")
                f.write("-" * 80 + "\n")
                sharepoint_stats = stats.get('sharepoint', {})
                if sharepoint_stats:
                    f.write(f"Sites Processed: {sharepoint_stats.get('sites_processed', 0)}\n")
                    f.write(f"Files Downloaded: {sharepoint_stats.get('files_downloaded', 0)}\n")
                    f.write(f"Folders Created: {sharepoint_stats.get('folders_created', 0)}\n")
                    f.write(f"Total Size: {self._format_size(sharepoint_stats.get('total_size', 0))}\n")
                    if sharepoint_stats.get('errors'):
                        f.write(f"Errors: {len(sharepoint_stats['errors'])}\n")
                else:
                    f.write("Not performed\n")
                f.write("\n")

                # Teams
                f.write("TEAMS CHATS\n")
                f.write("-" * 80 + "\n")
                teams_stats = stats.get('teams', {})
                if teams_stats:
                    f.write(f"Chats Exported: {teams_stats.get('chats_exported', 0)}\n")
                    f.write(f"Messages Exported: {teams_stats.get('messages_exported', 0)}\n")
                    f.write(f"Files Downloaded: {teams_stats.get('files_downloaded', 0)}\n")
                    f.write(f"Total Size: {self._format_size(teams_stats.get('total_size', 0))}\n")
                    if teams_stats.get('errors'):
                        f.write(f"Errors: {len(teams_stats['errors'])}\n")
                else:
                    f.write("Not performed\n")
                f.write("\n")

                # Summary
                f.write("=" * 80 + "\n")
                f.write("SUMMARY\n")
                f.write("=" * 80 + "\n")

                total_files = (
                    local_stats.get('files_copied', 0) +
                    browser_stats.get('files_copied', 0) +
                    onedrive_stats.get('files_downloaded', 0) +
                    sharepoint_stats.get('files_downloaded', 0) +
                    teams_stats.get('files_downloaded', 0)
                )

                total_size = (
                    local_stats.get('total_size', 0) +
                    email_stats.get('total_size', 0) +
                    browser_stats.get('total_size', 0) +
                    onedrive_stats.get('total_size', 0) +
                    sharepoint_stats.get('total_size', 0) +
                    teams_stats.get('total_size', 0)
                )

                total_errors = sum(
                    len(s.get('errors', [])) for s in stats.values()
                )

                f.write(f"Total Files Extracted: {total_files}\n")
                f.write(f"Total Data Size: {self._format_size(total_size)}\n")
                f.write(f"Total Errors: {total_errors}\n")

                f.write("\n" + "=" * 80 + "\n")

            # Also create JSON report
            json_report_path = output_dir / "extraction_report.json"
            with open(json_report_path, 'w', encoding='utf-8') as f:
                report_data = {
                    'timestamp': datetime.now().isoformat(),
                    'username': username,
                    'email': user_email,
                    'duration_seconds': duration,
                    'statistics': stats
                }
                json.dump(report_data, f, indent=2)

            logger.info(f"Report generated: {report_path}")
            return report_path

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes into human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in seconds to human-readable string."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
