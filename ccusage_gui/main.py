"""
Main application runner for Mr. The Guru - Claude Code Usage GUI
"""

import os
import sys
import tkinter as tk
from pathlib import Path

from .config import ConfigManager
from .gui import MainApplication


def run_app():
    """
    Initialize and run the main GUI application.
    """
    # Initialize configuration
    config_manager = ConfigManager()

    # Create main window
    root = tk.Tk()

    # Set application title
    root.title("Mr. The Guru - Claude Code Usage")

    # Set icon if it exists
    icon_path = Path(__file__).parent.parent / "assets" / "mrtheguru_icon_main.ico"
    if icon_path.exists():
        try:
            root.iconbitmap(str(icon_path))
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")

    # Set minimum window size
    root.minsize(800, 600)

    # Center window on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 1200
    window_height = 800

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Create main application
    app = MainApplication(root, config_manager)

    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    run_app()