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


class ModernTheme:
    """Modern purple gradient theme matching the HTML dashboard template."""

    # Color Palette - Purple Gradient Theme
    BACKGROUND_PRIMARY = "#f5f7fa"      # Light blue-gray background
    BACKGROUND_SECONDARY = "#ffffff"     # White cards/panels
    BACKGROUND_ACCENT = "#f9fafb"       # Very light gray for alternating rows

    # Gradient Colors
    GRADIENT_START = "#667eea"          # Purple gradient start
    GRADIENT_END = "#764ba2"            # Purple gradient end
    PRIMARY_PURPLE = "#667eea"          # Main purple for primary actions
    PRIMARY_PURPLE_HOVER = "#5a67d8"    # Darker purple for hover
    PRIMARY_PURPLE_PRESSED = "#4c51bf"  # Even darker for pressed

    # Border Colors
    BORDER_LIGHT = "#e5e7eb"            # Light borders
    BORDER_MEDIUM = "#d1d5db"           # Medium borders
    BORDER_FOCUS = "#667eea"            # Focus state borders

    # Text Colors
    TEXT_PRIMARY = "#1f2937"            # Main text color (darker)
    TEXT_SECONDARY = "#6b7280"          # Secondary text
    TEXT_DISABLED = "#9ca3af"           # Disabled text
    TEXT_WHITE = "#ffffff"              # White text for gradients

    # Status Colors
    SUCCESS_GREEN = "#10b981"           # Success states
    SUCCESS_LIGHT = "#d1fae5"           # Success background
    SUCCESS_DARK = "#065f46"            # Success text
    WARNING_ORANGE = "#ff8c00"          # Warning states
    ERROR_RED = "#dc2626"               # Error states
    ERROR_LIGHT = "#fee2e2"             # Error background
    ERROR_DARK = "#991b1b"              # Error text

    # Icon Background Colors
    ICON_BLUE_BG = "#e6f2ff"
    ICON_BLUE_FG = "#0066cc"
    ICON_GREEN_BG = "#e6f9f0"
    ICON_GREEN_FG = "#00b359"
    ICON_PURPLE_BG = "#f0e6ff"
    ICON_PURPLE_FG = "#7c3aed"
    ICON_ORANGE_BG = "#fff4e6"
    ICON_ORANGE_FG = "#ff8c00"

    # Spacing (more generous for modern look)
    PADDING_XS = 4
    PADDING_SM = 8
    PADDING_MD = 16
    PADDING_LG = 24
    PADDING_XL = 32
    PADDING_XXL = 48

    # Typography (larger sizes for dashboard)
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_CAPTION = 11
    FONT_SIZE_SM = 12
    FONT_SIZE_MD = 14
    FONT_SIZE_LG = 16
    FONT_SIZE_XL = 18
    FONT_SIZE_XXL = 20
    FONT_SIZE_STAT = 32          # Large stats values
    FONT_SIZE_HEADER = 28        # Header title

    # Card styling
    CARD_RADIUS = 12
    CARD_SHADOW_COLOR = "#e5e7eb"
    CARD_HOVER_OFFSET = 4


class ModernFrame(tk.Frame):
    """Modern styled frame with card appearance."""

    def __init__(self, parent, **kwargs):
        # Extract custom options
        card_style = kwargs.pop('card_style', True)
        padding = kwargs.pop('padding', ModernTheme.PADDING_MD)

        # Set default styling
        kwargs.setdefault('bg', ModernTheme.BACKGROUND_SECONDARY)
        kwargs.setdefault('relief', 'flat')
        kwargs.setdefault('bd', 1)

        super().__init__(parent, **kwargs)

        if card_style:
            self.configure(
                highlightbackground=ModernTheme.BORDER_LIGHT,
                highlightthickness=1,
                relief='solid'
            )

        # Apply padding using grid
        if padding:
            self.grid_configure(padx=padding, pady=padding)


class ModernButton(tk.Button):
    """Modern styled button with hover effects and gradient support."""

    def __init__(self, parent, **kwargs):
        # Extract button style
        style = kwargs.pop('style', 'primary')  # primary, secondary, outline

        # Configure based on style
        if style == 'primary':
            kwargs.setdefault('bg', ModernTheme.PRIMARY_PURPLE)
            kwargs.setdefault('fg', ModernTheme.TEXT_WHITE)
            kwargs.setdefault('activebackground', ModernTheme.PRIMARY_PURPLE_HOVER)
            kwargs.setdefault('activeforeground', ModernTheme.TEXT_WHITE)
        elif style == 'secondary':
            kwargs.setdefault('bg', ModernTheme.BACKGROUND_ACCENT)
            kwargs.setdefault('fg', ModernTheme.TEXT_SECONDARY)
            kwargs.setdefault('activebackground', ModernTheme.BORDER_LIGHT)
        elif style == 'outline':
            kwargs.setdefault('bg', ModernTheme.BACKGROUND_SECONDARY)
            kwargs.setdefault('fg', ModernTheme.PRIMARY_PURPLE)
            kwargs.setdefault('activebackground', ModernTheme.BACKGROUND_ACCENT)

        # Modern styling with rounded appearance
        kwargs.setdefault('font', (ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD, 'bold'))
        kwargs.setdefault('relief', 'flat')
        kwargs.setdefault('bd', 0)
        kwargs.setdefault('highlightthickness', 0)
        kwargs.setdefault('padx', 20)
        kwargs.setdefault('pady', 10)
        kwargs.setdefault('cursor', 'hand2')

        super().__init__(parent, **kwargs)

        # Add hover effects
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

        # Store original colors
        self.original_bg = self['bg']
        self.hover_bg = self['activebackground']

    def _on_enter(self, event):
        self.configure(bg=self.hover_bg)
        # Add slight elevation effect
        self.configure(relief='raised', bd=1)

    def _on_leave(self, event):
        self.configure(bg=self.original_bg)
        self.configure(relief='flat', bd=0)


class ModernLabel(tk.Label):
    """Modern styled label with typography hierarchy."""

    def __init__(self, parent, **kwargs):
        # Extract typography level
        level = kwargs.pop('level', 'body')  # heading, subheading, body, caption

        # Configure typography
        if level == 'heading':
            kwargs.setdefault('font', (ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_HEADER, 'bold'))
            kwargs.setdefault('fg', ModernTheme.TEXT_WHITE)  # For gradient backgrounds
        elif level == 'subheading':
            kwargs.setdefault('font', (ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_LG, 'bold'))
            kwargs.setdefault('fg', ModernTheme.TEXT_PRIMARY)
        elif level == 'body':
            kwargs.setdefault('font', (ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD))
            kwargs.setdefault('fg', ModernTheme.TEXT_PRIMARY)
        elif level == 'caption':
            kwargs.setdefault('font', (ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SM))
            kwargs.setdefault('fg', ModernTheme.TEXT_SECONDARY)

        # Common styling
        kwargs.setdefault('bg', ModernTheme.BACKGROUND_PRIMARY)

        super().__init__(parent, **kwargs)


class EmptyStateWidget(ModernFrame):
    """Modern empty state with icon, title, description and actions."""

    def __init__(self, parent, title="No Data Available",
                 description="There's nothing to show here yet.",
                 action_text="Refresh Data", action_command=None, **kwargs):

        super().__init__(parent, card_style=False, **kwargs)

        # Configure the frame
        self.configure(bg=ModernTheme.BACKGROUND_SECONDARY)

        # Create content container
        content_frame = tk.Frame(self, bg=ModernTheme.BACKGROUND_SECONDARY)
        content_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Empty state icon (using text for now, could be image)
        icon_label = ModernLabel(
            content_frame,
            text="📊",  # Data icon
            font=(ModernTheme.FONT_FAMILY, 32),
            bg=ModernTheme.BACKGROUND_SECONDARY
        )
        icon_label.pack(pady=(0, ModernTheme.PADDING_MD))

        # Title
        title_label = ModernLabel(
            content_frame,
            text=title,
            level='heading',
            bg=ModernTheme.BACKGROUND_SECONDARY
        )
        title_label.pack(pady=(0, ModernTheme.PADDING_SM))

        # Description
        desc_label = ModernLabel(
            content_frame,
            text=description,
            level='caption',
            bg=ModernTheme.BACKGROUND_SECONDARY,
            wraplength=400,
            justify='center'
        )
        desc_label.pack(pady=(0, ModernTheme.PADDING_LG))

        # Action button
        if action_command:
            action_btn = ModernButton(
                content_frame,
                text=action_text,
                command=action_command,
                style='primary'
            )
            action_btn.pack()


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
        """Setup the modern dashboard interface with purple gradient theme."""
        # Set main window background
        self.root.configure(bg=ModernTheme.BACKGROUND_PRIMARY)

        # Apply modern treeview styling
        self._setup_modern_treeview_style()

        # Create scrollable canvas container
        canvas_container = tk.Frame(self.root, bg=ModernTheme.BACKGROUND_PRIMARY)
        canvas_container.pack(fill='both', expand=True)

        # Canvas for scrolling
        self.main_canvas = tk.Canvas(canvas_container, bg=ModernTheme.BACKGROUND_PRIMARY, highlightthickness=0)
        self.main_canvas.pack(side='left', fill='both', expand=True)

        # Scrollbar for canvas
        scrollbar = ttk.Scrollbar(canvas_container, orient='vertical', command=self.main_canvas.yview)
        scrollbar.pack(side='right', fill='y')

        self.main_canvas.configure(yscrollcommand=scrollbar.set)

        # Main container (direct content holder for canvas)
        self.main_frame = tk.Frame(
            self.main_canvas,
            bg=ModernTheme.BACKGROUND_PRIMARY
        )
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.main_frame, anchor='nw')

        # Configure scrolling
        def _on_frame_configure(event):
            """Reset scroll region when frame size changes."""
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox('all'))

        def _on_canvas_configure(event):
            """Resize frame when canvas size changes."""
            canvas_width = event.width
            self.main_canvas.itemconfig(self.canvas_window, width=canvas_width)

        self.main_frame.bind('<Configure>', _on_frame_configure)
        self.main_canvas.bind('<Configure>', _on_canvas_configure)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')

        self.main_canvas.bind_all('<MouseWheel>', _on_mousewheel)

        # Add padding to frame content (this is what components will attach to)
        self.main_frame_inner = tk.Frame(self.main_frame, bg=ModernTheme.BACKGROUND_PRIMARY)
        self.main_frame_inner.pack(fill='both', expand=True, padx=20, pady=20)

        # Setup menu
        self._setup_menu()

        # Setup dashboard components (use main_frame_inner instead of main_frame)
        self._setup_modern_status_bar()  # Initialize status_var first
        self._setup_gradient_header()
        self._setup_stats_cards()
        self._setup_dashboard_controls()
        self._setup_charts_section()
        self._setup_modern_content_area()
        self._setup_footer_section()

    def _setup_gradient_header(self):
        """Setup the gradient header matching HTML template."""
        # Create gradient header frame
        header_container = tk.Frame(self.main_frame_inner, bg=ModernTheme.BACKGROUND_PRIMARY)
        header_container.pack(fill='x', pady=(0, ModernTheme.PADDING_XL))

        # Gradient background frame
        gradient_header = GradientFrame(
            header_container,
            ModernTheme.GRADIENT_START,
            ModernTheme.GRADIENT_END,
            height=120
        )
        gradient_header.pack(fill='x')

        # Add content to gradient header
        header_content = tk.Frame(gradient_header.canvas, bg=ModernTheme.GRADIENT_START)
        gradient_header.canvas.create_window(0, 0, anchor='nw', window=header_content)

        # Configure header content to fill canvas
        def configure_header_content(event):
            gradient_header.canvas.configure(scrollregion=gradient_header.canvas.bbox("all"))
            canvas_width = gradient_header.canvas.winfo_width()
            gradient_header.canvas.itemconfig(
                gradient_header.canvas.find_all()[0], width=canvas_width
            )
        gradient_header.canvas.bind('<Configure>', configure_header_content)

        # Header title
        title_label = tk.Label(
            header_content,
            text="Mr. The Guru - Claude Code Usage Dashboard",
            bg=ModernTheme.GRADIENT_START,
            fg=ModernTheme.TEXT_WHITE,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_HEADER, 'bold')
        )
        title_label.pack(side='left', padx=ModernTheme.PADDING_XL, pady=ModernTheme.PADDING_XL)

        # Subtitle
        subtitle_label = tk.Label(
            header_content,
            text="Track your token usage and costs across all Claude models",
            bg=ModernTheme.GRADIENT_START,
            fg=ModernTheme.TEXT_WHITE,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD),
            justify='left'
        )
        subtitle_label.pack(side='left', padx=(0, ModernTheme.PADDING_XL), pady=(ModernTheme.PADDING_XL + 40, ModernTheme.PADDING_XL))

    def _setup_stats_cards(self):
        """Setup the statistics cards grid."""
        # Stats grid container
        stats_container = tk.Frame(self.main_frame_inner, bg=ModernTheme.BACKGROUND_PRIMARY)
        stats_container.pack(fill='x', pady=(0, ModernTheme.PADDING_XL))

        # Create 4 stats cards in a grid
        self.stats_cards = {}

        # Card 1: Total Tokens
        card1 = StatsCard(
            stats_container,
            title="Total Tokens",
            value="0",
            detail="Last 30 days",
            icon="📊",
            trend="+0%",
            icon_color="blue"
        )
        card1.grid(row=0, column=0, sticky='ew', padx=(0, 10), pady=10)
        self.stats_cards['tokens'] = card1

        # Card 2: Total Cost
        card2 = StatsCard(
            stats_container,
            title="Total Cost",
            value="$0.00",
            detail="Avg: $0.00/day",
            icon="💰",
            trend="+0%",
            icon_color="green"
        )
        card2.grid(row=0, column=1, sticky='ew', padx=5, pady=10)
        self.stats_cards['cost'] = card2

        # Card 3: Total Sessions
        card3 = StatsCard(
            stats_container,
            title="Total Sessions",
            value="0",
            detail="This month",
            icon="📅",
            trend="+0",
            icon_color="purple"
        )
        card3.grid(row=0, column=2, sticky='ew', padx=5, pady=10)
        self.stats_cards['sessions'] = card3

        # Card 4: Cache Hit Rate
        card4 = StatsCard(
            stats_container,
            title="Cache Hit Rate",
            value="0%",
            detail="Saved $0.00",
            icon="⚡",
            trend="+0%",
            icon_color="orange"
        )
        card4.grid(row=0, column=3, sticky='ew', padx=(10, 0), pady=10)
        self.stats_cards['cache'] = card4

        # Configure grid weights for responsive layout
        for i in range(4):
            stats_container.columnconfigure(i, weight=1)

    def _setup_dashboard_controls(self):
        """Setup modern controls section."""
        # Controls card
        controls_card = ModernFrame(self.main_frame_inner, padding=0)
        controls_card.pack(fill='x', pady=(0, ModernTheme.PADDING_XL))

        # Controls content
        controls_content = tk.Frame(controls_card, bg=ModernTheme.BACKGROUND_SECONDARY)
        controls_content.pack(fill='x', padx=ModernTheme.PADDING_LG, pady=ModernTheme.PADDING_LG)

        # Create grid layout for controls
        controls_grid = tk.Frame(controls_content, bg=ModernTheme.BACKGROUND_SECONDARY)
        controls_grid.pack(fill='x')

        # Report type control
        report_frame = tk.Frame(controls_grid, bg=ModernTheme.BACKGROUND_SECONDARY)
        report_frame.grid(row=0, column=0, sticky='w', padx=(0, 20))

        tk.Label(
            report_frame,
            text="Report Type",
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.TEXT_SECONDARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SM, 'bold')
        ).pack(anchor='w', pady=(0, 8))

        self.report_type_var = tk.StringVar(value="daily")
        report_combo = ttk.Combobox(
            report_frame,
            textvariable=self.report_type_var,
            values=["daily", "monthly", "weekly", "session", "blocks"],
            state="readonly",
            width=15,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD)
        )
        report_combo.pack()
        report_combo.bind('<<ComboboxSelected>>', self._on_report_type_changed)

        # Date controls
        date_frame = tk.Frame(controls_grid, bg=ModernTheme.BACKGROUND_SECONDARY)
        date_frame.grid(row=0, column=1, sticky='w', padx=(0, 20))

        tk.Label(
            date_frame,
            text="Start Date",
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.TEXT_SECONDARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SM, 'bold')
        ).pack(anchor='w', pady=(0, 8))

        self.start_date_var = tk.StringVar()
        start_date_entry = tk.Entry(
            date_frame,
            textvariable=self.start_date_var,
            width=12,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor=ModernTheme.BORDER_FOCUS
        )
        start_date_entry.pack()

        # End date
        end_date_frame = tk.Frame(controls_grid, bg=ModernTheme.BACKGROUND_SECONDARY)
        end_date_frame.grid(row=0, column=2, sticky='w', padx=(0, 20))

        tk.Label(
            end_date_frame,
            text="End Date",
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.TEXT_SECONDARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SM, 'bold')
        ).pack(anchor='w', pady=(0, 8))

        self.end_date_var = tk.StringVar()
        end_date_entry = tk.Entry(
            end_date_frame,
            textvariable=self.end_date_var,
            width=12,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor=ModernTheme.BORDER_FOCUS
        )
        end_date_entry.pack()

        # Action buttons
        buttons_frame = tk.Frame(controls_grid, bg=ModernTheme.BACKGROUND_SECONDARY)
        buttons_frame.grid(row=0, column=3, sticky='w')

        tk.Label(
            buttons_frame,
            text=" ",  # Empty label for spacing
            bg=ModernTheme.BACKGROUND_SECONDARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SM)
        ).pack(pady=(0, 8))

        button_container = tk.Frame(buttons_frame, bg=ModernTheme.BACKGROUND_SECONDARY)
        button_container.pack()

        ModernButton(
            button_container,
            text="Apply Filters",
            command=self._apply_filters,
            style='primary'
        ).pack(side='left', padx=(0, 10))

        ModernButton(
            button_container,
            text="Clear",
            command=self._clear_filters,
            style='secondary'
        ).pack(side='left')

    def _setup_charts_section(self):
        """Setup charts section with usage trends and model distribution."""
        # Charts container
        charts_container = tk.Frame(self.main_frame_inner, bg=ModernTheme.BACKGROUND_PRIMARY)
        charts_container.pack(fill='x', pady=(0, ModernTheme.PADDING_XL))

        # Usage trend chart (left side)
        chart_card = ModernFrame(charts_container, padding=0)
        chart_card.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Sample data for demonstration
        sample_data = [
            {'label': 'Mon', 'value': 75},
            {'label': 'Tue', 'value': 45},
            {'label': 'Wed', 'value': 85},
            {'label': 'Thu', 'value': 60},
            {'label': 'Fri', 'value': 95},
            {'label': 'Sat', 'value': 40},
            {'label': 'Sun', 'value': 30}
        ]

        self.usage_chart = BarChart(
            chart_card,
            title="Usage Trend",
            data=sample_data
        )
        self.usage_chart.pack(fill='both', expand=True, padx=ModernTheme.PADDING_LG, pady=ModernTheme.PADDING_LG)

        # Model distribution (right side) - placeholder for now
        model_card = ModernFrame(charts_container, padding=0, width=300)
        model_card.pack(side='right', fill='y', padx=(10, 0))
        model_card.pack_propagate(False)

        model_content = tk.Frame(model_card, bg=ModernTheme.BACKGROUND_SECONDARY)
        model_content.pack(fill='both', expand=True, padx=ModernTheme.PADDING_LG, pady=ModernTheme.PADDING_LG)

        tk.Label(
            model_content,
            text="Model Usage",
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.TEXT_PRIMARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_XL, 'bold')
        ).pack(pady=(0, ModernTheme.PADDING_LG))

        # Placeholder for progress bars
        tk.Label(
            model_content,
            text="Model distribution\nwill be shown here",
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.TEXT_SECONDARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD),
            justify='center'
        ).pack(expand=True)

    def _setup_modern_treeview_style(self):
        """Configure modern styling for treeview widgets."""
        style = ttk.Style()
        style.theme_use('winnative')

        # Configure treeview style
        style.configure("Modern.Treeview",
            background=ModernTheme.BACKGROUND_SECONDARY,
            foreground=ModernTheme.TEXT_PRIMARY,
            rowheight=32,  # Increased row height for better readability
            fieldbackground=ModernTheme.BACKGROUND_SECONDARY,
            borderwidth=0,
            relief="flat"
        )

        # Configure treeview heading style
        style.configure("Modern.Treeview.Heading",
            background=ModernTheme.BACKGROUND_ACCENT,
            foreground=ModernTheme.TEXT_PRIMARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MD, 'bold'),
            borderwidth=1,
            relief="solid"
        )

        # Configure selection colors
        style.map("Modern.Treeview",
            background=[('selected', ModernTheme.PRIMARY_PURPLE)],
            foreground=[('selected', 'white')]
        )

        # Configure scrollbar styling
        style.configure("Modern.Vertical.TScrollbar",
            troughcolor=ModernTheme.BACKGROUND_ACCENT,
            borderwidth=0,
            arrowcolor=ModernTheme.TEXT_SECONDARY,
            darkcolor=ModernTheme.BORDER_MEDIUM,
            lightcolor=ModernTheme.BORDER_LIGHT
        )

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


    def _setup_modern_content_area(self):
        """Setup the modern data table section."""
        # Data table card
        table_card = ModernFrame(self.main_frame_inner, padding=0)
        table_card.pack(fill='both', expand=True, pady=(0, ModernTheme.PADDING_LG))

        # Table header
        table_header = tk.Frame(table_card, bg=ModernTheme.BACKGROUND_SECONDARY)
        table_header.pack(fill='x', padx=ModernTheme.PADDING_LG, pady=(ModernTheme.PADDING_LG, 0))

        tk.Label(
            table_header,
            text="Daily Usage Report",
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.TEXT_PRIMARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_XL, 'bold')
        ).pack(side='left')

        # Report table container
        self.report_frame = tk.Frame(table_card, bg=ModernTheme.BACKGROUND_SECONDARY)
        self.report_frame.pack(fill='both', expand=True, padx=ModernTheme.PADDING_LG, pady=ModernTheme.PADDING_LG)

        # Configure report frame
        self.report_frame.columnconfigure(0, weight=1)
        self.report_frame.rowconfigure(0, weight=1)

        # Setup modern report table
        self._setup_modern_report_table()

    def _setup_footer_section(self):
        """Setup footer section with attribution."""
        footer_card = ModernFrame(self.main_frame_inner, padding=0)
        footer_card.pack(fill='x', pady=(ModernTheme.PADDING_LG, 0))

        footer_content = tk.Frame(footer_card, bg=ModernTheme.BACKGROUND_SECONDARY)
        footer_content.pack(fill='x', padx=ModernTheme.PADDING_LG, pady=ModernTheme.PADDING_MD)

        # Attribution text
        attribution_label = tk.Label(
            footer_content,
            text="© 2024 Claude Code Usage • Based on ccusage by @ryoppippi",
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.TEXT_SECONDARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SM)
        )
        attribution_label.pack()

        # Links frame
        links_frame = tk.Frame(footer_content, bg=ModernTheme.BACKGROUND_SECONDARY)
        links_frame.pack(pady=(ModernTheme.PADDING_SM, 0))

        # Documentation link
        doc_link = tk.Label(
            links_frame,
            text="Documentation",
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.PRIMARY_PURPLE,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SM, 'bold'),
            cursor="hand2"
        )
        doc_link.pack(side='left', padx=(0, ModernTheme.PADDING_LG))
        doc_link.bind('<Button-1>', lambda e: self._show_documentation())

        # GitHub link (placeholder)
        github_link = tk.Label(
            links_frame,
            text="GitHub",
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.PRIMARY_PURPLE,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SM, 'bold'),
            cursor="hand2"
        )
        github_link.pack(side='left', padx=(0, ModernTheme.PADDING_LG))

        # Support link (placeholder)
        support_link = tk.Label(
            links_frame,
            text="Support",
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.PRIMARY_PURPLE,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SM, 'bold'),
            cursor="hand2"
        )
        support_link.pack(side='left')

    def _setup_modern_report_table(self):
        """Setup the modern report data table."""
        # Table frame with scrollbars
        table_frame = tk.Frame(self.report_frame, bg=ModernTheme.BACKGROUND_SECONDARY)
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Treeview for report data with modern styling
        columns = ('date', 'tokens', 'input', 'output', 'cache_creation', 'cache_read', 'cost')
        self.report_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            height=15,
            style="Modern.Treeview"
        )

        # Configure columns with modern styling
        self.report_tree.heading('date', text='Date')
        self.report_tree.heading('tokens', text='Total Tokens')
        self.report_tree.heading('input', text='Input Tokens')
        self.report_tree.heading('output', text='Output Tokens')
        self.report_tree.heading('cache_creation', text='Cache Creation')
        self.report_tree.heading('cache_read', text='Cache Read')
        self.report_tree.heading('cost', text='Cost (USD)')

        # Configure column widths (responsive)
        self.report_tree.column('date', width=120, minwidth=100)
        self.report_tree.column('tokens', width=120, minwidth=100)
        self.report_tree.column('input', width=110, minwidth=90)
        self.report_tree.column('output', width=110, minwidth=90)
        self.report_tree.column('cache_creation', width=130, minwidth=110)
        self.report_tree.column('cache_read', width=110, minwidth=90)
        self.report_tree.column('cost', width=100, minwidth=80)

        # Modern scrollbars
        v_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.report_tree.yview,
            style="Modern.Vertical.TScrollbar"
        )
        h_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.report_tree.xview
        )
        self.report_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout
        self.report_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def _setup_modern_summary_view(self):
        """Setup the modern summary view with cards."""
        # Create summary cards container
        cards_container = tk.Frame(self.summary_frame, bg=ModernTheme.BACKGROUND_SECONDARY)
        cards_container.pack(fill='both', expand=True, padx=ModernTheme.PADDING_LG, pady=ModernTheme.PADDING_LG)

        # Summary data storage
        self.summary_labels = {}

        # Create summary cards in a grid
        card_data = [
            ("Total Records", "total_records", "📄"),
            ("Date Range", "date_range", "📅"),
            ("Total Tokens", "total_tokens", "📊"),
            ("Total Cost", "total_cost", "💰"),
            ("Avg Daily Cost", "avg_daily_cost", "📈"),
            ("Top Model", "top_model", "🤖")
        ]

        # Create cards in 2 columns
        for i, (title, key, icon) in enumerate(card_data):
            row = i // 2
            col = i % 2

            # Card frame
            card_frame = ModernFrame(
                cards_container,
                padding=0,
                bd=1,
                relief='solid',
                highlightbackground=ModernTheme.BORDER_LIGHT,
                highlightthickness=1
            )
            card_frame.grid(
                row=row, column=col,
                sticky=(tk.W, tk.E, tk.N, tk.S),
                padx=ModernTheme.PADDING_SM,
                pady=ModernTheme.PADDING_SM
            )

            # Card content
            content_frame = tk.Frame(card_frame, bg=ModernTheme.BACKGROUND_SECONDARY)
            content_frame.pack(fill='both', expand=True, padx=ModernTheme.PADDING_MD, pady=ModernTheme.PADDING_MD)

            # Icon and title row
            header_frame = tk.Frame(content_frame, bg=ModernTheme.BACKGROUND_SECONDARY)
            header_frame.pack(fill='x', pady=(0, ModernTheme.PADDING_XS))

            ModernLabel(
                header_frame,
                text=icon,
                font=(ModernTheme.FONT_FAMILY, 16),
                bg=ModernTheme.BACKGROUND_SECONDARY
            ).pack(side='left')

            ModernLabel(
                header_frame,
                text=title,
                level='caption',
                bg=ModernTheme.BACKGROUND_SECONDARY
            ).pack(side='left', padx=(ModernTheme.PADDING_SM, 0))

            # Value label
            value_label = ModernLabel(
                content_frame,
                text="Loading...",
                level='subheading',
                bg=ModernTheme.BACKGROUND_SECONDARY
            )
            value_label.pack(anchor='w')
            self.summary_labels[key] = value_label

        # Configure grid weights for responsive layout
        for i in range(2):
            cards_container.columnconfigure(i, weight=1)

    def _setup_modern_status_bar(self):
        """Setup the modern status bar."""
        self.status_var = tk.StringVar(value="Ready")
        # Status updates will be shown in the UI, no separate status bar needed

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
        # Update status
        self.status_var.set(f"Loaded {len(records)} usage records")

        # Update dashboard stats
        self._update_summary(records)

        # Update usage chart with sample data based on records
        if records:
            # Create sample weekly data - in a real implementation, this would aggregate actual data
            sample_chart_data = [
                {'label': 'Mon', 'value': len([r for r in records[:len(records)//7]]) * 10},
                {'label': 'Tue', 'value': len([r for r in records[:len(records)//6]]) * 8},
                {'label': 'Wed', 'value': len([r for r in records[:len(records)//5]]) * 12},
                {'label': 'Thu', 'value': len([r for r in records[:len(records)//4]]) * 9},
                {'label': 'Fri', 'value': len([r for r in records[:len(records)//3]]) * 15},
                {'label': 'Sat', 'value': len([r for r in records[:len(records)//2]]) * 6},
                {'label': 'Sun', 'value': len(records) // 10}
            ]
            self.usage_chart.update_data(sample_chart_data)

        # Generate the detailed report
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

            # Update table with modern styling
            self._update_modern_report_table(report_data, report_type)

            self.status_var.set(f"Generated {report_type} report with {len(report_data)} entries")

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            self.status_var.set("Error generating report")
            messagebox.showerror("Report Error", f"Failed to generate report:\n{e}")

    def _update_modern_report_table(self, report_data, report_type):
        """Update report table with modern empty state handling."""
        # Clear existing data
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        # Check for empty data
        if not report_data:
            # Hide the treeview and show empty state
            self.report_tree.grid_remove()

            # Create or update empty state
            if not hasattr(self, 'empty_state_widget'):
                self.empty_state_widget = EmptyStateWidget(
                    self.report_frame,
                    title="No Claude Usage Data Found",
                    description=f"No {report_type} data available for the selected criteria.\n\nThis usually means:\n• Claude Code hasn't been used yet\n• No data in the selected date range\n• Data files may be in a different location\n\nTry adjusting your date range or refresh the data.",
                    action_text="Refresh Data",
                    action_command=self._refresh_data
                )

            self.empty_state_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            return

        # Hide empty state and show table
        if hasattr(self, 'empty_state_widget'):
            self.empty_state_widget.grid_remove()

        self.report_tree.grid()

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

        # Add new data with proper formatting
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
        """Update the stats cards with current data."""
        if not records:
            # Update stats cards with zero values
            self.stats_cards['tokens'].update_values("0", "No data available")
            self.stats_cards['cost'].update_values("$0.00", "Avg: $0.00/day")
            self.stats_cards['sessions'].update_values("0", "This month")
            self.stats_cards['cache'].update_values("0%", "Saved $0.00")
            return

        try:
            # Calculate summary statistics
            total_records = len(records)

            # Date range
            timestamps = [r.timestamp for r in records]
            start_date = min(timestamps)
            end_date = max(timestamps)

            # Token totals
            total_tokens = sum(r.total_tokens for r in records)
            total_input = sum(r.input_tokens for r in records)
            total_output = sum(r.output_tokens for r in records)
            total_cache_creation = sum(r.cache_creation_tokens for r in records)
            total_cache_read = sum(r.cache_read_tokens for r in records)

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

            # Cache hit rate calculation
            total_cache_tokens = total_cache_creation + total_cache_read
            cache_hit_rate = (total_cache_read / total_cache_tokens * 100) if total_cache_tokens > 0 else 0

            # Estimated cache savings (rough calculation)
            cache_savings = (total_cache_read / 1000) * 0.01  # Simplified calculation

            # Session count (unique session IDs)
            session_ids = set(getattr(r, 'session_id', str(i)) for i, r in enumerate(records))
            session_count = len(session_ids)

            # Format large numbers
            if total_tokens >= 1_000_000:
                tokens_display = f"{total_tokens / 1_000_000:.1f}M"
            elif total_tokens >= 1_000:
                tokens_display = f"{total_tokens / 1_000:.1f}K"
            else:
                tokens_display = str(total_tokens)

            # Update stats cards
            self.stats_cards['tokens'].update_values(
                tokens_display,
                f"Last {days} days"
            )

            self.stats_cards['cost'].update_values(
                format_currency(total_cost),
                f"Avg: {format_currency(avg_daily_cost)}/day"
            )

            self.stats_cards['sessions'].update_values(
                str(session_count),
                "This period"
            )

            self.stats_cards['cache'].update_values(
                f"{cache_hit_rate:.0f}%",
                f"Saved {format_currency(cache_savings)}"
            )

        except Exception as e:
            logger.error(f"Error updating summary: {e}")
            # Update with error state
            for card in self.stats_cards.values():
                card.update_values("Error", "Failed to calculate")

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


# Additional modern widget classes for dashboard style

class StatsCard(ModernFrame):
    """Statistics card widget with icon, value, and trend indicator."""

    def __init__(self, parent, title="", value="", detail="", icon="📊",
                 trend=None, icon_color="blue", **kwargs):

        super().__init__(parent, card_style=True, padding=0, **kwargs)

        # Configure the card
        self.configure(
            bg=ModernTheme.BACKGROUND_SECONDARY,
            relief='flat',
            bd=0,
            highlightbackground=ModernTheme.CARD_SHADOW_COLOR,
            highlightthickness=1
        )

        # Add hover effect
        self.bind('<Enter>', self._on_hover_enter)
        self.bind('<Leave>', self._on_hover_leave)

        # Card content frame
        content_frame = tk.Frame(self, bg=ModernTheme.BACKGROUND_SECONDARY)
        content_frame.pack(fill='both', expand=True, padx=ModernTheme.PADDING_LG,
                          pady=ModernTheme.PADDING_LG)

        # Header row with icon and trend badge
        header_frame = tk.Frame(content_frame, bg=ModernTheme.BACKGROUND_SECONDARY)
        header_frame.pack(fill='x', pady=(0, ModernTheme.PADDING_MD))

        # Icon with colored background
        icon_bg_colors = {
            'blue': (ModernTheme.ICON_BLUE_BG, ModernTheme.ICON_BLUE_FG),
            'green': (ModernTheme.ICON_GREEN_BG, ModernTheme.ICON_GREEN_FG),
            'purple': (ModernTheme.ICON_PURPLE_BG, ModernTheme.ICON_PURPLE_FG),
            'orange': (ModernTheme.ICON_ORANGE_BG, ModernTheme.ICON_ORANGE_FG)
        }

        bg_color, fg_color = icon_bg_colors.get(icon_color, icon_bg_colors['blue'])

        icon_frame = tk.Frame(
            header_frame,
            bg=bg_color,
            width=48,
            height=48,
            relief='flat'
        )
        icon_frame.pack(side='left')
        icon_frame.pack_propagate(False)

        icon_label = tk.Label(
            icon_frame,
            text=icon,
            bg=bg_color,
            fg=fg_color,
            font=(ModernTheme.FONT_FAMILY, 24),
            justify='center'
        )
        icon_label.pack(expand=True)

        # Trend badge (if provided)
        if trend:
            trend_color = ModernTheme.SUCCESS_LIGHT if trend.startswith('+') else ModernTheme.ERROR_LIGHT
            trend_text_color = ModernTheme.SUCCESS_DARK if trend.startswith('+') else ModernTheme.ERROR_DARK

            trend_badge = tk.Label(
                header_frame,
                text=trend,
                bg=trend_color,
                fg=trend_text_color,
                font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_CAPTION, 'bold'),
                padx=10,
                pady=4
            )
            trend_badge.pack(side='right')

        # Title label
        title_label = tk.Label(
            content_frame,
            text=title,
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.TEXT_SECONDARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SM, 'normal')
        )
        title_label.pack(anchor='w', pady=(0, 6))

        # Value label (large)
        value_label = tk.Label(
            content_frame,
            text=value,
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.TEXT_PRIMARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_STAT, 'bold')
        )
        value_label.pack(anchor='w', pady=(0, 6))

        # Detail label
        detail_label = tk.Label(
            content_frame,
            text=detail,
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.TEXT_DISABLED,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_CAPTION)
        )
        detail_label.pack(anchor='w')

        # Store references for updating
        self.title_label = title_label
        self.value_label = value_label
        self.detail_label = detail_label

    def _on_hover_enter(self, event):
        """Hover enter effect."""
        # Add elevation effect by changing highlight
        self.configure(highlightthickness=2, highlightbackground=ModernTheme.PRIMARY_PURPLE)

    def _on_hover_leave(self, event):
        """Hover leave effect."""
        # Return to normal state
        self.configure(highlightthickness=1, highlightbackground=ModernTheme.CARD_SHADOW_COLOR)

    def update_values(self, value="", detail=""):
        """Update the card values."""
        if value:
            self.value_label.config(text=value)
        if detail:
            self.detail_label.config(text=detail)


class GradientFrame(tk.Frame):
    """Frame with gradient background using Canvas."""

    def __init__(self, parent, start_color, end_color, **kwargs):
        super().__init__(parent, **kwargs)

        self.start_color = start_color
        self.end_color = end_color

        # Create canvas for gradient
        self.canvas = tk.Canvas(
            self,
            highlightthickness=0,
            relief='flat'
        )
        self.canvas.pack(fill='both', expand=True)

        # Bind resize event to redraw gradient
        self.canvas.bind('<Configure>', self._draw_gradient)

    def _draw_gradient(self, event=None):
        """Draw gradient background."""
        self.canvas.delete('gradient')

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        # Convert hex colors to RGB
        start_rgb = self._hex_to_rgb(self.start_color)
        end_rgb = self._hex_to_rgb(self.end_color)

        # Create gradient strips
        steps = min(width, 100)  # Limit steps for performance

        for i in range(steps):
            # Calculate color for this step
            ratio = i / (steps - 1) if steps > 1 else 0
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)

            color = f'#{r:02x}{g:02x}{b:02x}'

            # Draw vertical strip
            x1 = (i * width) // steps
            x2 = ((i + 1) * width) // steps

            self.canvas.create_rectangle(
                x1, 0, x2, height,
                fill=color,
                outline=color,
                tags='gradient'
            )

    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def add_content(self, widget_class, **kwargs):
        """Add content widget on top of gradient."""
        return widget_class(self.canvas, **kwargs)


class BarChart(tk.Frame):
    """Bar chart widget for displaying usage trends."""

    def __init__(self, parent, title="Chart", data=None, **kwargs):
        super().__init__(parent, bg=ModernTheme.BACKGROUND_SECONDARY, **kwargs)

        self.data = data or []

        # Chart title
        title_label = tk.Label(
            self,
            text=title,
            bg=ModernTheme.BACKGROUND_SECONDARY,
            fg=ModernTheme.TEXT_PRIMARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_XL, 'bold')
        )
        title_label.pack(pady=(0, ModernTheme.PADDING_LG))

        # Chart canvas
        self.canvas = tk.Canvas(
            self,
            bg=ModernTheme.BACKGROUND_SECONDARY,
            height=240,
            highlightthickness=0
        )
        self.canvas.pack(fill='x', expand=True, padx=ModernTheme.PADDING_MD)

        # Bind resize to redraw
        self.canvas.bind('<Configure>', self._draw_chart)

    def _draw_chart(self, event=None):
        """Draw the bar chart."""
        self.canvas.delete('all')

        if not self.data:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        # Chart dimensions (with extra bottom margin for labels)
        margin_top = 20
        margin_bottom = 50  # Extra space for labels
        margin_sides = 40
        chart_width = width - 2 * margin_sides
        chart_height = height - margin_top - margin_bottom

        if len(self.data) == 0:
            return

        # Calculate bar dimensions
        bar_width = chart_width / len(self.data) * 0.8
        bar_spacing = chart_width / len(self.data) * 0.2

        # Find max value for scaling
        max_value = max(item['value'] for item in self.data) if self.data else 1

        # Draw bars
        for i, item in enumerate(self.data):
            x = margin_sides + i * (bar_width + bar_spacing) + bar_spacing / 2
            bar_height = (item['value'] / max_value) * chart_height if max_value > 0 else 0
            y = margin_top + chart_height - bar_height

            # Create gradient effect with multiple rectangles
            gradient_steps = 20
            step_height = bar_height / gradient_steps

            for j in range(gradient_steps):
                step_y = y + j * step_height

                # Calculate color blend
                ratio = j / gradient_steps
                start_color = self._hex_to_rgb(ModernTheme.GRADIENT_START)
                end_color = self._hex_to_rgb(ModernTheme.GRADIENT_END)

                r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)

                color = f'#{r:02x}{g:02x}{b:02x}'

                self.canvas.create_rectangle(
                    x, step_y, x + bar_width, step_y + step_height + 1,
                    fill=color,
                    outline=color
                )

            # Label (positioned below the chart area)
            self.canvas.create_text(
                x + bar_width / 2,
                height - margin_bottom + 20,
                text=item['label'],
                fill=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_CAPTION)
            )

    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def update_data(self, data):
        """Update chart data and redraw."""
        self.data = data
        self._draw_chart()