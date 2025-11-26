# WhatsApp API Fix Summary

## Problem
The WhatsApp API calls were failing because the payload structure didn't match the required format for template messages.

## Key Differences Found

### ❌ Old Code (Not Working)
```json
{
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "message"
  }
}
```

### ✅ Fixed Code (Working)
```json
{
  "type": "template",
  "template": {
    "name": "template_name",
    "language": {
      "code": "en"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "message"
          }
        ]
      }
    ]
  }
}
```

## PIVOTAL FIELDS (Critical for API to work)

### 1. **`"type": "template"`** ⚠️ CRITICAL
- **MUST** be `"template"` (NOT `"text"`)
- This is the most important change
- Most WhatsApp Business API accounts require template messages

### 2. **`"template.language.code"`** ⚠️ REQUIRED
- **MUST** be present in template object
- Format: `{"code": "en"}` (or your language code)
- Common codes: "en", "hi", "es", etc.

### 3. **`"template.name"`** ⚠️ REQUIRED
- **MUST** be an approved template name from Meta Business Suite
- Set via `WHATSAPP_TEMPLATE_NAME` environment variable
- Defaults to `"hello_world"` if not set
- Template must be approved in your Meta Business account

### 4. **`"template.components"`** ⚠️ REQUIRED IF template has variables
- Only needed if your template has body variables/parameters
- If template has `{{1}}` in body, you need components
- Structure shown in fixed code above

### 5. **NO `"preview_url"`** ✅
- Template messages don't use `preview_url`
- This field was removed from template payload

## What Changed in the Code

1. ✅ Changed `type` from `"text"` to `"template"`
2. ✅ Added `template` object with `name` and `language`
3. ✅ Added `language` object with `code` field
4. ✅ Removed `preview_url` from template messages
5. ✅ Added `components` array for dynamic message content
6. ✅ Made template format the default (`use_template=True`)

## How to Use

### Option 1: Using Environment Variables (Recommended)
```python
# Set in api_key.env or environment:
# WHATSAPP_TEMPLATE_NAME=your_template_name
# WHATSAPP_TOKEN=your_token
# WHATSAPP_PHONE_ID=your_phone_id

from whatsapp.send_message import send_whatsapp_message_simple

send_whatsapp_message_simple("919876543210", "Your message here")
```

### Option 2: Explicit Template Name
```python
from whatsapp.send_message import send_whatsapp_message

result = send_whatsapp_message(
    phone_number="919876543210",
    message="Your message here",
    template_name="your_template_name",
    language_code="en"
)
```

### Option 3: Free-form Text (Only if account approved)
```python
result = send_whatsapp_message(
    phone_number="919876543210",
    message="Your message here",
    use_template=False  # Only works for approved accounts
)
```

## Template Setup Requirements

1. **Create Template in Meta Business Suite:**
   - Go to Meta Business Suite → WhatsApp → Message Templates
   - Create a template with a body variable (e.g., `{{1}}`)
   - Wait for approval (usually instant for simple templates)
   - Note the exact template name

2. **Set Template Name:**
   - Add to `api_key.env`: `WHATSAPP_TEMPLATE_NAME=your_template_name`
   - Or pass as parameter: `template_name="your_template_name"`

3. **Template Example:**
   ```
   Template Name: "stock_alert"
   Body: "Stock Alert: {{1}}"
   Language: English
   ```

## Testing

The code now includes debug output showing:
- Endpoint URL
- Payload structure
- Headers

Check these to verify the payload matches the successful API call format.

## Common Issues

1. **"Template not found"**
   - Check template name matches exactly (case-sensitive)
   - Ensure template is approved in Meta Business Suite

2. **"Invalid parameter"**
   - Verify template has body variables if using components
   - Check parameter count matches template variables

3. **"Message failed to send"**
   - Verify phone number format (no +, spaces, or dashes)
   - Check token and phone_id are correct
   - Ensure template is approved

