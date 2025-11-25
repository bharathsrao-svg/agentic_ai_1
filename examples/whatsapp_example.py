"""
Example: How to use WhatsApp messaging functionality
"""
from whatsapp.send_message import send_whatsapp_message, send_whatsapp_message_simple


def example_basic_usage():
    """Basic example of sending a WhatsApp message"""
    phone_number = "919876543210"  # Replace with actual phone number (country code + number)
    message = "Hello! This is a test message from Python."
    
    try:
        result = send_whatsapp_message(phone_number, message)
        if result.get("success"):
            print(f"✓ Message sent successfully!")
            print(f"  Message ID: {result.get('message_id')}")
        else:
            print(f"✗ Failed to send message")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_simple_wrapper():
    """Example using the simplified wrapper function"""
    phone_number = "919876543210"  # Replace with actual phone number
    message = "This is a simple test message."
    
    success = send_whatsapp_message_simple(phone_number, message)
    if success:
        print("✓ Message sent successfully!")
    else:
        print("✗ Failed to send message")


def example_with_custom_token():
    """Example with custom token (instead of using environment variable)"""
    phone_number = "919876543210"
    message = "Message with custom token"
    custom_token = "your_custom_token_here"
    
    try:
        result = send_whatsapp_message(
            phone_number=phone_number,
            message=message,
            token=custom_token
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("WhatsApp Messaging Examples")
    print("=" * 50)
    print("\nNote: Make sure you have:")
    print("  1. WHATSAPP_TOKEN set in api_key.env")
    print("  2. Valid phone number in international format")
    print("  3. WhatsApp Business API access configured")
    print("\nUncomment the example you want to run:\n")
    
    # Uncomment the example you want to test:
    # example_basic_usage()
    # example_simple_wrapper()
    # example_with_custom_token()

