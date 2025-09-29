"""
Configuration management for Mr. The Guru - Claude Code Usage

Handles loading, saving, and validation of application configuration.
Configuration is stored in mrtg_ccusage.json in the application directory.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataSourceConfig:
    """Configuration for Claude data directories."""
    primary_path: str = ""
    secondary_path: str = ""
    custom_paths: List[str] = None
    use_environment_var: bool = True

    def __post_init__(self):
        if self.custom_paths is None:
            self.custom_paths = []


@dataclass
class DisplayConfig:
    """Configuration for display options."""
    theme: str = "light"  # light, dark, system
    font_family: str = "Segoe UI"
    font_size: int = 9
    show_toolbar: bool = True
    show_status_bar: bool = True
    compact_mode: bool = False
    color_output: bool = True


@dataclass
class CostConfig:
    """Configuration for cost calculation."""
    mode: str = "auto"  # auto, calculate, display
    offline_mode: bool = False
    currency: str = "USD"
    auto_update_pricing: bool = False
    update_frequency: str = "weekly"  # daily, weekly, monthly, never
    last_update: str = ""


@dataclass
class ExportConfig:
    """Configuration for export options."""
    default_format: str = "json"  # json, csv
    include_breakdown: bool = True
    default_directory: str = ""
    timestamp_files: bool = True


@dataclass
class AppConfig:
    """Main application configuration."""
    data_sources: DataSourceConfig
    display: DisplayConfig
    cost: CostConfig
    export: ExportConfig
    window_state: Dict[str, Any] = None

    def __post_init__(self):
        if self.window_state is None:
            self.window_state = {
                "width": 1200,
                "height": 800,
                "x": -1,
                "y": -1,
                "maximized": False
            }


class ConfigManager:
    """
    Manages application configuration with automatic file handling.

    Configuration is stored in mrtg_ccusage.json in the application directory.
    If the file doesn't exist, it will be created with default values.
    """

    CONFIG_FILENAME = "mrtg_ccusage.json"
    CONFIG_VERSION = "1.0"

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the configuration manager.

        Args:
            config_dir: Directory to store config file. If None, uses app directory.
        """
        if config_dir is None:
            # Use the directory where the application is running
            config_dir = Path.cwd()

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / self.CONFIG_FILENAME
        self._config: Optional[AppConfig] = None

        # Set up default Claude data directories
        self._default_claude_paths = self._get_default_claude_paths()

        # Load or create configuration
        self.load_config()

    def _get_default_claude_paths(self) -> List[str]:
        """Get default Claude data directory paths for Windows."""
        user_profile = os.environ.get("USERPROFILE", "")
        if not user_profile:
            return []

        paths = [
            os.path.join(user_profile, ".config", "claude", "projects"),
            os.path.join(user_profile, ".claude", "projects")
        ]

        # Add CLAUDE_CONFIG_DIR if set
        claude_config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
        if claude_config_dir:
            paths.insert(0, os.path.join(claude_config_dir, "projects"))

        return paths

    def _create_default_config(self) -> AppConfig:
        """Create a default configuration."""
        claude_paths = self._default_claude_paths
        primary_path = claude_paths[0] if claude_paths else ""
        secondary_path = claude_paths[1] if len(claude_paths) > 1 else ""

        return AppConfig(
            data_sources=DataSourceConfig(
                primary_path=primary_path,
                secondary_path=secondary_path,
                custom_paths=[],
                use_environment_var=True
            ),
            display=DisplayConfig(),
            cost=CostConfig(),
            export=ExportConfig()
        )

    def load_config(self) -> AppConfig:
        """
        Load configuration from file or create default if file doesn't exist.

        Returns:
            The loaded or default configuration.
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Validate version compatibility
                version = data.get('version', '1.0')
                if version != self.CONFIG_VERSION:
                    logger.warning(f"Config version mismatch: {version} != {self.CONFIG_VERSION}")

                # Remove version and metadata from config data
                config_data = {k: v for k, v in data.items()
                             if k not in ['version', 'created', 'modified']}

                # Convert to config objects
                self._config = AppConfig(
                    data_sources=DataSourceConfig(**config_data.get('data_sources', {})),
                    display=DisplayConfig(**config_data.get('display', {})),
                    cost=CostConfig(**config_data.get('cost', {})),
                    export=ExportConfig(**config_data.get('export', {})),
                    window_state=config_data.get('window_state', {})
                )

                logger.info(f"Configuration loaded from {self.config_file}")

            except Exception as e:
                logger.error(f"Error loading config: {e}")
                logger.info("Creating default configuration")
                self._config = self._create_default_config()
                self.save_config()
        else:
            logger.info(f"Config file not found at {self.config_file}, creating default")
            self._config = self._create_default_config()
            self.save_config()

        return self._config

    def save_config(self) -> bool:
        """
        Save current configuration to file.

        Returns:
            True if successful, False otherwise.
        """
        if self._config is None:
            logger.error("No configuration to save")
            return False

        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Convert config to dictionary
            config_dict = asdict(self._config)

            # Add metadata
            config_dict['version'] = self.CONFIG_VERSION
            config_dict['created'] = config_dict.get('created',
                                                   Path(self.config_file).stat().st_ctime
                                                   if self.config_file.exists() else None)

            # Write to file with pretty formatting
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Configuration saved to {self.config_file}")
            return True

        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False

    @property
    def config(self) -> AppConfig:
        """Get the current configuration."""
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def get_claude_data_paths(self) -> List[str]:
        """
        Get all configured Claude data directory paths.

        Returns:
            List of directory paths to search for Claude data.
        """
        paths = []

        # Add primary path if configured
        if self.config.data_sources.primary_path:
            paths.append(self.config.data_sources.primary_path)

        # Add secondary path if configured
        if self.config.data_sources.secondary_path:
            paths.append(self.config.data_sources.secondary_path)

        # Add custom paths
        paths.extend(self.config.data_sources.custom_paths)

        # Add environment variable path if enabled
        if self.config.data_sources.use_environment_var:
            env_path = os.environ.get("CLAUDE_CONFIG_DIR")
            if env_path:
                env_projects_path = os.path.join(env_path, "projects")
                if env_projects_path not in paths:
                    paths.append(env_projects_path)

        # Add default paths if none configured
        if not paths:
            paths = self._default_claude_paths

        # Filter to only existing directories
        existing_paths = [p for p in paths if os.path.exists(p)]

        return existing_paths

    def update_window_state(self, width: int, height: int, x: int, y: int, maximized: bool = False):
        """Update window state in configuration."""
        self.config.window_state.update({
            "width": width,
            "height": height,
            "x": x,
            "y": y,
            "maximized": maximized
        })
        self.save_config()

    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self._config = self._create_default_config()
            return self.save_config()
        except Exception as e:
            logger.error(f"Error resetting config: {e}")
            return False