#!/usr/bin/env python3
"""
Mr. The Guru - Claude Code Usage
Main entry point for the ccusage GUI application

This is a Windows-focused GUI application that provides the same functionality
as the original ccusage CLI tool but with a user-friendly graphical interface.

Author: Based on ccusage by @ryoppippi
License: MIT
"""

import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from ccusage_gui import main as gui_main


def main():
    """Main entry point for the application."""
    try:
        # Start the GUI application
        gui_main.run_app()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()