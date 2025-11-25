"""
Simple script to help set up Kite API access
Provides step-by-step guidance
"""
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
import os

# Load API key
load_dotenv("api_key.env")
KITE_API_KEY = os.getenv('KITE_API_KEY', 'ej7jiz1qk7h6irli')

print("=" * 80)
print("KITE API SETUP HELPER")
print("=" * 80)
print()

print("Since the apps page URL doesn't work, here are your options:")
print()

print("OPTION 1: Try Direct Login (Recommended)")
print("-" * 80)
login_url = f"https://kite.trade/connect/login?api_key={KITE_API_KEY}&v=3"
print(f"1. Visit this URL in your browser:")
print(f"   {login_url}")
print()
print("2. If you can login successfully:")
print("   - You'll be redirected with a request_token")
print("   - Copy that token")
print("   - Run: python get_kite_access_token.py")
print()
print("3. If you get 'user not enabled' error:")
print("   - The app needs to be enabled (see Option 2)")
print()

open_browser = input("Open login URL in browser now? (y/n): ").strip().lower()
if open_browser == 'y':
    webbrowser.open(login_url)
    print("\nBrowser opened. After login, come back here.")
    print()

print()
print("OPTION 2: Access API Settings (Alternative URLs)")
print("-" * 80)
print("Try these URLs one by one:")
print()
urls = [
    "https://kite.trade/connect/apps",
    "https://kite.zerodha.com/settings",
    "https://kite.trade",
    "https://kite.zerodha.com/dashboard"
]

for i, url in enumerate(urls, 1):
    print(f"{i}. {url}")
    open_it = input(f"   Open this URL? (y/n): ").strip().lower()
    if open_it == 'y':
        webbrowser.open(url)
        print("   Opened in browser. Look for 'API', 'Apps', or 'Developer' section")
        print()

print()
print("OPTION 3: Create New App (Easiest if above don't work)")
print("-" * 80)
print("1. Visit: https://kite.trade")
print("2. Login with your credentials")
print("3. Look for 'Developer' or 'API' in the menu")
print("4. Click 'Create new app' or 'New application'")
print("5. Fill in:")
print("   - App name: Holdings Analysis")
print("   - Redirect URL: http://localhost")
print("6. Save and copy the new API key")
print("7. Update api_key.env with new key")
print()

print()
print("OPTION 4: Use Existing Access Token (If you have one)")
print("-" * 80)
print("If you already have a valid access token:")
print("1. Update api_key.env with: KITE_ACCESS_TOKEN=your_token")
print("2. Test with: python test_kite_official.py")
print()

print("=" * 80)
print("QUICK REFERENCE")
print("=" * 80)
print(f"Your API Key: {KITE_API_KEY}")
print(f"Login URL: {login_url}")
print()
print("After getting request_token, run:")
print("  python get_kite_access_token.py")
print()
print("After getting access_token, test with:")
print("  python test_kite_official.py")
print()

