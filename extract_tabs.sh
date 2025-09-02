#!/bin/bash
# Tab Regulator - Quick launcher script

echo "🗂️  Tab Regulator - Extracting your browser tabs..."
echo ""

# Run the Python script
python3 "$(dirname "$0")/tab_extractor.py" "$@"

# Check if any files were created
if ls browser_tabs_*.txt 1> /dev/null 2>&1 || ls current_tabs.txt 1> /dev/null 2>&1; then
    echo ""
    echo "📄 Tab files created in: $(pwd)"
    echo "💡 Tip: You can also run with --json for machine-readable format"
    echo "💡 Use -o filename.txt to specify a custom output file"
fi
