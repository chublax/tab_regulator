#!/usr/bin/env python3
"""
Tab Regulator - Extract all open browser tabs to a text file
Works with Chrome, Firefox, and other browsers without closing them.
"""

import json
import os
import platform
import subprocess
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
import argparse


class TabExtractor:
    def __init__(self):
        self.system = platform.system()
        self.tabs = []
    
    def get_chrome_tabs(self):
        """Extract tabs from Google Chrome"""
        try:
            if self.system == "Darwin":  # macOS
                # First check if Chrome is running and has windows
                check_script = '''
                tell application "System Events"
                    if exists (processes where name is "Google Chrome") then
                        tell application "Google Chrome"
                            if (count of windows) > 0 then
                                return "ready"
                            else
                                return "no_windows"
                            end if
                        end tell
                    else
                        return "not_running"
                    end if
                end tell
                '''
                check_result = subprocess.run(['osascript', '-e', check_script], 
                                            capture_output=True, text=True)
                
                if check_result.returncode == 0:
                    status = check_result.stdout.strip()
                    if status == "not_running":
                        return False
                    elif status == "no_windows":
                        print("Chrome is running but has no windows open")
                        return False
                    elif status == "ready":
                        # Use AppleScript to get Chrome tabs
                        script = '''
                        tell application "Google Chrome"
                            set tab_list to {}
                            repeat with w in windows
                                repeat with t in tabs of w
                                    try
                                        set tab_info to (title of t & " ||| " & URL of t)
                                        set end of tab_list to tab_info
                                    end try
                                end repeat
                            end repeat
                            return tab_list
                        end tell
                        '''
                        result = subprocess.run(['osascript', '-e', script], 
                                              capture_output=True, text=True)
                        if result.returncode == 0 and result.stdout.strip():
                            tabs_output = result.stdout.strip()
                            if tabs_output and tabs_output != "":
                                # Handle the case where AppleScript returns a comma-separated list
                                if tabs_output.startswith('{') and tabs_output.endswith('}'):
                                    tabs_output = tabs_output[1:-1]  # Remove braces
                                tabs = [tab.strip().strip('"') for tab in tabs_output.split(',')]
                                
                                for tab in tabs:
                                    if ' ||| ' in tab:
                                        title, url = tab.split(' ||| ', 1)
                                        self.tabs.append({'title': title.strip(), 'url': url.strip(), 'browser': 'Chrome'})
                                return True
                return False
            
            elif self.system == "Windows":
                # Try using PowerShell for Windows Chrome
                script = '''
                Add-Type -AssemblyName System.Windows.Forms
                $chrome = Get-Process chrome -ErrorAction SilentlyContinue
                if ($chrome) {
                    # This is a simplified approach - Windows automation is more complex
                    Write-Host "Chrome detected but tab extraction requires additional setup"
                }
                '''
                # Windows implementation would be more complex
                print("Windows Chrome tab extraction requires additional setup")
                return False
                
        except Exception as e:
            print(f"Error extracting Chrome tabs: {e}")
            return False
    
    def get_firefox_tabs(self):
        """Extract tabs from Firefox using session store"""
        try:
            if self.system == "Darwin":  # macOS
                profile_path = Path.home() / "Library/Application Support/Firefox/Profiles"
            elif self.system == "Windows":
                profile_path = Path.home() / "AppData/Roaming/Mozilla/Firefox/Profiles"
            elif self.system == "Linux":
                profile_path = Path.home() / ".mozilla/firefox"
            else:
                return False
            
            if not profile_path.exists():
                return False
            
            # Find the default profile
            for profile_dir in profile_path.iterdir():
                if profile_dir.is_dir() and "default" in profile_dir.name.lower():
                    session_file = profile_dir / "sessionstore-backups/recovery.jsonlz4"
                    if not session_file.exists():
                        session_file = profile_dir / "sessionstore.jsonlz4"
                    
                    if session_file.exists():
                        # Firefox uses LZ4 compression, which is complex to handle
                        # For now, we'll use AppleScript on macOS
                        if self.system == "Darwin":
                            return self.get_firefox_tabs_applescript()
            
            return False
            
        except Exception as e:
            print(f"Error extracting Firefox tabs: {e}")
            return False
    
    def get_firefox_tabs_applescript(self):
        """Extract Firefox tabs using AppleScript on macOS"""
        try:
            script = '''
            tell application "Firefox"
                set tab_list to {}
                repeat with w in windows
                    repeat with t in tabs of w
                        set end of tab_list to (title of t & " | " & URL of t)
                    end repeat
                end repeat
                return tab_list
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                tabs = result.stdout.strip().split('\n')
                for tab in tabs:
                    if ' | ' in tab:
                        title, url = tab.split(' | ', 1)
                        self.tabs.append({'title': title.strip(), 'url': url.strip(), 'browser': 'Firefox'})
                return True
        except Exception as e:
            print(f"Error with Firefox AppleScript: {e}")
            return False
    
    def get_safari_tabs(self):
        """Extract tabs from Safari on macOS"""
        if self.system != "Darwin":
            return False
            
        try:
            # First check if Safari is running and has windows
            check_script = '''
            tell application "System Events"
                if exists (processes where name is "Safari") then
                    tell application "Safari"
                        if (count of windows) > 0 then
                            return "ready"
                        else
                            return "no_windows"
                        end if
                    end tell
                else
                    return "not_running"
                end if
            end tell
            '''
            check_result = subprocess.run(['osascript', '-e', check_script], 
                                        capture_output=True, text=True)
            
            if check_result.returncode == 0:
                status = check_result.stdout.strip()
                if status == "not_running":
                    return False
                elif status == "no_windows":
                    print("Safari is running but has no windows open")
                    return False
                elif status == "ready":
                    script = '''
                    tell application "Safari"
                        set tab_list to {}
                        repeat with w in windows
                            repeat with t in tabs of w
                                try
                                    set tab_info to (name of t & " ||| " & URL of t)
                                    set end of tab_list to tab_info
                                end try
                            end repeat
                        end repeat
                        return tab_list
                    end tell
                    '''
                    result = subprocess.run(['osascript', '-e', script], 
                                          capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        tabs_output = result.stdout.strip()
                        if tabs_output and tabs_output != "":
                            # Handle the case where AppleScript returns a comma-separated list
                            if tabs_output.startswith('{') and tabs_output.endswith('}'):
                                tabs_output = tabs_output[1:-1]  # Remove braces
                            tabs = [tab.strip().strip('"') for tab in tabs_output.split(',')]
                            
                            for tab in tabs:
                                if ' ||| ' in tab:
                                    title, url = tab.split(' ||| ', 1)
                                    self.tabs.append({'title': title.strip(), 'url': url.strip(), 'browser': 'Safari'})
                            return True
            return False
            
        except Exception as e:
            print(f"Error extracting Safari tabs: {e}")
            return False
    
    def get_brave_tabs(self):
        """Extract tabs from Brave Browser (similar to Chrome)"""
        try:
            if self.system == "Darwin":  # macOS
                # First check if Brave is running and has windows
                check_script = '''
                tell application "System Events"
                    if exists (processes where name is "Brave Browser") then
                        tell application "Brave Browser"
                            if (count of windows) > 0 then
                                return "ready"
                            else
                                return "no_windows"
                            end if
                        end tell
                    else
                        return "not_running"
                    end if
                end tell
                '''
                check_result = subprocess.run(['osascript', '-e', check_script], 
                                            capture_output=True, text=True)
                
                if check_result.returncode == 0:
                    status = check_result.stdout.strip()
                    if status == "ready":
                        # Use AppleScript to get Brave tabs
                        script = '''
                        tell application "Brave Browser"
                            set tab_list to {}
                            repeat with w in windows
                                repeat with t in tabs of w
                                    try
                                        set tab_info to (title of t & " ||| " & URL of t)
                                        set end of tab_list to tab_info
                                    end try
                                end repeat
                            end repeat
                            return tab_list
                        end tell
                        '''
                        result = subprocess.run(['osascript', '-e', script], 
                                              capture_output=True, text=True)
                        if result.returncode == 0 and result.stdout.strip():
                            tabs_output = result.stdout.strip()
                            if tabs_output and tabs_output != "":
                                # Handle the case where AppleScript returns a comma-separated list
                                if tabs_output.startswith('{') and tabs_output.endswith('}'):
                                    tabs_output = tabs_output[1:-1]  # Remove braces
                                tabs = [tab.strip().strip('"') for tab in tabs_output.split(',')]
                                
                                for tab in tabs:
                                    if ' ||| ' in tab:
                                        title, url = tab.split(' ||| ', 1)
                                        self.tabs.append({'title': title.strip(), 'url': url.strip(), 'browser': 'Brave'})
                                return True
                return False
        except Exception as e:
            print(f"Error extracting Brave tabs: {e}")
            return False

    def extract_all_tabs(self):
        """Extract tabs from all supported browsers"""
        print("Extracting tabs from browsers...")
        
        browsers_found = []
        
        # Try Chrome
        if self.get_chrome_tabs():
            browsers_found.append("Chrome")
            print(f"✓ Found {len([t for t in self.tabs if t['browser'] == 'Chrome'])} Chrome tabs")
        
        # Try Brave
        if self.get_brave_tabs():
            browsers_found.append("Brave")
            print(f"✓ Found {len([t for t in self.tabs if t['browser'] == 'Brave'])} Brave tabs")
        
        # Try Firefox
        if self.get_firefox_tabs():
            browsers_found.append("Firefox")
            print(f"✓ Found {len([t for t in self.tabs if t['browser'] == 'Firefox'])} Firefox tabs")
        
        # Try Safari (macOS only)
        if self.get_safari_tabs():
            browsers_found.append("Safari")
            print(f"✓ Found {len([t for t in self.tabs if t['browser'] == 'Safari'])} Safari tabs")
        
        if not browsers_found:
            print("❌ No supported browsers found or no tabs could be extracted")
            print("Make sure your browser is running and try again")
            return False
        
        print(f"✓ Successfully extracted tabs from: {', '.join(browsers_found)}")
        return True
    
    def load_previous_tabs(self, filename):
        """Load previous tabs from file to compare"""
        if not os.path.exists(filename):
            return set()
        
        try:
            previous_urls = set()
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract URLs from previous content
                import re
                url_pattern = r'https?://[^\s\n]+'
                urls = re.findall(url_pattern, content)
                previous_urls.update(urls)
            return previous_urls
        except Exception as e:
            print(f"Warning: Could not read previous tabs: {e}")
            return set()

    def save_to_file(self, filename=None):
        """Save extracted tabs to a daily file with incremental updates"""
        if not self.tabs:
            print("No tabs to save!")
            return False
        
        now = datetime.now()
        
        if filename is None:
            # Use daily filename format: tabs_YYYY-MM-DD.txt
            date_str = now.strftime("%Y-%m-%d")
            filename = f"tabs_{date_str}.txt"
        
        # Load previous tabs to compare
        previous_urls = self.load_previous_tabs(filename)
        
        # Create a more sophisticated comparison
        # Filter out common "empty" tabs that shouldn't be tracked
        ignored_urls = {
            'chrome://newtab/',
            'chrome-extension://',
            'about:blank',
            'edge://newtab/',
            'safari://newtab/'
        }
        
        # Filter for genuinely new/interesting tabs
        current_urls = {tab['url'] for tab in self.tabs 
                       if not any(ignored in tab['url'] for ignored in ignored_urls)}
        new_urls = current_urls - previous_urls
        
        # Get tabs that are genuinely new (excluding boring ones)
        new_tabs = [tab for tab in self.tabs 
                   if tab['url'] in new_urls and 
                   not any(ignored in tab['url'] for ignored in ignored_urls)]
        
        # Count filtered/ignored tabs for reporting
        ignored_tabs = [tab for tab in self.tabs 
                       if any(ignored in tab['url'] for ignored in ignored_urls)]
        
        # Count different types of ignored tabs
        blank_tab_count = len([tab for tab in ignored_tabs 
                             if 'newtab' in tab['url'] or 'about:blank' in tab['url']])
        extension_tab_count = len([tab for tab in ignored_tabs 
                                 if 'chrome-extension://' in tab['url']])
        other_ignored_count = len(ignored_tabs) - blank_tab_count - extension_tab_count
        
        try:
            # Check if file exists to determine if we're appending
            file_exists = os.path.exists(filename)
            
            with open(filename, 'a' if file_exists else 'w', encoding='utf-8') as f:
                if not file_exists:
                    # First run of the day - create header
                    f.write(f"Daily Browser Tabs Log - {now.strftime('%A, %B %d, %Y')}\n")
                    f.write("=" * 80 + "\n\n")
                
                if new_tabs:
                    # Add timestamp separator only if there are new tabs
                    f.write(f"{'=' * 20} {now.strftime('%H:%M:%S')} {'=' * 20}\n")
                    f.write(f"Run at: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"New/Changed tabs: {len(new_tabs)} (out of {len(self.tabs)} total)\n")
                    f.write("-" * 60 + "\n")
                    
                    # Group new tabs by browser
                    browsers = {}
                    for tab in new_tabs:
                        browser = tab['browser']
                        if browser not in browsers:
                            browsers[browser] = []
                        browsers[browser].append(tab)
                    
                    for browser, tabs in browsers.items():
                        if tabs:  # Only show browsers with new tabs
                            f.write(f"\n{browser.upper()} - {len(tabs)} new tabs:\n")
                            for i, tab in enumerate(tabs, 1):
                                f.write(f"  {i:2d}. {tab['title']}\n")
                                f.write(f"      {tab['url']}\n")
                    
                    f.write(f"\n")
                else:
                    # Just add a simple timestamp for no-new-tabs runs
                    f.write(f"[{now.strftime('%H:%M:%S')}] No new tabs (all {len(self.tabs)} tabs already recorded)\n")
            
            # Enhanced reporting
            content_tabs = len(self.tabs) - len(ignored_tabs)
            
            if new_tabs:
                print(f"✅ Found {len(new_tabs)} new tabs out of {len(self.tabs)} total")
                if ignored_tabs:
                    ignored_details = []
                    if blank_tab_count > 0:
                        ignored_details.append(f"{blank_tab_count} blank tabs")
                    if extension_tab_count > 0:
                        ignored_details.append(f"{extension_tab_count} extension tabs")
                    if other_ignored_count > 0:
                        ignored_details.append(f"{other_ignored_count} other ignored tabs")
                    
                    if ignored_details:
                        print(f"ℹ️  Ignored: {', '.join(ignored_details)}")
                print(f"✅ Appended to daily file: {filename}")
            else:
                print(f"ℹ️  No new tabs found (all {content_tabs} content tabs were already recorded today)")
                if ignored_tabs:
                    ignored_details = []
                    if blank_tab_count > 0:
                        ignored_details.append(f"{blank_tab_count} blank tabs")
                    if extension_tab_count > 0:
                        ignored_details.append(f"{extension_tab_count} extension tabs")
                    if other_ignored_count > 0:
                        ignored_details.append(f"{other_ignored_count} other ignored tabs")
                    
                    if ignored_details:
                        print(f"ℹ️  Currently ignoring: {', '.join(ignored_details)}")
                print(f"✅ Updated timestamp in: {filename}")
            
            return True
            
        except Exception as e:
            print(f"Error saving file: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Extract browser tabs to a text file")
    parser.add_argument("-o", "--output", help="Output filename (default: browser_tabs_TIMESTAMP.txt)")
    parser.add_argument("--json", action="store_true", help="Also save as JSON format")
    
    args = parser.parse_args()
    
    extractor = TabExtractor()
    
    if extractor.extract_all_tabs():
        # Save as text file
        success = extractor.save_to_file(args.output)
        
        # Also save as JSON if requested
        if args.json and success:
            json_filename = args.output.replace('.txt', '.json') if args.output else None
            if json_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_filename = f"browser_tabs_{timestamp}.json"
            
            try:
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'timestamp': datetime.now().isoformat(),
                        'total_tabs': len(extractor.tabs),
                        'tabs': extractor.tabs
                    }, f, indent=2, ensure_ascii=False)
                print(f"✓ JSON data saved to: {json_filename}")
            except Exception as e:
                print(f"Error saving JSON: {e}")
    
    else:
        print("Failed to extract tabs. Please ensure:")
        print("1. Your browser is currently running")
        print("2. You have tabs open")
        print("3. You're using Chrome, Firefox, or Safari")
        if platform.system() == "Darwin":
            print("4. You may need to grant accessibility permissions to Terminal/your terminal app")


if __name__ == "__main__":
    main()
