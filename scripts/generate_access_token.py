"""
Generate Kite access token from request_token
Usage: python generate_access_token.py <KITE_API_KEY> <KITE_API_SECRET> <request_token>
Example: python generate_access_token.py aybro7iwoafvnmnj your_secret_here abc123xyz
"""
import sys
from kiteconnect import KiteConnect

def generate_access_token(api_key: str, api_secret: str, request_token: str) -> str:
    """
    Generate access token from request token
    
    Args:
        api_key: Kite API key
        api_secret: Kite API secret
        request_token: Request token from Kite Connect login
    
    Returns:
        Access token string
    """
    kite = KiteConnect(api_key=api_key)
    data = kite.generate_session(request_token, api_secret=api_secret)
    return data["access_token"]


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate_access_token.py <KITE_API_KEY> <KITE_API_SECRET> <request_token>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  python generate_access_token.py aybro7iwoafvnmnj your_secret_here abc123xyz", file=sys.stderr)
        print("", file=sys.stderr)
        print("To get request_token:", file=sys.stderr)
        print("  1. Visit: https://kite.trade/connect/login?api_key=YOUR_API_KEY&v=3", file=sys.stderr)
        print("  2. Login with your Kite credentials", file=sys.stderr)
        print("  3. Copy the request_token from the redirect URL", file=sys.stderr)
        sys.exit(1)
    
    api_key = sys.argv[1]
    api_secret = sys.argv[2]
    request_token = sys.argv[3]
    
    try:
        access_token = generate_access_token(api_key, api_secret, request_token)
        print(access_token)
        sys.exit(0)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n[INTERRUPTED] Script cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Failed to generate access token: {error_msg}", file=sys.stderr)
        
        # Provide specific guidance based on error
        if "invalid" in error_msg.lower() or "expired" in error_msg.lower():
            print("", file=sys.stderr)
            print("The request_token is invalid or expired.", file=sys.stderr)
            print("Request tokens expire quickly (within minutes).", file=sys.stderr)
            print("", file=sys.stderr)
            print("Get a fresh request_token:", file=sys.stderr)
            print(f"  https://kite.trade/connect/login?api_key={api_key}&v=3", file=sys.stderr)
        elif "incorrect" in error_msg.lower():
            print("", file=sys.stderr)
            print("API key or secret may be incorrect.", file=sys.stderr)
            print("Double-check your credentials.", file=sys.stderr)
        
        sys.exit(1)
