"""
Mr. The Guru - Claude Code Usage GUI Package

A Windows-focused GUI application for analyzing Claude Code usage data,
based on the original ccusage CLI tool by @ryoppippi.

This package provides:
- Data loading from Claude JSONL files
- Token usage analysis and cost calculation
- Multiple report types (daily, monthly, weekly, session, blocks)
- Export functionality (JSON, CSV)
- User-friendly GUI interface

Author: Based on ccusage by @ryoppippi
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Budgulick"
__description__ = "Mr. The Guru - Claude Code Usage GUI"

# Package imports
from . import config
from . import utils
from . import data_loader
from . import cost_calculator
from . import reports
from . import gui

__all__ = [
    "config",
    "utils",
    "data_loader",
    "cost_calculator",
    "reports",
    "gui",
]