# ccusage GUI - Comprehensive Project Plan

## Project Overview

**Mr. The Guru - Claude Code Usage** is a Windows-focused GUI application that provides the same functionality as the original [ccusage CLI tool](https://github.com/ryoppippi/ccusage) but with a user-friendly graphical interface. This project will implement all core features while adding visual enhancements and improved user experience.

### Application Branding
- **Application Title**: "Mr. The Guru - Claude Code Usage"
- **Application Icon**: `E:\Projects\ccusage_gui\assets\mrtheguru_icon_main.ico`
- **Executable Name**: `mrtg_ccusage.exe`
- **Configuration File**: `mrtg_ccusage.json` (stored in application directory)

## Current Project Status

- ✅ Project structure defined in CLAUDE.md
- ✅ Dependencies specified in requirements.txt
- ✅ Package setup configured in setup.py
- ⚠️ **No implementation files exist yet** - project is in planning phase
- ✅ 5 specialized agents created for development workflow

## Phase 1: Core Foundation & Architecture

### 1.1 Project Structure Setup

**Agent: general-purpose**

- [ ] Create main entry point (`main.py`)
- [ ] Create `ccusage_gui/` package directory
- [ ] Create `assets/` directory for icons and resources
- [ ] Place `mrtheguru_icon_main.ico` in assets folder
- [ ] Create `__init__.py` files for package structure
- [ ] Set up basic module structure:
  - `ccusage_gui/data_loader.py`
  - `ccusage_gui/cost_calculator.py`
  - `ccusage_gui/reports.py`
  - `ccusage_gui/gui.py`
  - `ccusage_gui/config.py`
  - `ccusage_gui/utils.py`

### 1.2 Configuration System

**Agent: code-modernizer**

- [ ] Implement JSON configuration schema (compatible with original ccusage)
- [ ] Configuration file: `mrtg_ccusage.json` stored in application directory
- [ ] Startup check for config file existence (create if missing)
- [ ] Create user preferences management
- [ ] Support for multiple Claude installation paths
- [ ] Environment variable handling for `CLAUDE_CONFIG_DIR`
- [ ] Configuration validation with proper error handling

### 1.3 Security Foundation

**Agent: security-auditor**

- [ ] Perform initial security assessment of project structure
- [ ] Review configuration file handling for security best practices
- [ ] Validate file path handling for directory traversal prevention
- [ ] Ensure secure defaults for all configuration options

## Phase 2: Core Data Processing Engine

### 2.1 Data Loading System

**Agent: python-performance-optimizer**

- [ ] Implement JSONL file discovery and parsing
- [ ] Support multiple Claude data directories:
  - `%USERPROFILE%\.config\claude\projects\`
  - `%USERPROFILE%\.claude\projects\`
- [ ] Optimize file reading for large JSONL files
- [ ] Implement streaming processing for memory efficiency
- [ ] Handle malformed data gracefully with error logging

### 2.2 Token Processing & Aggregation

**Agent: python-performance-optimizer**

- [ ] Implement token counting algorithms:
  - Input tokens
  - Output tokens
  - Cache creation tokens
  - Cache read tokens
- [ ] Model detection and classification
- [ ] Session identification and grouping
- [ ] Performance optimization for large datasets

### 2.3 Cost Calculation Engine

**Agent: code-modernizer**

- [ ] Implement model-specific pricing (Opus, Sonnet, etc.)
- [ ] Handle cache token pricing separately
- [ ] Support multiple cost calculation modes:
  - Auto (pre-calculated + calculated)
  - Calculate-only
  - Display-only
- [ ] Implement offline mode with cached pricing
- [ ] API integration for real-time pricing updates
- [ ] **Cost Update Strategy**:
  - Manual update option in settings menu
  - Optional auto-check on startup (configurable frequency)
  - Built-in fallback pricing data with version tracking
  - Update notification system

## Phase 3: Report Generation System

### 3.1 Core Report Types

**Agent: code-modernizer**

- [ ] **Daily Reports**: Usage aggregated by calendar date
- [ ] **Monthly Reports**: Monthly summaries with trends
- [ ] **Weekly Reports**: Weekly breakdown with configurable start day
- [ ] **Session Reports**: Individual conversation analysis
- [ ] **Blocks Reports**: 5-hour billing window tracking

### 3.2 Data Filtering & Sorting

**Agent: python-performance-optimizer**

- [ ] Date range filtering (since/until dates)
- [ ] Project-specific filtering
- [ ] Model type filtering
- [ ] Sort options (date, cost, tokens) with asc/desc order
- [ ] Advanced filtering combinations

### 3.3 Export Functionality

**Agent: code-modernizer**

- [ ] JSON export with structured schemas
- [ ] CSV export for spreadsheet analysis
- [ ] Configurable export options
- [ ] Batch export capabilities
- [ ] Export validation and error handling

## Phase 4: GUI Interface Development

### 4.1 Main Application Window

**Agent: ui-ux-designer**

- [ ] Design main window layout with responsive design
- [ ] **Application Branding**:
  - Title bar: "Mr. The Guru - Claude Code Usage"
  - Custom icon: `mrtheguru_icon_main.ico` in upper left corner
- [ ] Implement menu bar with File, View, Tools, Help menus
- [ ] **Enhanced Help Menu**:
  - Add "View Documentation" option
  - Opens resizable window displaying README.md
  - Markdown rendering for proper formatting
- [ ] Create status bar with current data source info
- [ ] Design toolbar with quick access buttons
- [ ] Ensure Windows-native look and feel

### 4.2 Report Visualization Interface

**Agent: ui-ux-designer**

- [ ] Design tabbed interface for different report types
- [ ] Create data table components with sorting capabilities
- [ ] Implement filtering controls panel
- [ ] Design export dialog interfaces
- [ ] Add visual indicators for loading states

### 4.3 Settings & Configuration UI

**Agent: ui-ux-designer**

- [ ] Create preferences dialog with tabbed sections:
  - Data Sources (Claude directories)
  - Display Options (formatting, colors)
  - Cost Settings (pricing modes, currency)
  - Export Preferences
- [ ] Implement configuration validation with user feedback
- [ ] Add help tooltips and documentation links

### 4.4 Advanced Visualizations

**Agent: ui-ux-designer**

- [ ] Design charts for usage trends:
  - Token usage over time
  - Cost breakdown by model
  - Monthly/weekly patterns
- [ ] Interactive session drill-down views
- [ ] Live monitoring dashboard for active sessions
- [ ] Responsive chart resizing

## Phase 5: Integration & Polish

### 5.1 Data Integration Testing

**Agent: general-purpose**

- [ ] Test with sample Claude Code data
- [ ] Verify compatibility with different Claude versions
- [ ] Test edge cases (empty data, malformed files)
- [ ] Performance testing with large datasets
- [ ] Cross-version compatibility validation

### 5.2 GUI Integration & Testing

**Agent: ui-ux-designer**

- [ ] Integration testing of GUI components
- [ ] User experience testing and refinement
- [ ] Accessibility compliance verification
- [ ] Responsive design testing at different window sizes
- [ ] Error state and edge case handling in UI

### 5.3 Security Hardening

**Agent: security-auditor**

- [ ] Comprehensive security audit of complete codebase
- [ ] File permission and access control review
- [ ] Input validation testing
- [ ] Dependency vulnerability scanning
- [ ] Security documentation and guidelines

### 5.4 Performance Optimization

**Agent: python-performance-optimizer**

- [ ] Profile application performance with real data
- [ ] Optimize startup time and memory usage
- [ ] Implement caching strategies
- [ ] Database/file access optimization
- [ ] GUI responsiveness optimization

## Phase 6: Distribution & Deployment

### 6.1 Standalone Executable

**Agent: python-performance-optimizer**

- [ ] Configure PyInstaller for Windows executable
- [ ] **Executable Configuration**:
  - Output name: `mrtg_ccusage.exe`
  - Include custom icon: `mrtheguru_icon_main.ico`
  - Bundle assets directory
- [ ] Optimize executable size and startup time
- [ ] Test standalone executable on different Windows versions
- [ ] Create installer package (optional)
- [ ] Distribution testing and validation

### 6.2 GitHub Repository Setup

**Agent: github-workflow-manager**

- [ ] Initialize Git repository
- [ ] Set up branch protection rules
- [ ] Create GitHub Project board for task tracking
- [ ] Configure CI/CD workflows:
  - Automated testing
  - Security scanning
  - Build validation
  - Release automation
- [ ] Set up issue templates and PR templates

### 6.3 Documentation & Release

**Agent: general-purpose**

- [ ] Create comprehensive user documentation
- [ ] Write developer documentation
- [ ] Create installation and setup guides
- [ ] Prepare release notes and changelog
- [ ] Create demo/tutorial materials

## Phase 7: Advanced Features & Future Enhancements

### 7.1 Live Monitoring

**Agent: python-performance-optimizer**

- [ ] Real-time file watching for active sessions
- [ ] Live dashboard with progress indicators
- [ ] Token burn rate tracking
- [ ] Session cost projections
- [ ] Auto-refresh capabilities

### 7.2 Data Visualization Enhancements

**Agent: ui-ux-designer**

- [ ] Interactive charts with matplotlib/plotly
- [ ] Customizable dashboard layouts
- [ ] Export charts as images
- [ ] Trend analysis with predictions
- [ ] Comparative analysis tools

### 7.3 Integration Features

**Agent: general-purpose**

- [ ] CLI mode alongside GUI
- [ ] API for external integrations
- [ ] Plugin system for extensions
- [ ] Auto-update functionality
- [ ] Cloud sync capabilities (optional)

## Development Workflow

### Task Assignment Strategy

1. **ui-ux-designer**: All interface design, user experience, and visual components
2. **code-modernizer**: Core business logic, modern Python patterns, API design
3. **security-auditor**: Security reviews, vulnerability assessments, secure coding
4. **python-performance-optimizer**: Performance-critical code, optimization, executables
5. **github-workflow-manager**: Git workflow, CI/CD, project management, releases
6. **general-purpose**: Research, integration, documentation, testing coordination

### Priority Order

1. **Phase 1 & 2**: Foundation and core data processing (critical path)
2. **Phase 3**: Report generation (core functionality)
3. **Phase 4**: GUI development (user-facing features)
4. **Phase 5**: Integration and polish (quality assurance)
5. **Phase 6**: Distribution (deployment ready)
6. **Phase 7**: Advanced features (enhancement)

## Success Criteria

### Minimum Viable Product (MVP)

- [ ] All 5 report types working (daily, monthly, weekly, session, blocks)
- [ ] GUI interface with basic functionality
- [ ] Export to JSON and CSV
- [ ] Windows executable generation
- [ ] Basic filtering and sorting

### Full Feature Parity

- [ ] Complete feature parity with original ccusage CLI
- [ ] Enhanced GUI with charts and visualizations
- [ ] Live monitoring capabilities
- [ ] Comprehensive configuration options
- [ ] Professional Windows application experience

### Quality Standards

- [ ] 90%+ code coverage with tests
- [ ] Zero high/critical security vulnerabilities
- [ ] Sub-2 second startup time
- [ ] Responsive UI (no freezing during data processing)
- [ ] Comprehensive user documentation

## Development Notes

- **Architecture**: Maintain compatibility with original ccusage data formats and configurations
- **Technology**: Python 3.10+, tkinter for GUI (with PyQt6 as advanced option)
- **Performance**: Optimize for Windows desktop usage patterns
- **Distribution**: Focus on standalone executable for easy installation
- **Compatibility**: Support multiple Claude Code versions and data formats

## Next Steps

1. Begin with Phase 1.1 - Project Structure Setup
2. Use TodoWrite tool to track individual task progress
3. Implement continuous integration between phases
4. Regular security audits and performance optimization throughout development
5. Maintain close alignment with original ccusage functionality while enhancing user experience

---

**Note**: This plan is designed to be executed with the available specialized agents, ensuring high-quality code, security, performance, and user experience throughout the development process.
