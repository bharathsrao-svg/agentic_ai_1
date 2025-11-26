# Why "type": "text" Doesn't Work (But "type": "template" Does)

## The Issue

Your text message format is **technically correct**, but WhatsApp Business API has strict restrictions on when text messages can be sent.

## Text Message Format (This is Correct)

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "919876543210",
  "type": "text",
  "text": {
    "body": "Hello"
  }
}
```

**The format is complete and correct.** The problem is **not** the format, but **when** you can use it.

## Why Text Messages Fail

### ⚠️ Text messages ONLY work if:

1. **24-Hour Window Rule:**
   - User must have messaged you first
   - You can only reply within 24 hours of their last message
   - After 24 hours, text messages are BLOCKED

2. **Account Approval:**
   - Your account must be approved for "free-form messaging"
   - Most new accounts are NOT approved
   - Approval requires business verification and compliance

### ✅ Template Messages Work Because:

- Can be sent **anytime** (no 24-hour restriction)
- Work for **initial messages** (user doesn't need to message first)
- Only require **template approval** (easier than free-form approval)
- Templates are pre-approved by WhatsApp

## Complete Comparison

| Feature | Text Messages | Template Messages |
|---------|--------------|-------------------|
| **Format** | ✅ Correct (as shown above) | ✅ Correct (with template object) |
| **24-Hour Window** | ❌ Must be within 24h | ✅ No restriction |
| **Initial Messages** | ❌ User must message first | ✅ Can initiate conversation |
| **Approval Required** | ✅ Free-form messaging approval | ✅ Template approval only |
| **When to Use** | Replies to active conversations | Initial messages, alerts, notifications |

## Your Text Message Format is Complete

The format you're using is **100% correct**:

```json
{
  "type": "text",
  "text": {
    "body": "Hello"
  }
}
```

**Nothing is missing.** The issue is that WhatsApp **rejects** it because:
- You're outside the 24-hour window, OR
- Your account isn't approved for free-form messaging

## Solution: Use Template Messages

Since template messages work for you, **always use them** for:
- Stock alerts
- Notifications
- Initial messages
- Any automated messages

### Template Message Format (Working)

```json
{
  "type": "template",
  "template": {
    "name": "your_template_name",
    "language": {
      "code": "en_US"
    }
  }
}
```

## When Text Messages Would Work

Text messages would work if:

1. **User messages you first:**
   ```
   User: "Hello"
   You: [Can send text message within 24h]
   ```

2. **Within 24-hour window:**
   ```
   User messages at 10:00 AM
   You can send text until 10:00 AM next day
   After that, must use template
   ```

3. **Account approved:**
   - Business verification complete
   - Free-form messaging enabled
   - Still subject to 24-hour rule for initial messages

## Error Codes You Might See

- **131047**: Message failed (usually 24-hour window expired)
- **100**: Invalid parameter (check format)
- **131026**: Too many messages (rate limit)

## Recommendation

**Always use template messages** for automated/scripted messages because:
- ✅ They work reliably
- ✅ No 24-hour restriction
- ✅ Can initiate conversations
- ✅ Already working in your setup

Only use text messages for:
- Manual customer service replies
- Within 24-hour active conversation window
- When you know the conversation is active

## Testing Text Messages

If you want to test text messages:

1. **Have user message you first** (via WhatsApp)
2. **Send text message within 24 hours**
3. **Check if it works**

But for your use case (stock alerts, automated notifications), **stick with template messages** - they're the right tool for the job.

