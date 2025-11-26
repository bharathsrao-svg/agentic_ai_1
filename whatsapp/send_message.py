"""
WhatsApp message sending functionality
Supports WhatsApp Business API and similar services

PIVOTAL FIELDS for successful WhatsApp Business API calls:
1. "type": "template" (NOT "text") - CRITICAL for most accounts
2. "template.language.code" - REQUIRED (e.g., "en")
3. "template.name" - REQUIRED (must be an approved template name)
4. "template.components" - REQUIRED if template has body variables/parameters
5. NO "preview_url" field in template messages

Template messages are REQUIRED for:
- Initial messages to users
- Messages outside 24-hour window
- Accounts not approved for free-form messaging

Set WHATSAPP_TEMPLATE_NAME in environment or pass template_name parameter.
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
    phone_id: Optional[str] = None,
    use_template: bool = False,
    template_name: Optional[str] = None,
    language_code: str = "en"
) -> dict:
    """
    Send a WhatsApp message using WhatsApp Business API
    
    Args:
        phone_number: Recipient phone number in international format (e.g., "919876543210")
        message: Message content to send
        token: WhatsApp API access token (if None, loads from WHATSAPP_TOKEN env var)
        api_url: WhatsApp API base URL (if None, uses default or WHATSAPP_API_URL env var)
        phone_id: WhatsApp Business Phone Number ID (if None, uses WHATSAPP_PHONE_ID env var)
        use_template: If True, use template message format (required for many accounts). Default: True
        template_name: Template name to use (if None, uses WHATSAPP_TEMPLATE_NAME env var or "hello_world")
        language_code: Language code for template (default: "en")
    
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
        api_url = os.getenv('WHATSAPP_API_URL', 'https://graph.facebook.com/v22.0')
    
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
    # PIVOTAL FIELDS for Template messages (required for most accounts):
    # 1. "type": "template" (NOT "text") - This is CRITICAL
    # 2. "template" object with "name" and "language" - REQUIRED
    # 3. "language" object with "code" - REQUIRED
    # 4. "components" array - Only needed if template has variables/parameters
    # 
    # Template messages are REQUIRED for:
    # - Initial messages to users
    # - Messages outside 24-hour window after user interaction
    # - Accounts not approved for free-form messaging
    
    if use_template:
        # Load template name from environment if not provided
        if template_name is None:
            template_name = os.getenv('WHATSAPP_TEMPLATE_NAME', 'hello_world')
        
        # Template message format - matches successful API call structure
        # PIVOTAL FIELDS:
        # - "type": "template" (NOT "text") - CRITICAL
        # - "template.name" - Your approved template name
        # - "template.language.code" - Language code (e.g., "en")
        # - "template.components" - Only if template has variables/parameters
        
        template_payload = {
            "name": template_name,
            "language": {
                "code": "en_US"
            }
        }
        
        # If your template has body variables, add components with the message
        # Most templates that send dynamic content need this
        # Check your template structure in Meta Business Suite
       # if message:  # Only add if we have a message to send
       #     template_payload["components"] = [
       #         {
       #             "type": "body",
       #             "parameters": [
       #                 {
       #                     "type": "text",
       #                     "text": message
       #                 }
       #             ]
       #         }
       #     ]
        
        payload = {
            "messaging_product": "whatsapp",
           "recipient_type": "individual",
            "to": phone_number,
           # "type": "template",  # PIVOTAL: Must be "template" not "text"
            #"template": template_payload
            "type": "text",
            "text":{ "body": message
            }
            }
        
    else:
        # Free-form text message format
        # ⚠️ IMPORTANT: Text messages ONLY work if:
        # 1. Sent within 24-hour window AFTER user has messaged you, OR
        # 2. Your account is approved for free-form messaging
        # 
        # If text messages fail, you MUST use template messages instead
        # 
        # Complete text message format (this is correct):
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": message
                # Note: "preview_url" is optional and not required
                # Add it if you want link previews: "preview_url": True
            }
        }
    
    try:
        # Send message
       # print("End Point : ")
       # print(endpoint )
       # print("Payload : ")
       # print(payload )
       # print("Headers : ")
       # print(headers )
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Check for errors in response
        if 'error' in result:
            error_code = result['error'].get('code', 'N/A')
            error_message = result['error'].get('message', 'Unknown error')
            error_type = result['error'].get('type', '')
            
            # Provide helpful error messages for common issues
            if error_code == 131047:  # Message failed to send
                error_message += " (This usually means you're outside the 24-hour window. Use template messages instead.)"
            elif error_code == 100:  # Invalid parameter
                error_message += " (Check your payload format and required fields.)"
            elif 'text' in str(payload.get('type', '')).lower() and error_code != 200:
                error_message += " (Text messages only work within 24h window. Try using template messages with use_template=True.)"
            
            raise requests.RequestException(
                f"WhatsApp API error: {error_message} "
                f"(Code: {error_code}, Type: {error_type})"
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


def send_whatsapp_message_simple(phone_number: str, message: str, use_template: bool = True) -> bool:
    """
    Simplified wrapper to send WhatsApp message
    Uses environment variables for configuration
    
    Args:
        phone_number: Recipient phone number in international format
        message: Message content to send
        use_template: If True, use template format (default: True, recommended for most accounts)
    
    Returns:
        bool: True if message sent successfully, False otherwise
    
    Note:
        Template messages are REQUIRED for most WhatsApp Business API accounts.
        Make sure you have:
        1. An approved template in Meta Business Suite
        2. WHATSAPP_TEMPLATE_NAME set in environment (or it defaults to 'hello_world')
        3. Template must have a body variable if you want to send dynamic content
    """
    try:
        result = send_whatsapp_message(phone_number, message, use_template=use_template)
        return result.get("success", False)
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 1:
        print("Usage: python send_message.py <phone_number> <message>")
        print("Example: python send_message.py 919876543210 'Hello from Python!'")
        print("\nEnvironment variables:")
        print("  WHATSAPP_TOKEN - WhatsApp API access token (required)")
        print("  WHATSAPP_PHONE_ID - WhatsApp Business Phone Number ID (optional)")
        print("  WHATSAPP_API_URL - WhatsApp API base URL (optional, default: https://graph.facebook.com/v18.0)")
        sys.exit(1)
    
    #phone = sys.argv[1]
    phone = "919502757136"
    msg = sys.argv[1]
    
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

