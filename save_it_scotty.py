#!/usr/bin/env python3
"""
Save-it-Scotty: Employee Offboarding Data Extraction Tool

Comprehensive tool for extracting employee data during offboarding:
- Local device data (Desktop, Documents, Downloads, AppData)
- Email archives (PST/OST files)
- Browser data (Chrome, Edge, Firefox)
- OneDrive files
- SharePoint documents
- Teams chat logs
"""

import os
import sys
import logging
import yaml
import click
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from local_extractor import LocalDataExtractor
from email_extractor import EmailArchiveExtractor
from browser_extractor import BrowserDataExtractor
from graph_auth import GraphAuthenticator
from onedrive_extractor import OneDriveExtractor
from sharepoint_extractor import SharePointExtractor
from teams_extractor import TeamsExtractor
from archiver import DataArchiver

console = Console()


def setup_logging(config: dict) -> None:
    """
    Set up logging configuration.

    Args:
        config: Configuration dictionary
    """
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))

    # Create logs directory if needed
    if log_config.get('log_to_file', True):
        log_file = Path(log_config.get('log_file', './logs/extraction.log'))
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                RichHandler(console=console, rich_tracebacks=True),
                logging.FileHandler(log_file)
            ]
        )
    else:
        logging.basicConfig(
            level=log_level,
            format="%(message)s",
            handlers=[RichHandler(console=console, rich_tracebacks=True)]
        )


def load_config(config_path: str) -> dict:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)

    if not config_file.exists():
        console.print(f"[red]Error: Configuration file not found: {config_path}[/red]")
        console.print("\n[yellow]Please copy config.yaml.example to config.yaml and configure it.[/yellow]")
        sys.exit(1)

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return config


@click.command()
@click.option(
    '--username',
    required=True,
    help='Windows username of the terminated employee'
)
@click.option(
    '--email',
    required=True,
    help='Email address of the terminated employee'
)
@click.option(
    '--config',
    default='config.yaml',
    help='Path to configuration file (default: config.yaml)'
)
@click.option(
    '--output-dir',
    default=None,
    help='Output directory (overrides config)'
)
@click.option(
    '--skip-local',
    is_flag=True,
    help='Skip local file system extraction'
)
@click.option(
    '--skip-cloud',
    is_flag=True,
    help='Skip cloud data extraction (OneDrive, SharePoint, Teams)'
)
@click.option(
    '--no-archive',
    is_flag=True,
    help='Do not create ZIP archive'
)
def main(username: str, email: str, config: str, output_dir: str, skip_local: bool, skip_cloud: bool, no_archive: bool):
    """
    Save-it-Scotty: Employee Offboarding Data Extraction Tool

    Extracts all data from a terminated employee's device and cloud storage.
    """
    start_time = time.time()

    # Load configuration
    try:
        cfg = load_config(config)
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        sys.exit(1)

    # Setup logging
    setup_logging(cfg)
    logger = logging.getLogger(__name__)

    # Display banner
    console.print("\n[bold cyan]╔═══════════════════════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║         SAVE-IT-SCOTTY: Data Extraction Tool          ║[/bold cyan]")
    console.print("[bold cyan]╚═══════════════════════════════════════════════════════════╝[/bold cyan]\n")

    console.print(f"[bold]Target User:[/bold] {username} ({email})")
    console.print(f"[bold]Extraction Date:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Determine output directory
    if output_dir:
        output_path = Path(output_dir)
    else:
        base_output = Path(cfg.get('extraction', {}).get('output_dir', './extracted_data'))
        if cfg.get('extraction', {}).get('use_timestamps', True):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = base_output / f"{username}_{timestamp}"
        else:
            output_path = base_output / username

    output_path.mkdir(parents=True, exist_ok=True)
    console.print(f"[bold]Output Directory:[/bold] {output_path}\n")

    # Statistics dictionary
    stats = {}

    try:
        # ===== LOCAL EXTRACTION =====
        if not skip_local:
            console.print("\n[bold yellow]═══ LOCAL DATA EXTRACTION ═══[/bold yellow]\n")

            # Local file system
            if cfg.get('local_extraction', {}).get('include_desktop', True):
                console.print("[cyan]→ Extracting local file system data...[/cyan]")
                extractor = LocalDataExtractor(cfg, output_path)
                stats['local'] = extractor.extract_all(username)

            # Email archives
            if cfg.get('local_extraction', {}).get('include_email_archives', True):
                console.print("[cyan]→ Searching for email archives...[/cyan]")
                email_extractor = EmailArchiveExtractor(cfg, output_path)
                stats['email'] = email_extractor.extract_all(username)

            # Browser data
            if cfg.get('local_extraction', {}).get('include_browser_data', True):
                console.print("[cyan]→ Extracting browser data...[/cyan]")
                browser_extractor = BrowserDataExtractor(cfg, output_path)
                stats['browser'] = browser_extractor.extract_all(username)

        # ===== CLOUD EXTRACTION =====
        if not skip_cloud:
            console.print("\n[bold yellow]═══ CLOUD DATA EXTRACTION ═══[/bold yellow]\n")
            console.print("[cyan]→ Authenticating with Microsoft Graph API...[/cyan]")

            try:
                auth = GraphAuthenticator(cfg)
                auth.authenticate()
                auth.validate_permissions()

                # OneDrive
                if cfg.get('cloud_extraction', {}).get('include_onedrive', True):
                    console.print("[cyan]→ Extracting OneDrive data...[/cyan]")
                    onedrive_extractor = OneDriveExtractor(auth, cfg, output_path)
                    stats['onedrive'] = onedrive_extractor.extract_all(email)

                # SharePoint
                if cfg.get('cloud_extraction', {}).get('include_sharepoint', True):
                    console.print("[cyan]→ Extracting SharePoint data...[/cyan]")
                    sharepoint_extractor = SharePointExtractor(auth, cfg, output_path)
                    stats['sharepoint'] = sharepoint_extractor.extract_all(email)

                # Teams
                if cfg.get('cloud_extraction', {}).get('include_teams_chats', True):
                    console.print("[cyan]→ Extracting Teams chat logs...[/cyan]")
                    teams_extractor = TeamsExtractor(auth, cfg, output_path)
                    stats['teams'] = teams_extractor.extract_all(email)

            except Exception as e:
                logger.error(f"Cloud extraction error: {e}")
                console.print(f"[red]Cloud extraction failed: {e}[/red]")

        # ===== REPORTING =====
        console.print("\n[bold yellow]═══ GENERATING REPORT ═══[/bold yellow]\n")

        duration = time.time() - start_time
        archiver = DataArchiver(cfg)
        report_path = archiver.generate_report(username, email, output_path, stats, duration)

        console.print(f"[green]✓ Report generated: {report_path}[/green]")

        # ===== ARCHIVING =====
        if not no_archive and cfg.get('extraction', {}).get('create_archive', True):
            console.print("\n[bold yellow]═══ CREATING ARCHIVE ═══[/bold yellow]\n")

            archive_password = cfg.get('extraction', {}).get('archive_password', '')
            archive_name = f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            archive_path = output_path.parent / archive_name

            console.print("[cyan]→ Compressing extracted data...[/cyan]")
            success = archiver.create_archive(output_path, archive_path, archive_password or None)

            if success:
                console.print(f"[green]✓ Archive created: {archive_path}[/green]")
                if archive_password:
                    console.print("[yellow]⚠ Archive is password-protected[/yellow]")

        # ===== COMPLETION =====
        console.print("\n[bold green]╔═══════════════════════════════════════════════════════════╗[/bold green]")
        console.print("[bold green]║              EXTRACTION COMPLETED SUCCESSFULLY            ║[/bold green]")
        console.print("[bold green]╚═══════════════════════════════════════════════════════════╝[/bold green]\n")

        console.print(f"[bold]Total Duration:[/bold] {archiver._format_duration(duration)}")
        console.print(f"[bold]Output Location:[/bold] {output_path}\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Extraction interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.exception("Fatal error during extraction")
        console.print(f"\n[red]✗ Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
