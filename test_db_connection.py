"""
Quick test script to verify database connection
"""
from pathlib import Path
from dotenv import load_dotenv
import os

# Load config
config_path = Path("input_parsers/db_config.env")
if config_path.exists():
    load_dotenv(config_path)
    print(f"[OK] Loaded config from {config_path}")
else:
    print(f"[ERROR] Config file not found: {config_path}")

# Check environment variables
print("\nDatabase Configuration:")
print(f"  DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}")
print(f"  DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}")
print(f"  DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
print(f"  DB_USER: {os.getenv('DB_USER', 'NOT SET')}")
password = os.getenv('DB_PASSWORD', 'NOT SET')
print(f"  DB_PASSWORD: {'*' * len(password) if password != 'NOT SET' else 'NOT SET'}")

# Test connection
print("\nTesting database connection...")
try:
    from input_parsers.db_persistence import HoldingsDBPersistence
    
    with HoldingsDBPersistence() as db:
        print("[OK] Successfully connected to database!")
        print("[OK] Connection test passed")
        
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure PostgreSQL is running")
    print("2. Verify database 'demo_db' exists")
    print("3. Check username and password in db_config.env")
    print("4. Ensure PostgreSQL is listening on port 5432")

