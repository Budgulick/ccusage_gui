"""
GUI interface for Mr. The Guru - Claude Code Usage

Main application window and GUI components.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import logging

from .config import ConfigManager
from .data_loader import DataLoader
from .cost_calculator import CostCalculator
from .reports import ReportGenerator
from .utils import format_currency, format_number, setup_logging

logger = logging.getLogger(__name__)


class MainApplication:
    """
    Main application window for Mr. The Guru - Claude Code Usage.

    Provides GUI interface for:
    - Loading Claude Code usage data
    - Generating various report types
    - Filtering and sorting data
    - Exporting reports
    - Configuration management
    """

    def __init__(self, root: tk.Tk, config_manager: ConfigManager):
        """
        Initialize the main application.

        Args:
            root: Tkinter root window
            config_manager: Configuration manager instance
        """
        self.root = root
        self.config_manager = config_manager
        self.data_loader: Optional[DataLoader] = None
        self.cost_calculator: Optional[CostCalculator] = None
        self.report_generator: Optional[ReportGenerator] = None

        # Setup logging
        setup_logging("INFO")

        # Initialize components
        self._setup_data_components()
        self._setup_gui()
        self._load_initial_data()

    def _setup_data_components(self):
        """Initialize data processing components."""
        try:
            # Get Claude data paths from config
            data_paths = self.config_manager.get_claude_data_paths()
            self.data_loader = DataLoader(data_paths)

            # Initialize cost calculator
            cost_config = self.config_manager.config.cost
            self.cost_calculator = CostCalculator(
                mode=cost_config.mode,
                offline=cost_config.offline_mode,
                currency=cost_config.currency
            )

            # Initialize report generator
            self.report_generator = ReportGenerator(self.cost_calculator)

            logger.info("Data components initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing data components: {e}")
            messagebox.showerror("Initialization Error",
                               f"Failed to initialize data components:\n{e}")

    def _setup_gui(self):
        """Setup the main GUI interface."""
        # Configure style
        style = ttk.Style()
        style.theme_use('winnative')  # Windows native theme

        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Setup menu
        self._setup_menu()

        # Setup toolbar
        self._setup_toolbar()

        # Setup main content area
        self._setup_content_area()

        # Setup status bar
        self._setup_status_bar()

    def _setup_menu(self):
        """Setup the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh Data", command=self._refresh_data)
        file_menu.add_separator()
        file_menu.add_command(label="Export JSON...", command=self._export_json)
        file_menu.add_command(label="Export CSV...", command=self._export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Daily Report", command=lambda: self._switch_report("daily"))
        view_menu.add_command(label="Monthly Report", command=lambda: self._switch_report("monthly"))
        view_menu.add_command(label="Weekly Report", command=lambda: self._switch_report("weekly"))
        view_menu.add_command(label="Session Report", command=lambda: self._switch_report("session"))
        view_menu.add_command(label="Blocks Report", command=lambda: self._switch_report("blocks"))

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Update Pricing", command=self._update_pricing)
        tools_menu.add_command(label="Settings...", command=self._show_settings)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="View Documentation", command=self._show_documentation)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)

    def _setup_toolbar(self):
        """Setup the toolbar."""
        toolbar_frame = ttk.Frame(self.main_frame)
        toolbar_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Report type selection
        ttk.Label(toolbar_frame, text="Report Type:").grid(row=0, column=0, padx=(0, 5))

        self.report_type_var = tk.StringVar(value="daily")
        report_combo = ttk.Combobox(toolbar_frame, textvariable=self.report_type_var,
                                  values=["daily", "monthly", "weekly", "session", "blocks"],
                                  state="readonly", width=10)
        report_combo.grid(row=0, column=1, padx=(0, 20))
        report_combo.bind('<<ComboboxSelected>>', self._on_report_type_changed)

        # Date range filters
        ttk.Label(toolbar_frame, text="From:").grid(row=0, column=2, padx=(0, 5))
        self.start_date_var = tk.StringVar()
        start_date_entry = ttk.Entry(toolbar_frame, textvariable=self.start_date_var, width=12)
        start_date_entry.grid(row=0, column=3, padx=(0, 10))

        ttk.Label(toolbar_frame, text="To:").grid(row=0, column=4, padx=(0, 5))
        self.end_date_var = tk.StringVar()
        end_date_entry = ttk.Entry(toolbar_frame, textvariable=self.end_date_var, width=12)
        end_date_entry.grid(row=0, column=5, padx=(0, 20))

        # Filter and refresh buttons
        ttk.Button(toolbar_frame, text="Apply Filters", command=self._apply_filters).grid(row=0, column=6, padx=(0, 10))
        ttk.Button(toolbar_frame, text="Clear Filters", command=self._clear_filters).grid(row=0, column=7, padx=(0, 10))
        ttk.Button(toolbar_frame, text="Refresh", command=self._refresh_data).grid(row=0, column=8)

    def _setup_content_area(self):
        """Setup the main content area."""
        # Create notebook for different views
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Report view tab
        self.report_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.report_frame, text="Report")

        # Setup report table
        self._setup_report_table()

        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")

        # Setup summary view
        self._setup_summary_view()

    def _setup_report_table(self):
        """Setup the report data table."""
        # Table frame with scrollbars
        table_frame = ttk.Frame(self.report_frame)
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Treeview for report data
        columns = ('date', 'tokens', 'input', 'output', 'cache_creation', 'cache_read', 'cost')
        self.report_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # Configure columns
        self.report_tree.heading('date', text='Date')
        self.report_tree.heading('tokens', text='Total Tokens')
        self.report_tree.heading('input', text='Input Tokens')
        self.report_tree.heading('output', text='Output Tokens')
        self.report_tree.heading('cache_creation', text='Cache Creation')
        self.report_tree.heading('cache_read', text='Cache Read')
        self.report_tree.heading('cost', text='Cost (USD)')

        # Configure column widths
        self.report_tree.column('date', width=100)
        self.report_tree.column('tokens', width=100)
        self.report_tree.column('input', width=100)
        self.report_tree.column('output', width=100)
        self.report_tree.column('cache_creation', width=100)
        self.report_tree.column('cache_read', width=100)
        self.report_tree.column('cost', width=100)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.report_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.report_tree.xview)
        self.report_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout
        self.report_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Configure grid weights
        self.report_frame.columnconfigure(0, weight=1)
        self.report_frame.rowconfigure(0, weight=1)

    def _setup_summary_view(self):
        """Setup the summary view."""
        # Summary labels
        self.summary_labels = {}

        row = 0
        for label, key in [
            ("Total Records:", "total_records"),
            ("Date Range:", "date_range"),
            ("Total Tokens:", "total_tokens"),
            ("Total Cost:", "total_cost"),
            ("Average Cost per Day:", "avg_daily_cost"),
            ("Most Used Model:", "top_model")
        ]:
            ttk.Label(self.summary_frame, text=label, font=('TkDefaultFont', 9, 'bold')).grid(
                row=row, column=0, sticky=tk.W, padx=10, pady=5)

            value_label = ttk.Label(self.summary_frame, text="Loading...")
            value_label.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
            self.summary_labels[key] = value_label

            row += 1

    def _setup_status_bar(self):
        """Setup the status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

    def _load_initial_data(self):
        """Load initial data in background thread."""
        def load_data():
            try:
                self.status_var.set("Loading Claude Code usage data...")
                self.root.update()

                if self.data_loader:
                    records = self.data_loader.load_usage_data()
                    logger.info(f"Loaded {len(records)} usage records")

                    # Update UI in main thread
                    self.root.after(0, self._on_data_loaded, records)

            except Exception as e:
                logger.error(f"Error loading data: {e}")
                self.root.after(0, self._on_data_load_error, str(e))

        # Start loading in background
        thread = threading.Thread(target=load_data, daemon=True)
        thread.start()

    def _on_data_loaded(self, records):
        """Handle successful data loading."""
        self.status_var.set(f"Loaded {len(records)} usage records")
        self._update_summary(records)
        self._generate_current_report()

    def _on_data_load_error(self, error_message):
        """Handle data loading error."""
        self.status_var.set("Error loading data")
        messagebox.showerror("Data Load Error", f"Failed to load usage data:\n{error_message}")

    def _generate_current_report(self):
        """Generate report based on current settings."""
        if not self.report_generator or not self.data_loader:
            return

        try:
            self.status_var.set("Generating report...")
            self.root.update()

            # Get all records
            records = self.data_loader.load_usage_data()

            # Apply date filters
            start_date = self._parse_date(self.start_date_var.get())
            end_date = self._parse_date(self.end_date_var.get())

            # Generate report based on type
            report_type = self.report_type_var.get()

            if report_type == "daily":
                report_data = self.report_generator.generate_daily_report(records, start_date, end_date)
            elif report_type == "monthly":
                report_data = self.report_generator.generate_monthly_report(records, start_date, end_date)
            elif report_type == "weekly":
                report_data = self.report_generator.generate_weekly_report(records, start_date, end_date)
            elif report_type == "session":
                report_data = self.report_generator.generate_session_report(records, start_date, end_date)
            elif report_type == "blocks":
                report_data = self.report_generator.generate_blocks_report(records, start_date, end_date)
            else:
                report_data = []

            # Update table
            self._update_report_table(report_data, report_type)

            self.status_var.set(f"Generated {report_type} report with {len(report_data)} entries")

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            self.status_var.set("Error generating report")
            messagebox.showerror("Report Error", f"Failed to generate report:\n{e}")

    def _update_report_table(self, report_data, report_type):
        """Update the report table with new data."""
        # Clear existing data
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        # Update column headers based on report type
        if report_type == "session":
            self.report_tree.heading('date', text='Session ID')
            self.report_tree.heading('tokens', text='Duration (min)')
        elif report_type == "blocks":
            self.report_tree.heading('date', text='Block Start')
            self.report_tree.heading('tokens', text='Sessions')
        else:
            self.report_tree.heading('date', text='Date')
            self.report_tree.heading('tokens', text='Total Tokens')

        # Add new data
        for entry in report_data:
            if report_type == "session":
                values = (
                    entry.session_id[:16] + "..." if len(entry.session_id) > 16 else entry.session_id,
                    f"{entry.duration_minutes:.1f}",
                    format_number(entry.input_tokens),
                    format_number(entry.output_tokens),
                    format_number(entry.cache_creation_tokens),
                    format_number(entry.cache_read_tokens),
                    format_currency(entry.total_cost)
                )
            elif report_type == "blocks":
                values = (
                    entry.block_start.strftime('%m/%d %H:%M'),
                    str(entry.sessions_count),
                    format_number(entry.input_tokens),
                    format_number(entry.output_tokens),
                    format_number(entry.cache_creation_tokens),
                    format_number(entry.cache_read_tokens),
                    format_currency(entry.total_cost)
                )
            else:
                values = (
                    entry.date.strftime('%Y-%m-%d'),
                    format_number(entry.total_tokens),
                    format_number(entry.input_tokens),
                    format_number(entry.output_tokens),
                    format_number(entry.cache_creation_tokens),
                    format_number(entry.cache_read_tokens),
                    format_currency(entry.total_cost)
                )

            self.report_tree.insert('', 'end', values=values)

    def _update_summary(self, records):
        """Update the summary view with statistics."""
        if not records:
            for label in self.summary_labels.values():
                label.config(text="No data")
            return

        try:
            # Calculate summary statistics
            total_records = len(records)

            # Date range
            timestamps = [r.timestamp for r in records]
            start_date = min(timestamps)
            end_date = max(timestamps)
            date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

            # Token totals
            total_tokens = sum(r.total_tokens for r in records)

            # Cost calculation
            if self.cost_calculator:
                cost_breakdown = self.cost_calculator.calculate_total_cost(records)
                total_cost = cost_breakdown['total_cost']

                # Average daily cost
                days = (end_date - start_date).days + 1
                avg_daily_cost = total_cost / max(days, 1)
            else:
                total_cost = 0.0
                avg_daily_cost = 0.0

            # Most used model
            model_counts = {}
            for r in records:
                model_counts[r.model] = model_counts.get(r.model, 0) + 1
            top_model = max(model_counts.items(), key=lambda x: x[1])[0] if model_counts else "None"

            # Update labels
            self.summary_labels["total_records"].config(text=format_number(total_records))
            self.summary_labels["date_range"].config(text=date_range)
            self.summary_labels["total_tokens"].config(text=format_number(total_tokens))
            self.summary_labels["total_cost"].config(text=format_currency(total_cost))
            self.summary_labels["avg_daily_cost"].config(text=format_currency(avg_daily_cost))
            self.summary_labels["top_model"].config(text=top_model)

        except Exception as e:
            logger.error(f"Error updating summary: {e}")
            for label in self.summary_labels.values():
                label.config(text="Error")

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in YYYY-MM-DD format."""
        if not date_str.strip():
            return None

        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d')
        except ValueError:
            return None

    # Event handlers
    def _on_report_type_changed(self, event):
        """Handle report type selection change."""
        self._generate_current_report()

    def _apply_filters(self):
        """Apply date filters and regenerate report."""
        self._generate_current_report()

    def _clear_filters(self):
        """Clear all filters."""
        self.start_date_var.set("")
        self.end_date_var.set("")
        self._generate_current_report()

    def _refresh_data(self):
        """Refresh data from files."""
        if self.data_loader:
            self.data_loader.clear_cache()
            self._load_initial_data()

    def _switch_report(self, report_type: str):
        """Switch to a different report type."""
        self.report_type_var.set(report_type)
        self._generate_current_report()

    def _export_json(self):
        """Export current report to JSON."""
        # Implementation placeholder
        messagebox.showinfo("Export", "JSON export functionality will be implemented in next phase")

    def _export_csv(self):
        """Export current report to CSV."""
        # Implementation placeholder
        messagebox.showinfo("Export", "CSV export functionality will be implemented in next phase")

    def _update_pricing(self):
        """Update pricing data."""
        if self.cost_calculator:
            success = self.cost_calculator.update_pricing(force=True)
            if success:
                messagebox.showinfo("Pricing Update", "Pricing data updated successfully")
                self._generate_current_report()  # Refresh with new pricing
            else:
                messagebox.showerror("Pricing Update", "Failed to update pricing data")

    def _show_settings(self):
        """Show settings dialog."""
        # Implementation placeholder
        messagebox.showinfo("Settings", "Settings dialog will be implemented in next phase")

    def _show_documentation(self):
        """Show documentation in a new window."""
        # Check if README.md exists
        readme_path = Path.cwd() / "README.md"
        if not readme_path.exists():
            messagebox.showerror("Documentation", "README.md file not found")
            return

        # Create documentation window
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Mr. The Guru - Claude Code Usage - Documentation")
        doc_window.geometry("800x600")

        # Set icon if available
        icon_path = Path.cwd() / "assets" / "mrtheguru_icon_main.ico"
        if icon_path.exists():
            try:
                doc_window.iconbitmap(str(icon_path))
            except Exception:
                pass

        # Create text widget with scrollbar
        frame = ttk.Frame(doc_window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        text_widget = tk.Text(frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Configure grid weights
        doc_window.columnconfigure(0, weight=1)
        doc_window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Load and display README content
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            text_widget.insert('1.0', content)
            text_widget.config(state='disabled')  # Make read-only
        except Exception as e:
            text_widget.insert('1.0', f"Error loading documentation: {e}")

    def _show_about(self):
        """Show about dialog."""
        about_text = """Mr. The Guru - Claude Code Usage v1.0.0

A Windows GUI application for analyzing Claude Code usage data.

Based on the original ccusage CLI tool by @ryoppippi.

Features:
• Daily, Monthly, Weekly, Session, and Blocks reports
• Token usage analysis and cost calculation
• Export to JSON and CSV formats
• Real-time pricing updates
• User-friendly Windows interface

© 2024 - Licensed under MIT License"""

        messagebox.showinfo("About", about_text)