# Tab Regulator 🗂️

Extract all your open browser tabs to a text file without closing or restarting your browser!

## Features

- ✅ Works with **Chrome**, **Firefox**, and **Safari**
- ✅ **No browser restart required** - works with your current session
- ✅ Exports to clean, readable text format
- ✅ Optional JSON export for programmatic use
- ✅ Cross-platform support (macOS, Windows, Linux)
- ✅ No external dependencies - uses built-in Python libraries

## Quick Start

1. **Make sure your browser is running** with tabs open
2. **Run the script**:
   ```bash
   python3 tab_extractor.py
   ```
3. **Find your exported tabs** in the generated text file!

## Usage Examples

### Basic Usage
```bash
# Extract all tabs to timestamped file
python3 tab_extractor.py

# Specify custom output filename  
python3 tab_extractor.py -o my_tabs.txt

# Also generate JSON format
python3 tab_extractor.py --json
```

### Sample Output
```
Browser Tabs Export
Generated: 2024-01-15 14:30:22
Total tabs: 15
================================================================================

CHROME TABS (12 tabs)
----------------------------------------
  1. GitHub - tab_regulator
     https://github.com/user/tab_regulator

  2. Stack Overflow - Python subprocess
     https://stackoverflow.com/questions/python-subprocess

  3. Google Search Results
     https://google.com/search?q=browser+automation

...

SAFARI TABS (3 tabs)
----------------------------------------
  1. Apple Developer Documentation
     https://developer.apple.com/documentation/

...
```

## How It Works

### macOS
- Uses **AppleScript** to communicate directly with running browsers
- No need for browser extensions or special permissions
- Works immediately with Chrome, Firefox, and Safari

### Windows/Linux
- Chrome: Uses process inspection and automation
- Firefox: Accesses session store files
- May require additional setup for some browsers

## Permissions (macOS)

If you get permission errors, you may need to:

1. **Grant Terminal accessibility permissions**:
   - System Preferences → Security & Privacy → Privacy → Accessibility
   - Add Terminal (or your terminal app) to the list

2. **Allow AppleScript access** to your browsers when prompted

## Troubleshooting

### "No tabs found"
- Make sure your browser is actually running
- Ensure you have tabs open (not just a new tab page)
- Try running the script while the browser is in focus

### Permission Errors
- Grant accessibility permissions to Terminal
- Make sure your browser allows AppleScript access

### Browser Not Supported
- Currently supports Chrome, Firefox, Safari
- Other Chromium browsers (Edge, Brave) may work with Chrome method
- Submit an issue for additional browser support!

## File Formats

### Text Format
- Clean, readable format
- Grouped by browser
- Shows title and URL for each tab
- Perfect for sharing or archiving

### JSON Format (--json flag)
- Machine-readable format
- Includes metadata (timestamps, browser info)
- Perfect for programmatic processing

## Advanced Usage

The script is designed to be simple but extensible. You can modify it to:
- Filter tabs by domain or title
- Export to different formats (CSV, HTML, etc.)
- Integrate with bookmark managers
- Schedule automatic exports

## Contributing

Found a bug or want to add a feature? Contributions welcome!

## License

MIT License - feel free to use and modify as needed.
