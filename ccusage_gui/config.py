"""
Configuration management for Mr. The Guru - Claude Code Usage

Handles loading, saving, and validation of application configuration.
Configuration is stored in mrtg_ccusage.json in the application directory.

Features:
- JSON Schema validation
- Configuration migration support
- Enhanced error handling and recovery
- Type-safe configuration with Pydantic
- Secure path validation
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from enum import Enum
import logging

try:
    from pydantic import BaseModel, Field, validator, root_validator
    from pydantic.types import DirectoryPath
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback to dataclasses if Pydantic not available
    from dataclasses import dataclass, asdict
    BaseModel = object
    Field = lambda default=None, **kwargs: default
    PYDANTIC_AVAILABLE = False

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    jsonschema = None
    JSONSCHEMA_AVAILABLE = False

try:
    from platformdirs import user_config_dir, user_data_dir
    PLATFORMDIRS_AVAILABLE = True
except ImportError:
    PLATFORMDIRS_AVAILABLE = False

logger = logging.getLogger(__name__)


# Configuration Enums for type safety
class Theme(str, Enum):
    """Available theme options."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class CostMode(str, Enum):
    """Cost calculation modes."""
    AUTO = "auto"
    CALCULATE = "calculate"
    DISPLAY = "display"


class UpdateFrequency(str, Enum):
    """Update frequency options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NEVER = "never"


class ExportFormat(str, Enum):
    """Export format options."""
    JSON = "json"
    CSV = "csv"


class ConfigError(Exception):
    """Base exception for configuration errors."""
    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails."""
    pass


class ConfigMigrationError(ConfigError):
    """Raised when configuration migration fails."""
    pass


# JSON Schema for configuration validation
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string", "pattern": r"^\d+\.\d+$"},
        "data_sources": {
            "type": "object",
            "properties": {
                "primary_path": {"type": "string"},
                "secondary_path": {"type": "string"},
                "custom_paths": {"type": "array", "items": {"type": "string"}},
                "use_environment_var": {"type": "boolean"}
            },
            "required": ["use_environment_var"]
        },
        "display": {
            "type": "object",
            "properties": {
                "theme": {"type": "string", "enum": ["light", "dark", "system"]},
                "font_family": {"type": "string"},
                "font_size": {"type": "integer", "minimum": 6, "maximum": 72},
                "show_toolbar": {"type": "boolean"},
                "show_status_bar": {"type": "boolean"},
                "compact_mode": {"type": "boolean"},
                "color_output": {"type": "boolean"}
            }
        },
        "cost": {
            "type": "object",
            "properties": {
                "mode": {"type": "string", "enum": ["auto", "calculate", "display"]},
                "offline_mode": {"type": "boolean"},
                "currency": {"type": "string", "pattern": r"^[A-Z]{3}$"},
                "auto_update_pricing": {"type": "boolean"},
                "update_frequency": {"type": "string", "enum": ["daily", "weekly", "monthly", "never"]},
                "last_update": {"type": "string"}
            }
        },
        "export": {
            "type": "object",
            "properties": {
                "default_format": {"type": "string", "enum": ["json", "csv"]},
                "include_breakdown": {"type": "boolean"},
                "default_directory": {"type": "string"},
                "timestamp_files": {"type": "boolean"}
            }
        },
        "window_state": {
            "type": "object",
            "properties": {
                "width": {"type": "integer", "minimum": 400},
                "height": {"type": "integer", "minimum": 300},
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "maximized": {"type": "boolean"}
            }
        }
    },
    "required": ["version", "data_sources", "display", "cost", "export"]
}


# Configuration base classes with Pydantic or dataclass fallback
if PYDANTIC_AVAILABLE:
    ConfigBase = BaseModel

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True
        extra = "forbid"
else:
    ConfigBase = object


if PYDANTIC_AVAILABLE:
    class DataSourceConfig(ConfigBase):
        """Configuration for Claude data directories."""
        primary_path: str = Field(default="", description="Primary Claude data directory")
        secondary_path: str = Field(default="", description="Secondary Claude data directory")
        custom_paths: List[str] = Field(default_factory=list, description="Additional custom paths")
        use_environment_var: bool = Field(default=True, description="Use CLAUDE_CONFIG_DIR environment variable")

        @validator('primary_path', 'secondary_path')
        def validate_paths(cls, v):
            """Validate directory paths for security."""
            if v and not cls._is_safe_path(v):
                raise ValueError(f"Unsafe path detected: {v}")
            return v

        @validator('custom_paths')
        def validate_custom_paths(cls, v):
            """Validate custom paths for security."""
            for path in v:
                if not cls._is_safe_path(path):
                    raise ValueError(f"Unsafe path detected: {path}")
            return v

        @staticmethod
        def _is_safe_path(path: str) -> bool:
            """Check if path is safe (no directory traversal)."""
            if not path:
                return True
            try:
                resolved = Path(path).resolve()
                return not any(part.startswith('..') for part in Path(path).parts)
            except (OSError, ValueError):
                return False

        class Config(Config):
            pass

    class DisplayConfig(ConfigBase):
        """Configuration for display options."""
        theme: Theme = Field(default=Theme.LIGHT, description="Application theme")
        font_family: str = Field(default="Segoe UI", description="Font family")
        font_size: int = Field(default=9, ge=6, le=72, description="Font size")
        show_toolbar: bool = Field(default=True, description="Show toolbar")
        show_status_bar: bool = Field(default=True, description="Show status bar")
        compact_mode: bool = Field(default=False, description="Compact display mode")
        color_output: bool = Field(default=True, description="Use colored output")

        class Config(Config):
            pass

    class CostConfig(ConfigBase):
        """Configuration for cost calculation."""
        mode: CostMode = Field(default=CostMode.AUTO, description="Cost calculation mode")
        offline_mode: bool = Field(default=False, description="Offline mode")
        currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$", description="Currency code")
        auto_update_pricing: bool = Field(default=False, description="Auto-update pricing")
        update_frequency: UpdateFrequency = Field(default=UpdateFrequency.WEEKLY, description="Update frequency")
        last_update: str = Field(default="", description="Last update timestamp")

        class Config(Config):
            pass

    class ExportConfig(ConfigBase):
        """Configuration for export options."""
        default_format: ExportFormat = Field(default=ExportFormat.JSON, description="Default export format")
        include_breakdown: bool = Field(default=True, description="Include breakdown in exports")
        default_directory: str = Field(default="", description="Default export directory")
        timestamp_files: bool = Field(default=True, description="Add timestamps to exported files")

        @validator('default_directory')
        def validate_export_directory(cls, v):
            """Validate export directory path."""
            if v and not DataSourceConfig._is_safe_path(v):
                raise ValueError(f"Unsafe export directory: {v}")
            return v

        class Config(Config):
            pass

    class AppConfig(ConfigBase):
        """Main application configuration."""
        data_sources: DataSourceConfig = Field(default_factory=DataSourceConfig)
        display: DisplayConfig = Field(default_factory=DisplayConfig)
        cost: CostConfig = Field(default_factory=CostConfig)
        export: ExportConfig = Field(default_factory=ExportConfig)
        window_state: Dict[str, Any] = Field(default_factory=lambda: {
            "width": 1200,
            "height": 800,
            "x": -1,
            "y": -1,
            "maximized": False
        })

        class Config(Config):
            pass

else:
    # Fallback to dataclasses when Pydantic is not available
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
    Enhanced configuration manager with validation, migration, and error recovery.

    Features:
    - JSON Schema validation
    - Configuration version migration
    - Backup and recovery mechanisms
    - Type-safe configuration handling
    - Enhanced error reporting and logging

    Configuration is stored in mrtg_ccusage.json in the application directory.
    If the file doesn't exist, it will be created with default values.
    """

    CONFIG_FILENAME = "mrtg_ccusage.json"
    CONFIG_VERSION = "1.1"
    BACKUP_SUFFIX = ".backup"
    MAX_BACKUP_FILES = 5

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the configuration manager.

        Args:
            config_dir: Directory to store config file. If None, uses platform-specific directory.
        """
        if config_dir is None:
            if PLATFORMDIRS_AVAILABLE:
                # Use platform-appropriate config directory
                config_dir = Path(user_config_dir("mrtg-ccusage", "MrTheGuru"))
            else:
                # Fallback to current working directory
                config_dir = Path.cwd()

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / self.CONFIG_FILENAME
        self._config: Optional[AppConfig] = None

        # Set up default Claude data directories
        self._default_claude_paths = self._get_default_claude_paths()

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load or create configuration
        self.load_config()

    def _get_default_claude_paths(self) -> List[str]:
        """Get default Claude data directory paths for Windows."""
        user_profile = os.environ.get("USERPROFILE", "")
        if not user_profile:
            return []

        paths = [
            os.path.join(user_profile, ".claude", "projects")
        ]

        # Add CLAUDE_CONFIG_DIR if set
        claude_config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
        if claude_config_dir:
            paths.insert(0, os.path.join(claude_config_dir, "projects"))

        return paths

    def _validate_config_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate configuration data against JSON schema.

        Args:
            data: Configuration data to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ConfigValidationError: If validation fails and JSONSCHEMA_AVAILABLE
        """
        if not JSONSCHEMA_AVAILABLE:
            logger.warning("JSON schema validation not available - skipping validation")
            return True

        try:
            jsonschema.validate(data, CONFIG_SCHEMA)
            return True
        except jsonschema.ValidationError as e:
            error_msg = f"Configuration validation failed: {e.message}"
            if e.path:
                error_msg += f" at path: {'.'.join(str(p) for p in e.path)}"
            logger.error(error_msg)
            raise ConfigValidationError(error_msg) from e
        except jsonschema.SchemaError as e:
            logger.error(f"Configuration schema error: {e}")
            return False

    def _create_backup(self) -> bool:
        """
        Create a backup of the current configuration file.

        Returns:
            True if backup created successfully, False otherwise
        """
        if not self.config_file.exists():
            return True

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.config_dir / f"{self.CONFIG_FILENAME}{self.BACKUP_SUFFIX}_{timestamp}"

            shutil.copy2(self.config_file, backup_file)
            logger.info(f"Configuration backup created: {backup_file}")

            # Clean up old backup files
            self._cleanup_old_backups()
            return True

        except Exception as e:
            logger.error(f"Failed to create configuration backup: {e}")
            return False

    def _cleanup_old_backups(self):
        """Remove old backup files, keeping only the most recent ones."""
        try:
            backup_pattern = f"{self.CONFIG_FILENAME}{self.BACKUP_SUFFIX}_*"
            backup_files = list(self.config_dir.glob(backup_pattern))

            if len(backup_files) > self.MAX_BACKUP_FILES:
                # Sort by modification time and remove oldest
                backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for old_backup in backup_files[self.MAX_BACKUP_FILES:]:
                    old_backup.unlink()
                    logger.debug(f"Removed old backup: {old_backup}")

        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")

    def _migrate_config(self, data: Dict[str, Any], from_version: str) -> Dict[str, Any]:
        """
        Migrate configuration from older version to current version.

        Args:
            data: Configuration data to migrate
            from_version: Source version

        Returns:
            Migrated configuration data

        Raises:
            ConfigMigrationError: If migration fails
        """
        logger.info(f"Migrating configuration from version {from_version} to {self.CONFIG_VERSION}")

        try:
            if from_version == "1.0" and self.CONFIG_VERSION == "1.1":
                # Migration from 1.0 to 1.1
                # Add any new fields with defaults
                migrated_data = data.copy()

                # Ensure all required sections exist
                if 'display' not in migrated_data:
                    migrated_data['display'] = {}
                if 'cost' not in migrated_data:
                    migrated_data['cost'] = {}
                if 'export' not in migrated_data:
                    migrated_data['export'] = {}

                # Add new fields for v1.1 (example - update as needed)
                # migrated_data['new_feature'] = {'enabled': True}

                migrated_data['version'] = self.CONFIG_VERSION
                logger.info("Configuration migrated successfully from 1.0 to 1.1")
                return migrated_data

            else:
                # Unknown migration path
                raise ConfigMigrationError(f"No migration path from {from_version} to {self.CONFIG_VERSION}")

        except Exception as e:
            raise ConfigMigrationError(f"Migration failed: {e}") from e

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
        Load configuration from file with validation and migration support.

        Returns:
            The loaded or default configuration.

        Raises:
            ConfigValidationError: If configuration validation fails
            ConfigMigrationError: If configuration migration fails
        """
        if self.config_file.exists():
            try:
                # Read and parse JSON
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Validate JSON structure first
                if not isinstance(data, dict):
                    raise ConfigValidationError("Configuration must be a JSON object")

                # Validate configuration data
                self._validate_config_data(data)

                # Check version and migrate if necessary
                version = data.get('version', '1.0')
                if version != self.CONFIG_VERSION:
                    logger.info(f"Config version mismatch: {version} != {self.CONFIG_VERSION}")

                    # Create backup before migration
                    self._create_backup()

                    # Migrate configuration
                    try:
                        data = self._migrate_config(data, version)
                        # Save migrated configuration
                        with open(self.config_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                    except ConfigMigrationError:
                        logger.error("Migration failed, using default configuration")
                        self._config = self._create_default_config()
                        self.save_config()
                        return self._config

                # Remove version and metadata from config data
                config_data = {k: v for k, v in data.items()
                             if k not in ['version', 'created', 'modified']}

                # Convert to config objects with error handling
                try:
                    if PYDANTIC_AVAILABLE:
                        # Use Pydantic for type validation
                        self._config = AppConfig(
                            data_sources=DataSourceConfig(**config_data.get('data_sources', {})),
                            display=DisplayConfig(**config_data.get('display', {})),
                            cost=CostConfig(**config_data.get('cost', {})),
                            export=ExportConfig(**config_data.get('export', {})),
                            window_state=config_data.get('window_state', {})
                        )
                    else:
                        # Fallback to dataclass construction
                        data_sources_data = config_data.get('data_sources', {})
                        if 'custom_paths' not in data_sources_data:
                            data_sources_data['custom_paths'] = []

                        self._config = AppConfig(
                            data_sources=DataSourceConfig(**data_sources_data),
                            display=DisplayConfig(**config_data.get('display', {})),
                            cost=CostConfig(**config_data.get('cost', {})),
                            export=ExportConfig(**config_data.get('export', {})),
                            window_state=config_data.get('window_state', {})
                        )

                    logger.info(f"Configuration loaded successfully from {self.config_file}")

                except (TypeError, ValueError) as e:
                    logger.error(f"Error constructing configuration objects: {e}")
                    raise ConfigValidationError(f"Invalid configuration structure: {e}") from e

            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"Error parsing config file: {e}")
                # Try to recover from backup
                if self._recover_from_backup():
                    return self.load_config()  # Retry after recovery
                else:
                    logger.info("Creating default configuration due to parse error")
                    self._config = self._create_default_config()
                    self.save_config()

            except (ConfigValidationError, ConfigMigrationError):
                # Re-raise these specific errors
                raise

            except Exception as e:
                logger.error(f"Unexpected error loading config: {e}")
                logger.info("Creating default configuration")
                self._config = self._create_default_config()
                self.save_config()
        else:
            logger.info(f"Config file not found at {self.config_file}, creating default")
            self._config = self._create_default_config()
            self.save_config()

        return self._config

    def _recover_from_backup(self) -> bool:
        """
        Attempt to recover configuration from the most recent backup.

        Returns:
            True if recovery successful, False otherwise
        """
        try:
            backup_pattern = f"{self.CONFIG_FILENAME}{self.BACKUP_SUFFIX}_*"
            backup_files = list(self.config_dir.glob(backup_pattern))

            if not backup_files:
                logger.warning("No backup files found for recovery")
                return False

            # Use the most recent backup
            latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
            logger.info(f"Attempting recovery from backup: {latest_backup}")

            # Copy backup to main config file
            shutil.copy2(latest_backup, self.config_file)
            logger.info("Configuration recovered from backup successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to recover from backup: {e}")
            return False

    def save_config(self) -> bool:
        """
        Save current configuration to file with validation and backup.

        Returns:
            True if successful, False otherwise.

        Raises:
            ConfigValidationError: If configuration validation fails
        """
        if self._config is None:
            logger.error("No configuration to save")
            return False

        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Create backup of existing config before saving
            if self.config_file.exists():
                self._create_backup()

            # Convert config to dictionary
            if PYDANTIC_AVAILABLE and hasattr(self._config, 'dict'):
                config_dict = self._config.dict()
            else:
                config_dict = asdict(self._config)

            # Add metadata
            current_time = datetime.now().isoformat()
            config_dict['version'] = self.CONFIG_VERSION
            config_dict['modified'] = current_time

            # Set created timestamp if this is the first save
            if not self.config_file.exists():
                config_dict['created'] = current_time
            else:
                # Preserve existing created timestamp
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        config_dict['created'] = existing_data.get('created', current_time)
                except Exception:
                    config_dict['created'] = current_time

            # Validate configuration before saving
            try:
                self._validate_config_data(config_dict)
            except ConfigValidationError as e:
                logger.error(f"Configuration validation failed before save: {e}")
                raise

            # Write to temporary file first for atomic save
            temp_file = self.config_file.with_suffix('.tmp')
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)

                # Atomic move to final location
                if os.name == 'nt':  # Windows
                    if self.config_file.exists():
                        self.config_file.unlink()
                    temp_file.rename(self.config_file)
                else:  # Unix-like
                    temp_file.rename(self.config_file)

                logger.info(f"Configuration saved successfully to {self.config_file}")
                return True

            finally:
                # Clean up temporary file if it still exists
                if temp_file.exists():
                    temp_file.unlink()

        except ConfigValidationError:
            # Re-raise validation errors
            raise

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
        Reset configuration to default values with backup.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Create backup before reset
            if self.config_file.exists():
                self._create_backup()

            self._config = self._create_default_config()
            result = self.save_config()

            if result:
                logger.info("Configuration reset to defaults successfully")
            return result

        except Exception as e:
            logger.error(f"Error resetting config: {e}")
            return False

    def export_config(self, export_path: Path, include_metadata: bool = True) -> bool:
        """
        Export configuration to a file.

        Args:
            export_path: Path to export the configuration
            include_metadata: Whether to include version and timestamps

        Returns:
            True if successful, False otherwise
        """
        try:
            if self._config is None:
                logger.error("No configuration to export")
                return False

            # Convert config to dictionary
            if PYDANTIC_AVAILABLE and hasattr(self._config, 'dict'):
                config_dict = self._config.dict()
            else:
                config_dict = asdict(self._config)

            if include_metadata:
                config_dict['version'] = self.CONFIG_VERSION
                config_dict['exported'] = datetime.now().isoformat()

            # Ensure export directory exists
            export_path.parent.mkdir(parents=True, exist_ok=True)

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Configuration exported to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            return False

    def import_config(self, import_path: Path, merge: bool = False) -> bool:
        """
        Import configuration from a file.

        Args:
            import_path: Path to import configuration from
            merge: If True, merge with existing config; if False, replace completely

        Returns:
            True if successful, False otherwise

        Raises:
            ConfigValidationError: If imported configuration is invalid
        """
        try:
            if not import_path.exists():
                logger.error(f"Import file does not exist: {import_path}")
                return False

            # Create backup before import
            if self.config_file.exists():
                self._create_backup()

            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            # Validate imported data
            self._validate_config_data(import_data)

            if merge and self._config is not None:
                # Merge with existing configuration
                if PYDANTIC_AVAILABLE and hasattr(self._config, 'dict'):
                    existing_dict = self._config.dict()
                else:
                    existing_dict = asdict(self._config)

                # Deep merge function
                def deep_merge(base: dict, update: dict) -> dict:
                    """Deep merge two dictionaries."""
                    result = base.copy()
                    for key, value in update.items():
                        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                            result[key] = deep_merge(result[key], value)
                        else:
                            result[key] = value
                    return result

                # Remove metadata from import data for merging
                import_config_data = {k: v for k, v in import_data.items()
                                    if k not in ['version', 'created', 'modified', 'exported']}

                merged_data = deep_merge(existing_dict, import_config_data)
                config_data = merged_data
            else:
                # Replace completely
                config_data = {k: v for k, v in import_data.items()
                             if k not in ['version', 'created', 'modified', 'exported']}

            # Convert to config objects
            if PYDANTIC_AVAILABLE:
                self._config = AppConfig(
                    data_sources=DataSourceConfig(**config_data.get('data_sources', {})),
                    display=DisplayConfig(**config_data.get('display', {})),
                    cost=CostConfig(**config_data.get('cost', {})),
                    export=ExportConfig(**config_data.get('export', {})),
                    window_state=config_data.get('window_state', {})
                )
            else:
                data_sources_data = config_data.get('data_sources', {})
                if 'custom_paths' not in data_sources_data:
                    data_sources_data['custom_paths'] = []

                self._config = AppConfig(
                    data_sources=DataSourceConfig(**data_sources_data),
                    display=DisplayConfig(**config_data.get('display', {})),
                    cost=CostConfig(**config_data.get('cost', {})),
                    export=ExportConfig(**config_data.get('export', {})),
                    window_state=config_data.get('window_state', {})
                )

            # Save the imported configuration
            result = self.save_config()

            if result:
                action = "merged" if merge else "imported"
                logger.info(f"Configuration {action} successfully from {import_path}")

            return result

        except ConfigValidationError:
            # Re-raise validation errors
            raise

        except Exception as e:
            logger.error(f"Error importing config: {e}")
            return False

    def validate_current_config(self) -> bool:
        """
        Validate the current configuration.

        Returns:
            True if valid, False otherwise
        """
        try:
            if self._config is None:
                return False

            if PYDANTIC_AVAILABLE and hasattr(self._config, 'dict'):
                config_dict = self._config.dict()
            else:
                config_dict = asdict(self._config)

            config_dict['version'] = self.CONFIG_VERSION
            return self._validate_config_data(config_dict)

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def get_config_info(self) -> Dict[str, Any]:
        """
        Get information about the current configuration.

        Returns:
            Dictionary containing configuration metadata and statistics
        """
        info = {
            "config_file": str(self.config_file),
            "config_dir": str(self.config_dir),
            "version": self.CONFIG_VERSION,
            "exists": self.config_file.exists(),
            "valid": self.validate_current_config(),
            "pydantic_available": PYDANTIC_AVAILABLE,
            "jsonschema_available": JSONSCHEMA_AVAILABLE,
            "platformdirs_available": PLATFORMDIRS_AVAILABLE
        }

        if self.config_file.exists():
            try:
                stat = self.config_file.stat()
                info.update({
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
            except Exception:
                pass

        # Count backup files
        try:
            backup_pattern = f"{self.CONFIG_FILENAME}{self.BACKUP_SUFFIX}_*"
            backup_files = list(self.config_dir.glob(backup_pattern))
            info["backup_count"] = len(backup_files)
        except Exception:
            info["backup_count"] = 0

        return info