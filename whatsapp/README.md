# WhatsApp Messaging Module

This module provides functionality to send WhatsApp messages using the WhatsApp Business API.

## Setup

### 1. Get Your WhatsApp Business API Credentials

You need two things:
- **Access Token** (`WHATSAPP_TOKEN`)
- **Phone Number ID** (`WHATSAPP_PHONE_ID`)

### 2. Find Your Phone Number ID

The Phone Number ID is **REQUIRED** and can be found in several ways:

#### Method 1: Meta Business Suite
1. Go to https://business.facebook.com/
2. Navigate to **WhatsApp** > **API Setup**
3. Look for **Phone number ID** (it's a numeric ID like `123456789012345`)

#### Method 2: Graph API Explorer
1. Go to https://developers.facebook.com/tools/explorer/
2. Select your app
3. Use the endpoint: `GET /me/phone_numbers`
4. The response will show your Phone Number IDs

#### Method 3: WhatsApp Business API Dashboard
1. Go to https://business.facebook.com/
2. Navigate to **WhatsApp Manager**
3. Click on your phone number
4. The Phone Number ID is displayed in the details

### 3. Configure Environment Variables

Add to your `api_key.env` file:

```env
WHATSAPP_TOKEN=your_access_token_here
WHATSAPP_PHONE_ID=your_phone_number_id_here
WHATSAPP_API_URL=https://graph.facebook.com/v18.0  # Optional
```

## Usage

### Basic Usage

```python
from whatsapp.send_message import send_whatsapp_message

# Send a message
result = send_whatsapp_message(
    phone_number="919876543210",  # International format (country code + number)
    message="Hello from Python!"
)

if result.get("success"):
    print(f"Message sent! ID: {result.get('message_id')}")
```

### With Custom Parameters

```python
result = send_whatsapp_message(
    phone_number="919876543210",
    message="Your message here",
    token="custom_token",  # Optional: overrides env var
    phone_id="123456789012345",  # Optional: overrides env var
    api_url="https://graph.facebook.com/v18.0"  # Optional
)
```

### Simplified Wrapper

```python
from whatsapp.send_message import send_whatsapp_message_simple

success = send_whatsapp_message_simple("919876543210", "Hello!")
```

### Command Line

```bash
python whatsapp/send_message.py 919876543210 "Hello from command line!"
```

## Phone Number Format

- Use international format: country code + number
- No spaces, dashes, or plus signs
- Example for India: `919876543210` (91 = country code)
- Example for US: `15551234567` (1 = country code)

## Error Handling

The function will raise exceptions for:
- Missing token or phone number ID
- Invalid phone number format
- API errors (with detailed error messages)

## Common Issues

### Error: "Object with ID 'messages' does not exist"
- **Solution**: Make sure `WHATSAPP_PHONE_ID` is set correctly
- The Phone Number ID is required in the API endpoint

### Error: "Invalid OAuth access token"
- **Solution**: Check that your `WHATSAPP_TOKEN` is valid and not expired
- Regenerate the token if needed

### Error: "Recipient phone number not in allowed list"
- **Solution**: For development/test mode, you need to add recipient numbers to your allowed list in Meta Business Suite

## API Documentation

For more details, see:
- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Send Messages API Reference](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages)

