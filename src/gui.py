"""
GUI interface for Save-it-Scotty
Simple graphical interface for IT administrators - Local Data Extraction Only
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import threading
import logging
from datetime import datetime
import queue

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SaveItScottyGUI:
    """Main GUI application for Save-it-Scotty"""

    def __init__(self, root):
        self.root = root
        self.root.title("Save-it-Scotty - Employee Data Extraction Tool")
        self.root.geometry("800x650")
        self.root.resizable(True, True)

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Variables
        self.username_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Desktop" / "Extracted_Data"))

        # Extraction options
        self.extract_local_var = tk.BooleanVar(value=True)
        self.extract_email_var = tk.BooleanVar(value=True)
        self.extract_browser_var = tk.BooleanVar(value=True)
        self.create_archive_var = tk.BooleanVar(value=True)

        # Status
        self.is_running = False
        self.log_queue = queue.Queue()

        self.create_widgets()
        self.center_window()

        # Start log queue processor
        self.process_log_queue()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        title_label = ttk.Label(header_frame, text="Save-it-Scotty", font=('Arial', 16, 'bold'))
        title_label.pack()
        subtitle_label = ttk.Label(header_frame, text="Employee Offboarding Data Extraction Tool - Local Data Only",
                                   font=('Arial', 9))
        subtitle_label.pack()

        # User Information Section
        user_frame = ttk.LabelFrame(main_frame, text="Employee Information", padding="10")
        user_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        user_frame.columnconfigure(1, weight=1)

        ttk.Label(user_frame, text="Windows Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        username_entry = ttk.Entry(user_frame, textvariable=self.username_var, width=40)
        username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

        ttk.Label(user_frame, text="Email Address (optional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(user_frame, textvariable=self.email_var, width=40)
        email_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

        # Auto-detect button
        detect_btn = ttk.Button(user_frame, text="Auto-Detect Current User",
                               command=self.auto_detect_user)
        detect_btn.grid(row=0, column=2, rowspan=2, padx=(10, 0))

        # Output Directory Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Location", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)

        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var)
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        browse_btn = ttk.Button(output_frame, text="Browse...", command=self.browse_output_dir)
        browse_btn.grid(row=0, column=1, padx=(5, 0))

        # Extraction Options Section
        options_frame = ttk.LabelFrame(main_frame, text="Extraction Options", padding="10")
        options_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Local data options
        local_frame = ttk.Frame(options_frame)
        local_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        ttk.Label(local_frame, text="Local Device Data:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(local_frame, text="User Folders (Desktop, Documents, Downloads, AppData)",
                       variable=self.extract_local_var).grid(row=1, column=0, sticky=tk.W, padx=(20, 0))
        ttk.Checkbutton(local_frame, text="Email Archives (PST/OST files)",
                       variable=self.extract_email_var).grid(row=2, column=0, sticky=tk.W, padx=(20, 0))
        ttk.Checkbutton(local_frame, text="Browser Data (Chrome, Edge, Firefox)",
                       variable=self.extract_browser_var).grid(row=3, column=0, sticky=tk.W, padx=(20, 0))

        ttk.Separator(options_frame, orient='horizontal').grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)

        # Archive option
        ttk.Checkbutton(options_frame, text="Create password-protected ZIP archive",
                       variable=self.create_archive_var).grid(row=2, column=0, sticky=tk.W)

        # Info label
        info_label = ttk.Label(options_frame,
                               text="Note: This tool extracts local device data only. Cloud data (OneDrive, SharePoint, Teams)\nmust be extracted separately through Microsoft 365 admin portal.",
                               foreground='#666', font=('Arial', 8))
        info_label.grid(row=3, column=0, sticky=tk.W, pady=(10, 0))

        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        self.log_text = scrolledtext.ScrolledText(progress_frame, height=12, state='disabled',
                                                   wrap=tk.WORD, bg='#f0f0f0')
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))

        self.start_btn = ttk.Button(button_frame, text="Start Extraction",
                                     command=self.start_extraction, style='Accent.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_btn = ttk.Button(button_frame, text="Cancel",
                                    command=self.stop_extraction, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(button_frame, text="Clear Log",
                  command=self.clear_log).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(button_frame, text="Exit",
                  command=self.root.quit).pack(side=tk.RIGHT)

    def auto_detect_user(self):
        """Auto-detect current logged-in user"""
        try:
            username = os.getenv('USERNAME')
            userdomain = os.getenv('USERDOMAIN')

            if username:
                self.username_var.set(username)
                self.log_message(f"Detected username: {username}")

                # Try to detect email (common patterns)
                if userdomain:
                    email = f"{username}@{userdomain.lower()}.com"
                    self.email_var.set(email)
                    self.log_message(f"Suggested email: {email} (optional field)")

                messagebox.showinfo("Auto-Detect",
                                  f"Detected user: {username}\n\nEmail field is optional for local extraction.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not auto-detect user: {e}")

    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)

    def log_message(self, message):
        """Add message to log"""
        self.log_queue.put(message)

    def process_log_queue(self):
        """Process log queue and update UI"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state='normal')
                timestamp = datetime.now().strftime('%H:%M:%S')
                self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
                self.log_text.see(tk.END)
                self.log_text.config(state='disabled')
        except queue.Empty:
            pass

        self.root.after(100, self.process_log_queue)

    def clear_log(self):
        """Clear the log text"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

    def validate_inputs(self):
        """Validate user inputs"""
        if not self.username_var.get():
            messagebox.showerror("Validation Error", "Please enter a Windows username")
            return False

        if not self.output_dir_var.get():
            messagebox.showerror("Validation Error", "Please select an output directory")
            return False

        # Check if any extraction option is selected
        if not any([self.extract_local_var.get(), self.extract_email_var.get(),
                   self.extract_browser_var.get()]):
            messagebox.showerror("Validation Error", "Please select at least one extraction option")
            return False

        return True

    def start_extraction(self):
        """Start the extraction process"""
        if not self.validate_inputs():
            return

        # Confirm before starting
        email_info = f" ({self.email_var.get()})" if self.email_var.get() else ""
        if not messagebox.askyesno("Confirm Extraction",
                                   f"Start data extraction for:\n\n"
                                   f"User: {self.username_var.get()}{email_info}\n\n"
                                   f"This may take several minutes depending on data size.\n\n"
                                   f"Continue?"):
            return

        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress_bar.start()

        self.log_message("="*60)
        self.log_message("Starting LOCAL data extraction...")
        self.log_message(f"Target user: {self.username_var.get()}{email_info}")
        self.log_message(f"Output directory: {self.output_dir_var.get()}")
        self.log_message("="*60)

        # Start extraction in separate thread
        extraction_thread = threading.Thread(target=self.run_extraction, daemon=True)
        extraction_thread.start()

    def run_extraction(self):
        """Run the extraction process (in separate thread)"""
        try:
            # Import extraction modules
            from local_extractor import LocalDataExtractor
            from email_extractor import EmailArchiveExtractor
            from browser_extractor import BrowserDataExtractor
            from archiver import DataArchiver

            # Get configuration
            config = self.get_default_config()

            username = self.username_var.get()
            email = self.email_var.get() or f"{username}@unknown.com"
            output_dir = Path(self.output_dir_var.get())

            # Create timestamped output directory
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = output_dir / f"{username}_{timestamp}"
            output_path.mkdir(parents=True, exist_ok=True)

            stats = {}
            start_time = datetime.now()

            # Local extraction
            if self.extract_local_var.get():
                self.log_message("\n--- Local File System Extraction ---")
                extractor = LocalDataExtractor(config, output_path)
                stats['local'] = extractor.extract_all(username)
                self.log_message(f"✓ Local files: {stats['local'].get('files_copied', 0)} files copied")

            if self.extract_email_var.get():
                self.log_message("\n--- Email Archives Extraction ---")
                email_extractor = EmailArchiveExtractor(config, output_path)
                stats['email'] = email_extractor.extract_all(username)
                self.log_message(f"✓ Email archives: {stats['email'].get('pst_files', 0)} PST, "
                               f"{stats['email'].get('ost_files', 0)} OST files found")

            if self.extract_browser_var.get():
                self.log_message("\n--- Browser Data Extraction ---")
                browser_extractor = BrowserDataExtractor(config, output_path)
                stats['browser'] = browser_extractor.extract_all(username)
                self.log_message(f"✓ Browser data: {stats['browser'].get('profiles_extracted', 0)} profiles extracted")

            # Generate report
            self.log_message("\n--- Generating Report ---")
            duration = (datetime.now() - start_time).total_seconds()
            archiver = DataArchiver(config)
            report_path = archiver.generate_report(username, email, output_path, stats, duration)
            self.log_message(f"✓ Report generated: {report_path.name}")

            # Create archive
            if self.create_archive_var.get():
                self.log_message("\n--- Creating Archive ---")
                archive_name = f"{username}_{timestamp}.zip"
                archive_path = output_dir / archive_name
                password = config.get('extraction', {}).get('archive_password', '')

                success = archiver.create_archive(output_path, archive_path, password or None)
                if success:
                    self.log_message(f"✓ Archive created: {archive_name}")
                    if password:
                        self.log_message("  (Password-protected)")

            self.log_message("\n" + "="*60)
            self.log_message("EXTRACTION COMPLETED SUCCESSFULLY!")
            self.log_message(f"Output location: {output_path}")
            self.log_message("="*60)

            # Show completion message
            self.root.after(0, lambda: messagebox.showinfo(
                "Extraction Complete",
                f"Data extraction completed successfully!\n\n"
                f"Output location:\n{output_path}\n\n"
                f"Please review the extraction report for details."
            ))

        except Exception as e:
            error_msg = f"Extraction failed: {e}"
            self.log_message(f"\n✗ ERROR: {error_msg}")
            logger.error(error_msg, exc_info=True)
            self.root.after(0, lambda: messagebox.showerror("Extraction Error", error_msg))

        finally:
            self.root.after(0, self.extraction_complete)

    def get_default_config(self):
        """Get default configuration"""
        return {
            'extraction': {
                'output_dir': str(Path.home() / 'Desktop' / 'Extracted_Data'),
                'use_timestamps': True,
                'create_archive': True,
                'archive_password': '',  # Set a default password here if desired
                'max_file_size_mb': 0,
                'skip_extensions': ['.tmp', '.temp', '.cache']
            },
            'local_extraction': {
                'include_desktop': True,
                'include_documents': True,
                'include_downloads': True,
                'include_appdata': True,
                'include_email_archives': True,
                'include_browser_data': True,
                'browsers': ['chrome', 'edge', 'firefox']
            },
            'logging': {
                'level': 'INFO',
                'log_to_file': True,
                'log_file': './logs/extraction.log'
            }
        }

    def stop_extraction(self):
        """Stop the extraction process"""
        if messagebox.askyesno("Cancel Extraction", "Are you sure you want to cancel the extraction?"):
            self.is_running = False
            self.log_message("\n⚠ Extraction cancelled by user")
            self.extraction_complete()

    def extraction_complete(self):
        """Cleanup after extraction completes"""
        self.progress_bar.stop()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.is_running = False


def main():
    """Main entry point"""
    root = tk.Tk()
    app = SaveItScottyGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
