"""
Quick test script to verify data loading from Claude directories.
"""
import os
import logging
from pathlib import Path
from ccusage_gui.data_loader import DataLoader
from ccusage_gui.config import ConfigManager

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def main():
    print("Testing Claude Code Usage Data Loading")
    print("=" * 60)

    # Initialize config
    config_mgr = ConfigManager()
    data_paths = config_mgr.get_claude_data_paths()

    print(f"\n1. Data Paths Configured:")
    for path in data_paths:
        exists = "[EXISTS]" if os.path.exists(path) else "[NOT FOUND]"
        print(f"   {path} {exists}")

    if not data_paths:
        print("   [ERROR] No valid data paths found!")
        return

    # Initialize data loader
    print(f"\n2. Initializing Data Loader...")
    loader = DataLoader(data_paths)

    # Discover files
    print(f"\n3. Discovering JSONL Files...")
    files = loader.discover_data_files()
    print(f"   Found {len(files)} Claude usage files")

    if files:
        print(f"\n   First 5 files:")
        for f in files[:5]:
            print(f"   - {f}")

    # Load usage data
    print(f"\n4. Loading Usage Data...")
    try:
        records = loader.load_usage_data()
        print(f"   [OK] Loaded {len(records)} usage records")

        if records:
            print(f"\n5. Data Summary:")

            # Total tokens
            total_tokens = sum(r.total_tokens for r in records)
            print(f"   Total Tokens: {total_tokens:,}")

            # Token breakdown
            total_input = sum(r.input_tokens for r in records)
            total_output = sum(r.output_tokens for r in records)
            total_cache_create = sum(r.cache_creation_tokens for r in records)
            total_cache_read = sum(r.cache_read_tokens for r in records)

            print(f"   - Input Tokens: {total_input:,}")
            print(f"   - Output Tokens: {total_output:,}")
            print(f"   - Cache Creation: {total_cache_create:,}")
            print(f"   - Cache Read: {total_cache_read:,}")

            # Date range
            start_date, end_date = loader.get_date_range()
            if start_date and end_date:
                print(f"\n   Date Range:")
                print(f"   - From: {start_date.strftime('%Y-%m-%d %H:%M')}")
                print(f"   - To:   {end_date.strftime('%Y-%m-%d %H:%M')}")

            # Sessions
            sessions = set(r.session_id for r in records)
            print(f"\n   Sessions: {len(sessions)}")

            # Models
            models = loader.get_models()
            print(f"\n   Models Used:")
            for model in models:
                count = len([r for r in records if r.model == model])
                print(f"   - {model}: {count} records")

            # Projects
            projects = loader.get_projects()
            print(f"\n   Projects:")
            for proj in projects[:5]:  # Show first 5
                name = proj.get('name', 'Unknown')
                print(f"   - {name}")
            if len(projects) > 5:
                print(f"   ... and {len(projects) - 5} more")

            # Sample records
            print(f"\n6. Sample Records (first 3):")
            for i, record in enumerate(records[:3], 1):
                print(f"\n   Record {i}:")
                print(f"   - Timestamp: {record.timestamp}")
                print(f"   - Model: {record.model}")
                print(f"   - Tokens: {record.total_tokens:,}")
                print(f"   - Session: {record.session_id[:8]}...")
                print(f"   - Project: {record.project_name or 'Unknown'}")
        else:
            print(f"   [WARNING] No usage records found in the files")

    except Exception as e:
        print(f"   [ERROR] Error loading data: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'=' * 60}")
    print("Test Complete!")

if __name__ == "__main__":
    main()