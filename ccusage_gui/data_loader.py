"""
Data loading module for Mr. The Guru - Claude Code Usage

Handles reading and parsing Claude Code JSONL files from local directories.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Iterator, NamedTuple
from datetime import datetime
import glob

logger = logging.getLogger(__name__)


class UsageRecord(NamedTuple):
    """Represents a single usage record from Claude data."""
    timestamp: datetime
    session_id: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    message_id: Optional[str] = None
    conversation_id: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        """Calculate total tokens for this record."""
        return (self.input_tokens + self.output_tokens +
                self.cache_creation_tokens + self.cache_read_tokens)


class DataLoader:
    """
    Loads and parses Claude Code usage data from JSONL files.

    This class handles:
    - Discovery of Claude data directories
    - Reading JSONL files with usage data
    - Parsing and normalizing usage records
    - Error handling for malformed data
    """

    def __init__(self, data_paths: List[str]):
        """
        Initialize the data loader.

        Args:
            data_paths: List of directory paths to search for Claude data
        """
        self.data_paths = [Path(p) for p in data_paths if os.path.exists(p)]
        self._usage_cache: Optional[List[UsageRecord]] = None

    def discover_data_files(self) -> List[Path]:
        """
        Discover all JSONL files in configured data directories.

        Returns:
            List of JSONL file paths containing Claude usage data
        """
        files = []

        for data_path in self.data_paths:
            if not data_path.exists():
                logger.warning(f"Data path does not exist: {data_path}")
                continue

            try:
                # Look for .jsonl files recursively
                jsonl_files = list(data_path.rglob("*.jsonl"))

                # Filter for files that look like Claude usage data
                for file_path in jsonl_files:
                    if self._is_claude_usage_file(file_path):
                        files.append(file_path)

                logger.info(f"Found {len(jsonl_files)} JSONL files in {data_path}")

            except Exception as e:
                logger.error(f"Error scanning directory {data_path}: {e}")

        logger.info(f"Discovered {len(files)} Claude usage files total")
        return files

    def _is_claude_usage_file(self, file_path: Path) -> bool:
        """
        Check if a JSONL file contains Claude usage data.

        Args:
            file_path: Path to the JSONL file

        Returns:
            True if the file appears to contain Claude usage data
        """
        try:
            # Read first few lines to check structure
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= 3:  # Check first 3 lines
                        break

                    try:
                        data = json.loads(line.strip())

                        # Check for expected Claude usage data fields
                        if self._has_usage_fields(data):
                            return True

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            logger.debug(f"Error checking file {file_path}: {e}")

        return False

    def _has_usage_fields(self, data: Dict) -> bool:
        """
        Check if a JSON object has expected Claude usage fields.

        Args:
            data: JSON data to check

        Returns:
            True if data appears to be Claude usage data
        """
        # Check for common Claude usage data fields
        usage_indicators = [
            'usage',
            'model',
            'tokens',
            'input_tokens',
            'output_tokens',
            'created_at',
            'timestamp'
        ]

        # Look for nested usage data
        if 'usage' in data:
            usage_data = data['usage']
            if isinstance(usage_data, dict):
                token_fields = ['input_tokens', 'output_tokens', 'cache_creation_tokens', 'cache_read_tokens']
                return any(field in usage_data for field in token_fields)

        # Look for direct token fields
        return any(field in data for field in usage_indicators)

    def load_usage_data(self, force_reload: bool = False) -> List[UsageRecord]:
        """
        Load all Claude usage data from discovered files.

        Args:
            force_reload: If True, reload data even if cached

        Returns:
            List of usage records sorted by timestamp
        """
        if self._usage_cache is not None and not force_reload:
            return self._usage_cache

        logger.info("Loading Claude usage data...")

        all_records = []
        data_files = self.discover_data_files()

        for file_path in data_files:
            try:
                records = self._parse_jsonl_file(file_path)
                all_records.extend(records)
                logger.debug(f"Loaded {len(records)} records from {file_path}")

            except Exception as e:
                logger.error(f"Error loading file {file_path}: {e}")

        # Sort by timestamp
        all_records.sort(key=lambda r: r.timestamp)

        self._usage_cache = all_records
        logger.info(f"Loaded {len(all_records)} total usage records")

        return all_records

    def _parse_jsonl_file(self, file_path: Path) -> List[UsageRecord]:
        """
        Parse a single JSONL file and extract usage records.

        Args:
            file_path: Path to the JSONL file

        Returns:
            List of usage records from the file
        """
        records = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    record = self._parse_usage_record(data, file_path)

                    if record:
                        records.append(record)

                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON at {file_path}:{line_num}: {e}")
                except Exception as e:
                    logger.warning(f"Error parsing record at {file_path}:{line_num}: {e}")

        return records

    def _parse_usage_record(self, data: Dict, file_path: Path) -> Optional[UsageRecord]:
        """
        Parse a single JSON record into a UsageRecord.

        Args:
            data: JSON data from JSONL line
            file_path: Source file path (for context)

        Returns:
            UsageRecord if parsing successful, None otherwise
        """
        try:
            # Extract timestamp
            timestamp = self._extract_timestamp(data)
            if not timestamp:
                return None

            # Extract model information
            model = self._extract_model(data)
            if not model:
                return None

            # Extract token usage
            tokens = self._extract_tokens(data)
            if tokens is None:
                return None

            # Extract session/conversation info
            session_id = self._extract_session_id(data)

            # Extract project information
            project_info = self._extract_project_info(data, file_path)

            return UsageRecord(
                timestamp=timestamp,
                session_id=session_id,
                model=model,
                input_tokens=tokens.get('input_tokens', 0),
                output_tokens=tokens.get('output_tokens', 0),
                cache_creation_tokens=tokens.get('cache_creation_tokens', 0),
                cache_read_tokens=tokens.get('cache_read_tokens', 0),
                project_id=project_info.get('id'),
                project_name=project_info.get('name'),
                message_id=data.get('id'),
                conversation_id=data.get('conversation_id')
            )

        except Exception as e:
            logger.debug(f"Error parsing usage record: {e}")
            return None

    def _extract_timestamp(self, data: Dict) -> Optional[datetime]:
        """Extract timestamp from usage data."""
        timestamp_fields = ['timestamp', 'created_at', 'time']

        for field in timestamp_fields:
            if field in data:
                try:
                    timestamp_str = data[field]
                    # Handle different timestamp formats
                    if isinstance(timestamp_str, str):
                        # ISO format with timezone
                        if timestamp_str.endswith('Z'):
                            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        # ISO format
                        return datetime.fromisoformat(timestamp_str)
                    elif isinstance(timestamp_str, (int, float)):
                        # Unix timestamp
                        return datetime.fromtimestamp(timestamp_str)
                except Exception:
                    continue

        return None

    def _extract_model(self, data: Dict) -> Optional[str]:
        """Extract model name from usage data."""
        # Check message.model first (Claude Code format)
        if 'message' in data and isinstance(data['message'], dict):
            if 'model' in data['message'] and data['message']['model']:
                return str(data['message']['model'])

        # Fallback to direct model fields
        model_fields = ['model', 'model_name']
        for field in model_fields:
            if field in data and data[field]:
                return str(data[field])

        return None

    def _extract_tokens(self, data: Dict) -> Optional[Dict[str, int]]:
        """Extract token usage information from usage data."""
        # Check message.usage first (Claude Code format)
        if 'message' in data and isinstance(data['message'], dict):
            if 'usage' in data['message'] and isinstance(data['message']['usage'], dict):
                usage = data['message']['usage']
                tokens = {
                    'input_tokens': int(usage.get('input_tokens', 0)),
                    'output_tokens': int(usage.get('output_tokens', 0)),
                    'cache_creation_tokens': int(usage.get('cache_creation_input_tokens', 0)),
                    'cache_read_tokens': int(usage.get('cache_read_input_tokens', 0))
                }
                return tokens

        # Look for direct usage object
        if 'usage' in data and isinstance(data['usage'], dict):
            usage = data['usage']
            tokens = {}

            # Standard token fields
            token_fields = {
                'input_tokens': ['input_tokens', 'prompt_tokens'],
                'output_tokens': ['output_tokens', 'completion_tokens'],
                'cache_creation_tokens': ['cache_creation_tokens', 'cache_creation_input_tokens'],
                'cache_read_tokens': ['cache_read_tokens', 'cache_read_input_tokens']
            }

            for key, possible_fields in token_fields.items():
                for field in possible_fields:
                    if field in usage:
                        tokens[key] = int(usage[field])
                        break
                else:
                    tokens[key] = 0

            return tokens

        # Direct token fields
        direct_fields = ['input_tokens', 'output_tokens', 'total_tokens']
        if any(field in data for field in direct_fields):
            return {
                'input_tokens': int(data.get('input_tokens', 0)),
                'output_tokens': int(data.get('output_tokens', 0)),
                'cache_creation_tokens': int(data.get('cache_creation_tokens', 0)),
                'cache_read_tokens': int(data.get('cache_read_tokens', 0))
            }

        return None

    def _extract_session_id(self, data: Dict) -> str:
        """Extract session ID from usage data."""
        # Check sessionId first (Claude Code format)
        if 'sessionId' in data and data['sessionId']:
            return str(data['sessionId'])

        # Fallback to other fields
        session_fields = ['session_id', 'conversation_id', 'thread_id', 'id']
        for field in session_fields:
            if field in data and data[field]:
                return str(data[field])

        return "unknown"

    def _extract_project_info(self, data: Dict, file_path: Path) -> Dict[str, Optional[str]]:
        """Extract project information from usage data and file path."""
        project_info = {'id': None, 'name': None}

        # Try to get project info from data.cwd (Claude Code format)
        if 'cwd' in data and data['cwd']:
            cwd = data['cwd']
            # Extract project name from cwd path
            cwd_path = Path(cwd)
            project_info['name'] = cwd_path.name
            project_info['id'] = str(cwd_path)

        # Try to get project info from data
        if 'project' in data:
            project = data['project']
            if isinstance(project, dict):
                project_info['id'] = project.get('id')
                project_info['name'] = project.get('name')
            else:
                project_info['id'] = str(project)

        # Try to infer from file path (parent directory name in .claude/projects)
        if not project_info['name']:
            parent_dir = file_path.parent.name
            if parent_dir and parent_dir != 'projects':
                # Convert directory name format: E--Projects-ccusage-gui -> E:\Projects\ccusage-gui
                project_info['name'] = parent_dir.replace('--', ':\\', 1).replace('-', ' ', 1).replace('-', '/')
                if not project_info['id']:
                    project_info['id'] = parent_dir

        return project_info

    def get_projects(self) -> List[Dict[str, str]]:
        """
        Get list of all projects found in the data.

        Returns:
            List of project dictionaries with 'id' and 'name' keys
        """
        records = self.load_usage_data()
        projects = {}

        for record in records:
            if record.project_id:
                projects[record.project_id] = {
                    'id': record.project_id,
                    'name': record.project_name or record.project_id
                }

        return list(projects.values())

    def get_models(self) -> List[str]:
        """
        Get list of all models found in the data.

        Returns:
            List of unique model names
        """
        records = self.load_usage_data()
        models = set(record.model for record in records)
        return sorted(models)

    def get_date_range(self) -> tuple[Optional[datetime], Optional[datetime]]:
        """
        Get the date range of available data.

        Returns:
            Tuple of (earliest_date, latest_date)
        """
        records = self.load_usage_data()

        if not records:
            return None, None

        timestamps = [record.timestamp for record in records]
        return min(timestamps), max(timestamps)

    def filter_records(self,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      project_ids: Optional[List[str]] = None,
                      models: Optional[List[str]] = None) -> List[UsageRecord]:
        """
        Filter usage records by various criteria.

        Args:
            start_date: Filter records after this date
            end_date: Filter records before this date
            project_ids: Filter by project IDs
            models: Filter by model names

        Returns:
            Filtered list of usage records
        """
        records = self.load_usage_data()
        filtered = records

        if start_date:
            filtered = [r for r in filtered if r.timestamp >= start_date]

        if end_date:
            filtered = [r for r in filtered if r.timestamp <= end_date]

        if project_ids:
            filtered = [r for r in filtered if r.project_id in project_ids]

        if models:
            filtered = [r for r in filtered if r.model in models]

        return filtered

    def clear_cache(self):
        """Clear the cached usage data to force reload."""
        self._usage_cache = None