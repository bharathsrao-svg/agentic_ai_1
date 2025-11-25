"""
Test script to verify Kite Connect URL and help debug
"""
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv("api_key.env")
KITE_API_KEY = os.getenv('KITE_API_KEY', 'aybro7iwoafvnmnj')

print("=" * 80)
print("KITE CONNECT URL TESTER")
print("=" * 80)
print()

print(f"Your API Key: {KITE_API_KEY}")
print()

# Build connect URL
connect_url = f"https://kite.trade/connect/login?api_key={KITE_API_KEY}&v=3"

print("Connect URL:")
print(connect_url)
print()

print("Troubleshooting Steps:")
print("-" * 80)
print()
print("1. The app shows as 'Active' on developers.kite.trade")
print("   ✓ Confirmed")
print()
print("2. Check if YOUR USER is enabled in app settings:")
print("   - Go to: https://developers.kite.trade")
print("   - Click on your app")
print("   - Look for 'Users', 'Authorized Users', or 'User Access' section")
print("   - Make sure YOUR email/user ID is listed there")
print("   - If not, ADD IT and save")
print()
print("3. Verify Redirect URL is set:")
print("   - In app settings, check 'Redirect URL'")
print("   - Should be set to something like: http://localhost")
print("   - Can't be empty")
print()
print("4. Check you're using the correct login:")
print("   - Use the SAME email/user ID that's authorized in the app")
print("   - Check your Kite profile to confirm your email/user ID")
print()

print("=" * 80)
print("TESTING CONNECT URL")
print("=" * 80)
print()

open_url = input("Open connect URL in browser? (y/n): ").strip().lower()
if open_url == 'y':
    webbrowser.open(connect_url)
    print("\nBrowser opened. Try to login.")
    print()
    print("Expected outcomes:")
    print("  ✅ SUCCESS: You get redirected with request_token in URL")
    print("  ❌ ERROR: 'The user is not enabled for the app'")
    print()
    print("If you get the error:")
    print("  1. Go back to developers.kite.trade")
    print("  2. Open your app settings")
    print("  3. Find 'Users' or 'Authorized Users' section")
    print("  4. Add your user email/ID")
    print("  5. Save and try again")
    print()

print()
print("Alternative: Create New App")
print("-" * 80)
print("If you can't enable the existing app:")
print("1. Go to: https://developers.kite.trade")
print("2. Create a new app")
print("3. During creation, make sure to:")
print("   - Add your user immediately")
print("   - Set redirect URL: http://localhost")
print("4. Use the new API key")
print()

