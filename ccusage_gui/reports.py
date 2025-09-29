"""
Report generation module for Mr. The Guru - Claude Code Usage

Generates various types of usage reports based on Claude Code data.
Supports daily, monthly, weekly, session, and blocks reports.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, NamedTuple, Any
from collections import defaultdict
from dataclasses import dataclass
import calendar

from .data_loader import UsageRecord
from .cost_calculator import CostCalculator

logger = logging.getLogger(__name__)


@dataclass
class ReportEntry:
    """Base class for report entries."""
    date: datetime
    total_tokens: int
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    total_cost: float
    model_breakdown: Dict[str, Dict[str, any]]
    record_count: int


@dataclass
class SessionReportEntry:
    """Report entry for session-based reports."""
    session_id: str
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    total_tokens: int
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    total_cost: float
    models_used: List[str]
    message_count: int
    project_id: Optional[str] = None
    project_name: Optional[str] = None


@dataclass
class BlockReportEntry:
    """Report entry for 5-hour blocks reports."""
    block_start: datetime
    block_end: datetime
    block_number: int
    total_tokens: int
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    total_cost: float
    sessions_count: int
    active_duration_minutes: float
    is_current_block: bool = False


class ReportGenerator:
    """
    Generates various types of usage reports from Claude Code data.

    Supports multiple report types:
    - Daily: Usage aggregated by calendar date
    - Monthly: Monthly summaries with trends
    - Weekly: Weekly breakdown with configurable start day
    - Session: Individual conversation analysis
    - Blocks: 5-hour billing window tracking
    """

    def __init__(self, cost_calculator: CostCalculator):
        """
        Initialize the report generator.

        Args:
            cost_calculator: Cost calculator instance for pricing
        """
        self.cost_calculator = cost_calculator

    def generate_daily_report(self,
                            records: List[UsageRecord],
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None,
                            order: str = "desc") -> List[ReportEntry]:
        """
        Generate daily usage report.

        Args:
            records: Usage records to analyze
            start_date: Filter records after this date
            end_date: Filter records before this date
            order: Sort order ('asc' or 'desc')

        Returns:
            List of daily report entries
        """
        # Filter records by date range
        filtered_records = self._filter_by_date_range(records, start_date, end_date)

        # Group by date
        daily_groups = defaultdict(list)
        for record in filtered_records:
            date_key = record.timestamp.date()
            daily_groups[date_key].append(record)

        # Generate report entries
        report_entries = []
        for date, day_records in daily_groups.items():
            entry = self._create_report_entry(
                datetime.combine(date, datetime.min.time()),
                day_records
            )
            report_entries.append(entry)

        # Sort by date
        reverse = (order == "desc")
        report_entries.sort(key=lambda x: x.date, reverse=reverse)

        return report_entries

    def generate_monthly_report(self,
                              records: List[UsageRecord],
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None,
                              order: str = "desc") -> List[ReportEntry]:
        """
        Generate monthly usage report.

        Args:
            records: Usage records to analyze
            start_date: Filter records after this date
            end_date: Filter records before this date
            order: Sort order ('asc' or 'desc')

        Returns:
            List of monthly report entries
        """
        # Filter records by date range
        filtered_records = self._filter_by_date_range(records, start_date, end_date)

        # Group by month
        monthly_groups = defaultdict(list)
        for record in filtered_records:
            month_key = (record.timestamp.year, record.timestamp.month)
            monthly_groups[month_key].append(record)

        # Generate report entries
        report_entries = []
        for (year, month), month_records in monthly_groups.items():
            month_start = datetime(year, month, 1)
            entry = self._create_report_entry(month_start, month_records)
            report_entries.append(entry)

        # Sort by date
        reverse = (order == "desc")
        report_entries.sort(key=lambda x: x.date, reverse=reverse)

        return report_entries

    def generate_weekly_report(self,
                             records: List[UsageRecord],
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             week_start_day: int = 0,  # 0 = Monday
                             order: str = "desc") -> List[ReportEntry]:
        """
        Generate weekly usage report.

        Args:
            records: Usage records to analyze
            start_date: Filter records after this date
            end_date: Filter records before this date
            week_start_day: Day of week to start (0=Monday, 6=Sunday)
            order: Sort order ('asc' or 'desc')

        Returns:
            List of weekly report entries
        """
        # Filter records by date range
        filtered_records = self._filter_by_date_range(records, start_date, end_date)

        # Group by week
        weekly_groups = defaultdict(list)
        for record in filtered_records:
            week_start = self._get_week_start(record.timestamp, week_start_day)
            weekly_groups[week_start].append(record)

        # Generate report entries
        report_entries = []
        for week_start, week_records in weekly_groups.items():
            entry = self._create_report_entry(week_start, week_records)
            report_entries.append(entry)

        # Sort by date
        reverse = (order == "desc")
        report_entries.sort(key=lambda x: x.date, reverse=reverse)

        return report_entries

    def generate_session_report(self,
                              records: List[UsageRecord],
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None,
                              order: str = "desc") -> List[SessionReportEntry]:
        """
        Generate session-based usage report.

        Args:
            records: Usage records to analyze
            start_date: Filter records after this date
            end_date: Filter records before this date
            order: Sort order ('asc' or 'desc')

        Returns:
            List of session report entries
        """
        # Filter records by date range
        filtered_records = self._filter_by_date_range(records, start_date, end_date)

        # Group by session
        session_groups = defaultdict(list)
        for record in filtered_records:
            session_groups[record.session_id].append(record)

        # Generate session entries
        session_entries = []
        for session_id, session_records in session_groups.items():
            # Sort records by timestamp
            session_records.sort(key=lambda x: x.timestamp)

            # Calculate session metrics
            start_time = session_records[0].timestamp
            end_time = session_records[-1].timestamp
            duration = (end_time - start_time).total_seconds() / 60  # minutes

            # Calculate totals
            total_tokens = sum(r.total_tokens for r in session_records)
            input_tokens = sum(r.input_tokens for r in session_records)
            output_tokens = sum(r.output_tokens for r in session_records)
            cache_creation_tokens = sum(r.cache_creation_tokens for r in session_records)
            cache_read_tokens = sum(r.cache_read_tokens for r in session_records)

            # Calculate cost
            cost_breakdown = self.cost_calculator.calculate_total_cost(session_records)
            total_cost = cost_breakdown['total_cost']

            # Get unique models
            models_used = list(set(r.model for r in session_records))

            # Get project info (use first record's project info)
            project_id = session_records[0].project_id
            project_name = session_records[0].project_name

            entry = SessionReportEntry(
                session_id=session_id,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=duration,
                total_tokens=total_tokens,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_creation_tokens=cache_creation_tokens,
                cache_read_tokens=cache_read_tokens,
                total_cost=total_cost,
                models_used=models_used,
                message_count=len(session_records),
                project_id=project_id,
                project_name=project_name
            )

            session_entries.append(entry)

        # Sort by start time
        reverse = (order == "desc")
        session_entries.sort(key=lambda x: x.start_time, reverse=reverse)

        return session_entries

    def generate_blocks_report(self,
                             records: List[UsageRecord],
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             order: str = "desc") -> List[BlockReportEntry]:
        """
        Generate 5-hour billing blocks report.

        Args:
            records: Usage records to analyze
            start_date: Filter records after this date
            end_date: Filter records before this date
            order: Sort order ('asc' or 'desc')

        Returns:
            List of 5-hour block report entries
        """
        # Filter records by date range
        filtered_records = self._filter_by_date_range(records, start_date, end_date)

        # Group by 5-hour blocks
        block_groups = defaultdict(list)
        for record in filtered_records:
            block_start = self._get_block_start(record.timestamp)
            block_groups[block_start].append(record)

        # Generate block entries
        block_entries = []
        current_time = datetime.now()

        for block_start, block_records in block_groups.items():
            block_end = block_start + timedelta(hours=5)

            # Calculate session metrics
            session_ids = set(r.session_id for r in block_records)
            sessions_count = len(session_ids)

            # Calculate active duration (time between first and last activity)
            if len(block_records) > 1:
                sorted_records = sorted(block_records, key=lambda x: x.timestamp)
                active_duration = (sorted_records[-1].timestamp - sorted_records[0].timestamp).total_seconds() / 60
            else:
                active_duration = 0.0

            # Calculate totals
            total_tokens = sum(r.total_tokens for r in block_records)
            input_tokens = sum(r.input_tokens for r in block_records)
            output_tokens = sum(r.output_tokens for r in block_records)
            cache_creation_tokens = sum(r.cache_creation_tokens for r in block_records)
            cache_read_tokens = sum(r.cache_read_tokens for r in block_records)

            # Calculate cost
            cost_breakdown = self.cost_calculator.calculate_total_cost(block_records)
            total_cost = cost_breakdown['total_cost']

            # Determine if this is the current active block
            is_current = block_start <= current_time < block_end

            # Calculate block number (hours since epoch / 5)
            epoch = datetime(1970, 1, 1)
            hours_since_epoch = (block_start - epoch).total_seconds() / 3600
            block_number = int(hours_since_epoch // 5)

            entry = BlockReportEntry(
                block_start=block_start,
                block_end=block_end,
                block_number=block_number,
                total_tokens=total_tokens,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_creation_tokens=cache_creation_tokens,
                cache_read_tokens=cache_read_tokens,
                total_cost=total_cost,
                sessions_count=sessions_count,
                active_duration_minutes=active_duration,
                is_current_block=is_current
            )

            block_entries.append(entry)

        # Sort by block start time
        reverse = (order == "desc")
        block_entries.sort(key=lambda x: x.block_start, reverse=reverse)

        return block_entries

    def _filter_by_date_range(self,
                            records: List[UsageRecord],
                            start_date: Optional[datetime],
                            end_date: Optional[datetime]) -> List[UsageRecord]:
        """Filter records by date range."""
        filtered = records

        if start_date:
            filtered = [r for r in filtered if r.timestamp >= start_date]

        if end_date:
            filtered = [r for r in filtered if r.timestamp <= end_date]

        return filtered

    def _create_report_entry(self, date: datetime, records: List[UsageRecord]) -> ReportEntry:
        """Create a report entry from a group of records."""
        # Calculate totals
        total_tokens = sum(r.total_tokens for r in records)
        input_tokens = sum(r.input_tokens for r in records)
        output_tokens = sum(r.output_tokens for r in records)
        cache_creation_tokens = sum(r.cache_creation_tokens for r in records)
        cache_read_tokens = sum(r.cache_read_tokens for r in records)

        # Calculate cost
        cost_breakdown = self.cost_calculator.calculate_total_cost(records)
        total_cost = cost_breakdown['total_cost']

        # Create model breakdown
        model_breakdown = defaultdict(lambda: {
            'tokens': 0,
            'input_tokens': 0,
            'output_tokens': 0,
            'cache_creation_tokens': 0,
            'cache_read_tokens': 0,
            'cost': 0.0,
            'count': 0
        })

        for record in records:
            model = record.model
            model_breakdown[model]['tokens'] += record.total_tokens
            model_breakdown[model]['input_tokens'] += record.input_tokens
            model_breakdown[model]['output_tokens'] += record.output_tokens
            model_breakdown[model]['cache_creation_tokens'] += record.cache_creation_tokens
            model_breakdown[model]['cache_read_tokens'] += record.cache_read_tokens
            model_breakdown[model]['count'] += 1

            # Calculate cost for this record
            cost_calc = self.cost_calculator.calculate_cost(record)
            if cost_calc:
                model_breakdown[model]['cost'] += cost_calc.total_cost

        return ReportEntry(
            date=date,
            total_tokens=total_tokens,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_creation_tokens=cache_creation_tokens,
            cache_read_tokens=cache_read_tokens,
            total_cost=total_cost,
            model_breakdown=dict(model_breakdown),
            record_count=len(records)
        )

    def _get_week_start(self, date: datetime, week_start_day: int) -> datetime:
        """Get the start of the week for a given date."""
        days_since_start = (date.weekday() - week_start_day) % 7
        week_start = date - timedelta(days=days_since_start)
        return datetime.combine(week_start.date(), datetime.min.time())

    def _get_block_start(self, timestamp: datetime) -> datetime:
        """Get the start of the 5-hour block for a given timestamp."""
        # Round down to the nearest 5-hour boundary
        hour = timestamp.hour
        block_hour = (hour // 5) * 5

        return datetime(
            timestamp.year,
            timestamp.month,
            timestamp.day,
            block_hour,
            0, 0
        )

    def export_to_json(self, report_data: List[Any]) -> Dict[str, Any]:
        """
        Export report data to JSON format.

        Args:
            report_data: Report entries to export

        Returns:
            Dictionary suitable for JSON serialization
        """
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'report_type': type(report_data[0]).__name__ if report_data else 'empty',
            'entry_count': len(report_data),
            'entries': []
        }

        for entry in report_data:
            if isinstance(entry, ReportEntry):
                export_data['entries'].append({
                    'date': entry.date.isoformat(),
                    'total_tokens': entry.total_tokens,
                    'input_tokens': entry.input_tokens,
                    'output_tokens': entry.output_tokens,
                    'cache_creation_tokens': entry.cache_creation_tokens,
                    'cache_read_tokens': entry.cache_read_tokens,
                    'total_cost': entry.total_cost,
                    'model_breakdown': entry.model_breakdown,
                    'record_count': entry.record_count
                })

            elif isinstance(entry, SessionReportEntry):
                export_data['entries'].append({
                    'session_id': entry.session_id,
                    'start_time': entry.start_time.isoformat(),
                    'end_time': entry.end_time.isoformat(),
                    'duration_minutes': entry.duration_minutes,
                    'total_tokens': entry.total_tokens,
                    'input_tokens': entry.input_tokens,
                    'output_tokens': entry.output_tokens,
                    'cache_creation_tokens': entry.cache_creation_tokens,
                    'cache_read_tokens': entry.cache_read_tokens,
                    'total_cost': entry.total_cost,
                    'models_used': entry.models_used,
                    'message_count': entry.message_count,
                    'project_id': entry.project_id,
                    'project_name': entry.project_name
                })

            elif isinstance(entry, BlockReportEntry):
                export_data['entries'].append({
                    'block_start': entry.block_start.isoformat(),
                    'block_end': entry.block_end.isoformat(),
                    'block_number': entry.block_number,
                    'total_tokens': entry.total_tokens,
                    'input_tokens': entry.input_tokens,
                    'output_tokens': entry.output_tokens,
                    'cache_creation_tokens': entry.cache_creation_tokens,
                    'cache_read_tokens': entry.cache_read_tokens,
                    'total_cost': entry.total_cost,
                    'sessions_count': entry.sessions_count,
                    'active_duration_minutes': entry.active_duration_minutes,
                    'is_current_block': entry.is_current_block
                })

        return export_data

    def export_to_csv(self, report_data: List[Any]) -> str:
        """
        Export report data to CSV format.

        Args:
            report_data: Report entries to export

        Returns:
            CSV string
        """
        if not report_data:
            return ""

        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Write headers based on report type
        if isinstance(report_data[0], ReportEntry):
            writer.writerow([
                'Date', 'Total Tokens', 'Input Tokens', 'Output Tokens',
                'Cache Creation Tokens', 'Cache Read Tokens', 'Total Cost',
                'Record Count', 'Models Used'
            ])

            for entry in report_data:
                models_used = ', '.join(entry.model_breakdown.keys())
                writer.writerow([
                    entry.date.strftime('%Y-%m-%d'),
                    entry.total_tokens,
                    entry.input_tokens,
                    entry.output_tokens,
                    entry.cache_creation_tokens,
                    entry.cache_read_tokens,
                    f"{entry.total_cost:.6f}",
                    entry.record_count,
                    models_used
                ])

        elif isinstance(report_data[0], SessionReportEntry):
            writer.writerow([
                'Session ID', 'Start Time', 'End Time', 'Duration (min)',
                'Total Tokens', 'Input Tokens', 'Output Tokens',
                'Cache Creation Tokens', 'Cache Read Tokens', 'Total Cost',
                'Models Used', 'Message Count', 'Project ID', 'Project Name'
            ])

            for entry in report_data:
                writer.writerow([
                    entry.session_id,
                    entry.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    entry.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    f"{entry.duration_minutes:.2f}",
                    entry.total_tokens,
                    entry.input_tokens,
                    entry.output_tokens,
                    entry.cache_creation_tokens,
                    entry.cache_read_tokens,
                    f"{entry.total_cost:.6f}",
                    ', '.join(entry.models_used),
                    entry.message_count,
                    entry.project_id or '',
                    entry.project_name or ''
                ])

        elif isinstance(report_data[0], BlockReportEntry):
            writer.writerow([
                'Block Start', 'Block End', 'Block Number', 'Total Tokens',
                'Input Tokens', 'Output Tokens', 'Cache Creation Tokens',
                'Cache Read Tokens', 'Total Cost', 'Sessions Count',
                'Active Duration (min)', 'Is Current Block'
            ])

            for entry in report_data:
                writer.writerow([
                    entry.block_start.strftime('%Y-%m-%d %H:%M:%S'),
                    entry.block_end.strftime('%Y-%m-%d %H:%M:%S'),
                    entry.block_number,
                    entry.total_tokens,
                    entry.input_tokens,
                    entry.output_tokens,
                    entry.cache_creation_tokens,
                    entry.cache_read_tokens,
                    f"{entry.total_cost:.6f}",
                    entry.sessions_count,
                    f"{entry.active_duration_minutes:.2f}",
                    entry.is_current_block
                ])

        return output.getvalue()