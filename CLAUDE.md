# CLAUDE.md - AI Assistant Development Guide

## Project Overview

**MP4 to MP3 Converter** is an elderly-friendly desktop application that converts video files to MP3 audio format. The application features a modern, accessible GUI specifically designed for older users with large fonts, oversized buttons, and simplified three-step workflow.

### Key Characteristics
- **Target Audience**: Elderly users with potential vision difficulties
- **Platform**: Windows (10+), though codebase is Python-based
- **UI Framework**: Tkinter with ttkbootstrap for modern theming
- **Primary Language**: Python 3.7+
- **License**: MIT

### Core Features
- Batch video to audio conversion (MP4, AVI, MKV, MOV, FLV, WMV, M4V)
- Multiple bitrate options (128k - 320k)
- Conversion history tracking
- User preferences persistence
- Real-time progress feedback
- Cancellable operations

---

## Codebase Structure

### File Organization

```
mp4to3/
├── main.py                      # Single-file application (all code)
├── requirements.txt             # Python dependencies
├── build.spec                   # PyInstaller configuration
├── build.bat                    # Windows build script
├── run.bat                      # Development run script
├── README.md                    # User documentation (Chinese)
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore rules
└── .claude/                     # Claude Code configuration
```

### Runtime Generated Files

The application creates files in `%APPDATA%\MP4to3\`:
- `conversion_history.json` - Conversion history records
- `config.json` - User preferences (bitrate, output directory)
- `converter.log` - Application logs

### Key Code Sections (main.py)

| Lines | Section | Description |
|-------|---------|-------------|
| 1-27 | Imports & Logging | Dependencies and logging configuration |
| 28-84 | `__init__` | Application initialization, window setup |
| 85-109 | Config Management | Load/save user preferences |
| 122-380 | UI Creation | All GUI components and layout |
| 381-411 | History Management | Load/save/display conversion history |
| 494-528 | File Selection | File picker and list management |
| 530-563 | Settings | Output directory and bitrate configuration |
| 565-601 | Conversion Control | Start/cancel conversion operations |
| 602-719 | Core Conversion | Threading, video processing, error handling |
| 720-730 | Window Lifecycle | Close event handling |
| 731-752 | Main Entry Point | Application bootstrap |

---

## Architecture and Design Patterns

### Single-Class Architecture

The application uses a monolithic design pattern with one main class:
- **`MP4ToMP3Converter`**: Handles UI, business logic, and state management

**Rationale**: Simple enough to not require separation of concerns; optimizes for maintainability given the limited scope.

### Threading Model

```python
# Main Thread (UI)
├── GUI event handling
├── User interactions
└── Status updates (via root.after())

# Worker Thread (Conversion)
├── File processing loop
├── MoviePy video/audio extraction
└── Progress callbacks to main thread
```

**Thread Safety**: All UI updates from worker thread use `self.root.after(0, lambda: ...)` to ensure thread-safe GUI operations.

### State Management

```python
# Instance Variables
self.files              # List[str] - Selected video files
self.converting         # bool - Conversion in progress flag
self.cancel_event       # threading.Event - Cancellation signal
self.config             # dict - User preferences
self.conversion_history # List[dict] - Historical conversions
```

### Key Design Patterns

1. **Observer Pattern**: Progress updates via callbacks
2. **Command Pattern**: Button handlers encapsulate operations
3. **Singleton Pattern**: One app instance per process
4. **Factory Pattern**: Theme and style configuration

---

## Development Workflows

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/raymondyan-zhijie/mp4to3.git
cd mp4to3

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
# OR on Windows:
run.bat
```

### Testing Changes

```bash
# Test directly
python main.py

# Verify changes with different scenarios:
# 1. Single file conversion
# 2. Batch (multiple files)
# 3. Cancel operation mid-conversion
# 4. Invalid file handling
# 5. Output directory permissions
```

### Building Executable

```bash
# Method 1: Use build script (Windows)
build.bat

# Method 2: Manual build
pyinstaller build.spec

# Output location
dist/MP4toMP3Converter.exe
```

### Deployment

1. Build executable using `build.bat`
2. Test the standalone .exe file
3. Distribute `dist/MP4toMP3Converter.exe`
4. No installer needed - portable application

---

## Key Conventions

### Code Style

1. **Language**: Chinese for UI strings, English for code/comments
2. **Docstrings**: Chinese docstrings for methods
3. **Naming**: Snake_case for functions/variables, PascalCase for classes
4. **Indentation**: 4 spaces (standard Python)

### UI/UX Principles

1. **Elderly-Friendly Design**:
   - Minimum font sizes: Title (24pt), Buttons (14pt bold), Body (12-16pt)
   - Large clickable areas (padding=12-15 for buttons)
   - High contrast colors (Cosmo theme)
   - Auto-maximize window on startup
   - Scrollable interface for smaller screens

2. **Three-Step Workflow**:
   ```
   Step 1: Select video files (选择视频文件)
   Step 2: Configure settings (设置转换选项) - Optional
   Step 3: Start conversion (开始转换)
   ```

3. **User Feedback**:
   - Real-time status updates
   - Progress bar with percentage
   - Sound notification on completion
   - Detailed error messages with context

### Error Handling

```python
# Pattern used throughout
try:
    # Operation
    logging.info("Success message")
except Exception as e:
    logging.error(f"Error context: {e}")
    messagebox.showerror("错误", user_friendly_message)
```

**Always**:
- Log errors with context
- Show user-friendly error dialogs
- Continue operation when possible (don't crash)
- Gracefully handle missing files, permissions, etc.

### Logging Strategy

```python
# Log Levels
logging.info()   # User actions, successful operations
logging.error()  # Exceptions, failures

# Log Format
# '[TIMESTAMP] - [LEVEL] - [MESSAGE]'
# Example: '2025-01-15 10:30:45 - INFO - 应用程序启动'
```

---

## Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `moviepy` | >=1.0.3 | Video/audio processing, extraction |
| `ttkbootstrap` | >=1.10.0 | Modern Tkinter themes |
| `pyinstaller` | >=5.0.0 | Executable packaging |

### Implicit Dependencies

- **imageio** & **imageio_ffmpeg**: Required by moviepy for video decoding
- **PIL/Pillow**: Image processing (used by ttkbootstrap)
- **tkinter**: Standard library GUI (included with Python)
- **winsound**: Windows sound notifications (Windows only)

### Version Compatibility Notes

1. **MoviePy 2.x**: Current code uses `from moviepy import VideoFileClip` (v2.x style)
2. **Python 3.7+**: Minimum for f-strings and type hints support
3. **Windows-Specific**: `winsound` and path handling assume Windows OS

---

## Build and Deployment

### PyInstaller Configuration (build.spec)

Key aspects of the build configuration:

```python
# Data Collection
datas = [
    ttkbootstrap themes and assets
    imageio codecs and plugins
    imageio_ffmpeg binary
]

# Metadata (critical for runtime import discovery)
copy_metadata('imageio')
copy_metadata('moviepy')
copy_metadata('ttkbootstrap')

# Hidden Imports
collect_submodules('moviepy')      # Ensure all moviepy modules included
collect_submodules('ttkbootstrap')  # Theme files
collect_submodules('imageio')       # Video codecs

# Exclusions (reduce size)
excludes=['matplotlib', 'scipy', 'pandas']

# Options
console=False  # Windowed application (no terminal)
upx=True       # Compress executable
```

### Build Process

1. **Clean**: Remove old `build/` and `dist/` directories
2. **Build**: Run `pyinstaller build.spec`
3. **Cleanup**: Remove `build/` folder
4. **Output**: Single executable in `dist/MP4toMP3Converter.exe`

### Common Build Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Missing module at runtime | Hidden import not collected | Add to `hiddenimports` in build.spec |
| Theme not loading | ttkbootstrap data files missing | Verify `collect_data_files('ttkbootstrap')` |
| Video codec error | imageio_ffmpeg not included | Add to datas and copy_metadata |
| Large executable size | Unnecessary packages included | Add to `excludes` list |

---

## Testing and Quality Assurance

### Manual Testing Checklist

**Before Release:**
- [ ] Single file conversion (MP4)
- [ ] Batch conversion (3+ files)
- [ ] All video formats (MP4, AVI, MKV, MOV, FLV, WMV)
- [ ] All bitrate options (128k, 192k, 256k, 320k)
- [ ] Cancel conversion mid-operation
- [ ] Custom output directory
- [ ] Conversion history view and clear
- [ ] Config persistence (restart app)
- [ ] Error handling (invalid file, no audio track)
- [ ] Window resize and scrolling
- [ ] Completion sound notification

**Edge Cases:**
- [ ] File already exists (should auto-rename)
- [ ] No write permissions to output directory
- [ ] Invalid video file (corrupted)
- [ ] Video with no audio track
- [ ] Very large files (>1GB)
- [ ] Special characters in filename
- [ ] Network drive as output location

### Logging Review

Check `converter.log` after testing for:
- No unexpected errors
- Proper error messages for known issues
- Successful operation logging

---

## Common Development Tasks

### Adding a New Video Format

1. Add extension to file dialog in `select_files()`:
   ```python
   filetypes=[
       ("视频文件", "*.mp4;*.avi;*.mkv;*.mov;*.flv;*.wmv;*.m4v;*.webm"),  # Add here
       ("所有文件", "*.*")
   ]
   ```

2. Test with sample file of that format
3. Update README.md supported formats list

### Adding a New Bitrate Option

1. Add to `self.bitrates` and `self.bitrate_values` (line 59-60):
   ```python
   self.bitrates = ["128k - 普通质量", "192k - 高质量 ★推荐", "256k - 极高质量", "320k - 最高质量", "384k - 超高质量"]
   self.bitrate_values = ["128k", "192k", "256k", "320k", "384k"]
   ```

2. No other changes needed (automatically handled by combobox)

### Modifying UI Layout

**Important**: Maintain elderly-friendly design principles
- Keep fonts large (>=12pt body, >=14pt buttons)
- Maintain high contrast
- Ensure touch-friendly button sizes (padding>=10)

To add a new UI element:
```python
# Create element
new_widget = ttk.Button(
    parent_frame,
    text="按钮文字",
    command=self.handler_method,
    bootstyle="primary"  # success, danger, info, secondary, warning
)
new_widget.pack(pady=10)  # or grid()
new_widget.configure(padding=12)  # Large touch target
```

### Adding Configuration Options

1. Add to default config (line 87-90):
   ```python
   self.config = {
       'bitrate': '192k',
       'output_dir': os.path.expanduser("~\\Music"),
       'new_option': 'default_value'  # Add here
   }
   ```

2. Create UI element and bind to config
3. Update `apply_config()` to restore from saved config
4. Save on change using `self.save_config()`

### Changing Theme

Available ttkbootstrap themes:
- cosmo (current - light, modern)
- flatly, litera, minty, pulse (light variants)
- darkly, solar, superhero, vapor (dark variants)

Change in `main()` (line 736):
```python
root = ttk.Window(
    title="MP4 转 MP3 转换器",
    themename="flatly",  # Change here
    size=(1000, 750)
)
```

---

## Best Practices for AI Assistants

### When Making Changes

1. **Preserve User Experience**:
   - Never reduce font sizes or button padding
   - Maintain the three-step workflow structure
   - Keep all Chinese UI text intact
   - Don't remove accessibility features

2. **Thread Safety**:
   - Always use `self.root.after(0, lambda: ...)` for UI updates from threads
   - Never directly modify tkinter widgets from worker threads
   - Respect the `self.cancel_event` for cancellation

3. **Error Handling**:
   - Wrap operations in try-except blocks
   - Log all errors with context
   - Show user-friendly error messages (in Chinese)
   - Allow graceful degradation

4. **Testing Guidance**:
   - After changes, provide specific test scenarios
   - Mention which methods were modified
   - Highlight potential edge cases
   - Remind to check logs after testing

### Code Modification Guidelines

**DO:**
- Maintain existing code style and conventions
- Add logging for new operations
- Update docstrings (in Chinese) when changing behavior
- Test with actual video files before committing
- Preserve backward compatibility for config files

**DON'T:**
- Change UI language to English
- Reduce accessibility (font sizes, button sizes)
- Remove error handling or logging
- Break the three-step workflow
- Modify thread safety patterns
- Add complex dependencies

### Understanding Context

**User Base**: Elderly users who may:
- Have limited technical knowledge
- Need large, clear text
- Prefer simple, guided workflows
- Be frustrated by complex options
- Require auditory feedback (sounds)

**Development Context**:
- Single maintainer (likely)
- No automated testing (manual QA)
- Windows-focused (but Python portable)
- Infrequent updates (stable release cycle)

### Suggesting Improvements

When suggesting features, consider:
1. **Simplicity**: Does it add complexity to the UI?
2. **Accessibility**: Does it maintain or improve usability for elderly users?
3. **Compatibility**: Does it work on Windows 10+?
4. **Dependencies**: Does it add large/complex dependencies?
5. **Localization**: Can it be properly translated to Chinese?

**Good Suggestions**:
- Better error recovery
- More video format support
- Performance optimizations
- Better progress feedback
- Improved logging

**Avoid Suggesting**:
- Advanced features (batch editing, filters, etc.)
- Multiple language support (Chinese-only is intentional)
- Cloud integration (privacy, complexity)
- Automatic updates (security, trust)
- Plugin systems (over-engineering)

---

## Git Workflow

### Branch Strategy

- **Main Branch**: Stable releases only
- **Feature Branches**: `claude/claude-md-*` for AI-assisted development
- Always work on the designated branch provided in task context

### Commit Messages

Follow format (Chinese acceptable):
```
Type: Brief description

Detailed explanation if needed.
```

Types:
- `Feature:` - New functionality
- `Fix:` - Bug fixes
- `Update:` - Improvements to existing features
- `Refactor:` - Code restructuring
- `Docs:` - Documentation changes
- `Build:` - Build system changes

**Example**:
```
Feature: Add WebM video format support

Added .webm to supported file types in file dialog
and updated README documentation.
```

### Before Pushing

1. Test the application manually
2. Check logs for errors
3. Verify config persistence
4. Test edge cases
5. Update README.md if user-facing changes

---

## Troubleshooting Guide

### Development Issues

**Import Error in IDE**:
- Ensure virtual environment activated
- Run `pip install -r requirements.txt`
- Restart IDE/language server

**Application Won't Start**:
- Check `converter.log` for errors
- Verify Python 3.7+ installed
- Ensure tkinter available (`python -m tkinter`)

**Video Conversion Fails**:
- Check if video has audio track
- Verify output directory permissions
- Test with different video format
- Check moviepy and ffmpeg installed

### Build Issues

**Missing DLL at Runtime**:
- Add to `binaries` in build.spec
- Check PyInstaller hooks

**Theme Not Loading**:
- Verify `collect_data_files('ttkbootstrap')` in build.spec
- Check datas are being collected

**Large Executable Size**:
- Add unused packages to `excludes`
- Disable UPX if causing issues: `upx=False`

### Production Issues

**Conversion Slow**:
- Expected for large files
- Higher bitrates take longer
- Check available disk space

**App Crashes on Close During Conversion**:
- Known: User must confirm cancellation
- By design: Prevents data loss

---

## Quick Reference

### Important File Paths

| Path | Purpose |
|------|---------|
| `main.py:28-730` | Main application class |
| `main.py:731-752` | Entry point and theme setup |
| `build.spec` | PyInstaller configuration |
| `requirements.txt` | Python dependencies |
| `%APPDATA%\MP4to3\` | User data directory |

### Key Methods

| Method | Line | Purpose |
|--------|------|---------|
| `__init__` | 31 | Initialize app and create UI |
| `create_widgets` | 122 | Build entire GUI |
| `select_files` | 494 | File picker dialog |
| `start_conversion` | 565 | Begin conversion process |
| `convert_files` | 602 | Core conversion logic (threaded) |
| `cancel_conversion` | 595 | Handle user cancellation |
| `show_history` | 413 | Display conversion history window |

### Configuration Keys

```python
self.config = {
    'bitrate': '192k',           # Audio quality
    'output_dir': '~\\Music'      # Save location
}
```

### Event Callbacks

```python
self.bitrate_var              # Selected bitrate
self.output_path              # Output directory path
self.progress_var             # Progress bar value (0-100)
self.status_var               # Status text display
self.file_count_var           # Selected files count
self.cancel_event             # Threading.Event for cancellation
```

---

## Version History

### v2.0.0 (Current - Elderly-Friendly)
- Modern ttkbootstrap UI
- Auto-maximized window
- Extra-large fonts and buttons
- Scrollable interface
- Three-step simplified workflow
- Cosmo theme (high contrast)
- Config auto-save
- Improved history display

### v1.5.0
- Full Chinese localization
- Cancel conversion feature
- Extended format support
- Error handling improvements
- Thread safety fixes
- MoviePy 2.x compatibility

### v1.0.0
- Initial release
- Basic MP4 to MP3 conversion
- Batch processing
- History tracking

---

## Resources

### Documentation
- [ttkbootstrap Docs](https://ttkbootstrap.readthedocs.io/)
- [MoviePy Documentation](https://zulko.github.io/moviepy/)
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)
- [Tkinter Reference](https://docs.python.org/3/library/tkinter.html)

### External Dependencies
- **FFmpeg**: Bundled with imageio-ffmpeg
- **ImageIO**: Video codec handling
- **Pillow**: Image processing

### Repository
- **GitHub**: https://github.com/raymondyan-zhijie/mp4to3
- **Issues**: Report bugs and feature requests
- **License**: MIT

---

## Contact and Contribution

For questions or contributions:
1. Check existing issues on GitHub
2. Read this CLAUDE.md thoroughly
3. Follow the code conventions
4. Test changes comprehensively
5. Submit pull requests with clear descriptions

**Remember**: This application serves elderly users. Prioritize simplicity, accessibility, and reliability over features and complexity.
