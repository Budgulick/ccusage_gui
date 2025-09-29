# CLAUDE.md - ccusage GUI Project

This file provides guidance to Claude Code when working with the ccusage GUI project.

## Project Overview

**ccusage GUI** is a Windows-focused GUI application that provides the same functionality as the original [ccusage CLI tool](https://github.com/ryoppippi/ccusage) but with a user-friendly graphical interface.

### What this project does

- Reads Claude Code usage data from local JSONL files
- Provides daily, monthly, weekly, session, and blocks usage reports
- Calculates token usage and costs
- Offers filtering by date ranges and projects
- Exports data in various formats (JSON, CSV)

### Project Structure

```text
ccusage_gui/
├── .gitignore          # Git ignore file
├── CLAUDE.md           # This file (Claude Code instructions)
├── README.md           # Project documentation
├── LICENSE             # MIT License
├── requirements.txt    # Python dependencies
├── setup.py           # Python package setup
├── ccusage_gui/       # Main Python package
│   ├── __init__.py
│   ├── data_loader.py     # Read Claude JSONL files
│   ├── cost_calculator.py # Calculate costs and tokens
│   ├── reports.py         # Generate reports
│   ├── gui.py            # GUI interface
│   ├── config.py         # Configuration
│   └── utils.py          # Utility functions
└── main.py            # Entry point
```

## Development Guidelines

### Python Style

- Use Python 3.10+ features
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write docstrings for modules, classes, and functions

### Dependencies

- Keep dependencies minimal and well-justified
- Prefer standard library when possible
- Use virtual environments for development

### GUI Framework

- Use tkinter for cross-platform compatibility (built into Python)
- Consider PyQt6 if more advanced features are needed
- Ensure Windows-specific optimizations

### Data Handling

- Read JSONL files from Claude directories:
  - `%USERPROFILE%\.claude\projects\`
  - `%USERPROFILE%\.config\claude\projects\`
- Handle malformed data gracefully
- Support multiple Claude installations

### Features to Implement

1. **Data Loading**: Parse Claude JSONL files
2. **Reports**: Daily, monthly, weekly, session, blocks
3. **GUI Interface**: User-friendly Windows application
4. **Filtering**: Date ranges, projects, models
5. **Export**: JSON, CSV formats
6. **Cost Calculation**: Token-based pricing

## Attribution

This project is based on the excellent [ccusage CLI tool](https://github.com/ryoppippi/ccusage) by [@ryoppippi](https://github.com/ryoppippi). We extend our gratitude for the original implementation and design.

## Development Commands

**Setup:**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Run:**

```bash
python main.py
```

**Build (future):**

```bash
pyinstaller --onefile --windowed main.py
```

## File Locations

### Claude Data Directories (Windows)

- Primary: `%USERPROFILE%\.config\claude\projects\`
- Secondary: `%USERPROFILE%\.claude\projects\`

### Configuration

- Store user preferences in `%APPDATA%\ccusage-gui\config.json`

## Testing

- Test with sample JSONL data
- Verify all report types work correctly
- Test date filtering and project filtering
- Ensure GUI is responsive and user-friendly
- Test on different Windows versions

## Future Enhancements

- Auto-update functionality
- Integration with Claude Desktop notifications
- Advanced filtering options
- Data visualization charts
- Export to Excel format
- Command-line interface alongside GUI
