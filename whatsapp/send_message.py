"""
WhatsApp message sending functionality
Supports WhatsApp Business API and similar services
"""
import os
import requests
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv


def send_whatsapp_message(
    phone_number: str,
    message: str,
    token: Optional[str] = None,
    api_url: Optional[str] = None,
    phone_id: Optional[str] = None
) -> dict:
    """
    Send a WhatsApp message using WhatsApp Business API
    
    Args:
        phone_number: Recipient phone number in international format (e.g., "919876543210")
        message: Message content to send
        token: WhatsApp API access token (if None, loads from WHATSAPP_TOKEN env var)
        api_url: WhatsApp API base URL (if None, uses default or WHATSAPP_API_URL env var)
        phone_id: WhatsApp Business Phone Number ID (if None, uses WHATSAPP_PHONE_ID env var)
    
    Returns:
        dict: Response from WhatsApp API with status and message_id if successful
    
    Raises:
        ValueError: If required parameters are missing
        requests.RequestException: If API request fails
    """
    # Load token from environment if not provided
    if token is None:
        # Try loading from api_key.env in parent directory
        script_dir = Path(__file__).parent.parent
        api_key_path = script_dir / "api_key.env"
        if api_key_path.exists():
            load_dotenv(api_key_path)
        token = os.getenv('WHATSAPP_TOKEN')
    
    if not token:
        raise ValueError("WhatsApp token is required. Provide as parameter or set WHATSAPP_TOKEN in environment.")
    
    # Load phone_id from environment if not provided
    if phone_id is None:
        phone_id = os.getenv('WHATSAPP_PHONE_ID')
    
    # Phone Number ID is REQUIRED for WhatsApp Business API
    if not phone_id:
        raise ValueError(
            "WhatsApp Phone Number ID is required. "
            "Provide as 'phone_id' parameter or set WHATSAPP_PHONE_ID in environment. "
            "You can find your Phone Number ID in Meta Business Suite or WhatsApp Business API dashboard."
        )
    
    # Load API URL from environment if not provided
    if api_url is None:
        api_url = os.getenv('WHATSAPP_API_URL', 'https://graph.facebook.com/v18.0')
    
    # Format phone number (remove any spaces, dashes, or plus signs)
    phone_number = phone_number.replace(' ', '').replace('-', '').replace('+', '')
    
    # Ensure phone number is in correct format (should start with country code)
    if not phone_number.isdigit():
        raise ValueError(f"Invalid phone number format: {phone_number}. Should contain only digits.")
    
    # Construct API endpoint - WhatsApp Business API requires Phone Number ID
    endpoint = f"{api_url}/{phone_id}/messages"
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Prepare payload for WhatsApp Business API
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
        }
    }
    
    try:
        # Send message
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Check for errors in response
        if 'error' in result:
            raise requests.RequestException(
                f"WhatsApp API error: {result['error'].get('message', 'Unknown error')} "
                f"(Code: {result['error'].get('code', 'N/A')})"
            )
        
        return {
            "success": True,
            "message_id": result.get('messages', [{}])[0].get('id'),
            "response": result
        }
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error: {e}"
        try:
            error_detail = e.response.json()
            if 'error' in error_detail:
                error_msg = f"WhatsApp API error: {error_detail['error'].get('message', str(e))}"
        except:
            pass
        raise requests.RequestException(error_msg) from e
    
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Failed to send WhatsApp message: {str(e)}") from e


def send_whatsapp_message_simple(phone_number: str, message: str) -> bool:
    """
    Simplified wrapper to send WhatsApp message
    Uses environment variables for configuration
    
    Args:
        phone_number: Recipient phone number in international format
        message: Message content to send
    
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        result = send_whatsapp_message(phone_number, message)
        return result.get("success", False)
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python send_message.py <phone_number> <message>")
        print("Example: python send_message.py 919876543210 'Hello from Python!'")
        print("\nEnvironment variables:")
        print("  WHATSAPP_TOKEN - WhatsApp API access token (required)")
        print("  WHATSAPP_PHONE_ID - WhatsApp Business Phone Number ID (optional)")
        print("  WHATSAPP_API_URL - WhatsApp API base URL (optional, default: https://graph.facebook.com/v18.0)")
        sys.exit(1)
    
    phone = sys.argv[1]
    msg = sys.argv[2]
    
    try:
        result = send_whatsapp_message(phone, msg)
        if result.get("success"):
            print(f"✓ Message sent successfully!")
            print(f"  Message ID: {result.get('message_id')}")
        else:
            print(f"✗ Failed to send message")
            print(f"  Response: {result}")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

