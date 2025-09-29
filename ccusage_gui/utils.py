"""
Utility functions for Mr. The Guru - Claude Code Usage GUI

Common utility functions used throughout the application.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
import re


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up application logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("ccusage_gui")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create log file {log_file}: {e}")

    return logger


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.2 MB")
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def format_number(number: Union[int, float], precision: int = 2) -> str:
    """
    Format number with thousand separators.

    Args:
        number: Number to format
        precision: Decimal places for float numbers

    Returns:
        Formatted number string
    """
    if isinstance(number, float):
        return f"{number:,.{precision}f}"
    return f"{number:,}"


def format_currency(amount: float, currency: str = "USD", precision: int = 2) -> str:
    """
    Format currency amount.

    Args:
        amount: Amount to format
        currency: Currency code (USD, EUR, etc.)
        precision: Decimal places

    Returns:
        Formatted currency string
    """
    symbol_map = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }

    symbol = symbol_map.get(currency, currency)
    return f"{symbol}{amount:,.{precision}f}"


def format_percentage(value: float, precision: int = 1) -> str:
    """
    Format percentage value.

    Args:
        value: Percentage value (0.0 to 1.0)
        precision: Decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{precision}f}%"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"


def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse date string in various formats.

    Args:
        date_str: Date string to parse

    Returns:
        Parsed datetime object or None if parsing fails
    """
    formats = [
        "%Y-%m-%d",
        "%Y%m%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def validate_json_file(file_path: Union[str, Path]) -> bool:
    """
    Validate if a file contains valid JSON.

    Args:
        file_path: Path to JSON file

    Returns:
        True if valid JSON, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return False


def safe_json_load(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Safely load JSON file with default fallback.

    Args:
        file_path: Path to JSON file
        default: Default value if loading fails

    Returns:
        Loaded JSON data or default value
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def ensure_directory(directory: Union[str, Path]) -> bool:
    """
    Ensure directory exists, create if it doesn't.

    Args:
        directory: Directory path

    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def find_files(directory: Union[str, Path], pattern: str, recursive: bool = True) -> List[Path]:
    """
    Find files matching pattern in directory.

    Args:
        directory: Directory to search
        pattern: File pattern (glob style)
        recursive: Search recursively

    Returns:
        List of matching file paths
    """
    directory = Path(directory)
    if not directory.exists():
        return []

    try:
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))
    except Exception:
        return []


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for Windows filesystem.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for Windows
    """
    # Remove or replace invalid characters
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')

    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext

    return filename


def get_app_version() -> str:
    """
    Get application version from package.

    Returns:
        Version string
    """
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "1.0.0"


def get_system_info() -> Dict[str, str]:
    """
    Get system information for debugging.

    Returns:
        Dictionary with system information
    """
    import platform

    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "app_version": get_app_version()
    }


def is_valid_claude_project_dir(directory: Union[str, Path]) -> bool:
    """
    Check if directory contains valid Claude project data.

    Args:
        directory: Directory path to check

    Returns:
        True if directory contains Claude project files
    """
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        return False

    # Look for .jsonl files which indicate Claude usage data
    jsonl_files = list(directory.glob("*.jsonl"))
    return len(jsonl_files) > 0


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with optional suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def escape_html(text: str) -> str:
    """
    Escape HTML special characters.

    Args:
        text: Text to escape

    Returns:
        HTML-escaped text
    """
    escape_map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;'
    }

    for char, escaped in escape_map.items():
        text = text.replace(char, escaped)

    return text


class ProgressTracker:
    """Simple progress tracking utility."""

    def __init__(self, total: int, callback: Optional[callable] = None):
        """
        Initialize progress tracker.

        Args:
            total: Total number of items to process
            callback: Optional callback function for progress updates
        """
        self.total = total
        self.current = 0
        self.callback = callback

    def update(self, increment: int = 1) -> float:
        """
        Update progress.

        Args:
            increment: Amount to increment

        Returns:
            Current progress as percentage (0.0 to 1.0)
        """
        self.current = min(self.current + increment, self.total)
        progress = self.current / self.total if self.total > 0 else 1.0

        if self.callback:
            self.callback(progress, self.current, self.total)

        return progress

    def reset(self):
        """Reset progress to zero."""
        self.current = 0

    @property
    def percentage(self) -> float:
        """Get current progress as percentage."""
        return (self.current / self.total) * 100 if self.total > 0 else 100.0

    @property
    def is_complete(self) -> bool:
        """Check if progress is complete."""
        return self.current >= self.total