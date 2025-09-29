# ccusage GUI

A Windows-focused GUI application for analyzing Claude Code usage data, based on the original [ccusage CLI tool](https://github.com/ryoppippi/ccusage).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## 🚀 Features

- **📊 Usage Reports**: Daily, monthly, weekly, session, and 5-hour blocks reports
- **💰 Cost Tracking**: Calculate token usage costs with real-time pricing
- **🎯 Smart Filtering**: Filter by date ranges, projects, and Claude models
- **📱 User-Friendly GUI**: Intuitive Windows application interface
- **📄 Export Options**: Export data to JSON and CSV formats
- **🔍 Project Analysis**: Group usage by Claude Code projects
- **⚙️ Flexible Configuration**: Support for multiple Claude installations

## 📋 Requirements

- Python 3.10 or higher
- Windows OS
- Claude Code (for generating usage data)

## 🛠️ Installation

### Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Budgulick/ccusage_gui.git
   cd ccusage_gui
   ```

2. **Set up virtual environment:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   python main.py
   ```

### Standalone Executable (Coming Soon)

We're working on a standalone `.exe` file that won't require Python installation.

## 📖 Usage

### Data Sources

The application automatically reads Claude Code usage data from:

- `%USERPROFILE%\.config\claude\projects\` (primary)
- `%USERPROFILE%\.claude\projects\` (fallback)

### Available Reports

- **Daily Report**: View token usage and costs by day
- **Monthly Report**: Aggregated monthly usage statistics
- **Weekly Report**: Weekly usage breakdown
- **Session Report**: Usage grouped by conversation sessions
- **Blocks Report**: 5-hour billing window analysis

### Filtering Options

- **Date Range**: Filter reports by start and end dates
- **Projects**: Focus on specific Claude Code projects
- **Models**: Filter by Claude model types (Opus, Sonnet, etc.)

## 🎯 Roadmap

- [ ] GUI Interface Implementation
- [ ] Core Data Loading Functions
- [ ] Report Generation System
- [ ] Export Functionality
- [ ] Advanced Filtering
- [ ] Standalone Executable
- [ ] Auto-Update Feature
- [ ] Data Visualization Charts

## 🙏 Attribution

This project is based on the excellent [ccusage CLI tool](https://github.com/ryoppippi/ccusage) created by [@ryoppippi](https://github.com/ryoppippi).

**Original Project**: <https://github.com/ryoppippi/ccusage>
**License**: MIT
**Author**: @ryoppippi

We extend our sincere gratitude to the original author for creating such a valuable tool for the Claude Code community. This GUI version aims to make the functionality more accessible to Windows users who prefer graphical interfaces.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The original ccusage project is also under MIT License: <https://github.com/ryoppippi/ccusage/blob/main/LICENSE>

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/Budgulick/ccusage_gui/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide detailed information about your setup and the issue

## ⭐ Acknowledgments

- [@ryoppippi](https://github.com/ryoppippi) for the original ccusage CLI tool
- The Claude Code community for valuable feedback and testing
- All contributors who help improve this project

---

**Note**: This is an independent GUI implementation inspired by ccusage. For the original CLI tool, visit: <https://github.com/ryoppippi/ccusage>
