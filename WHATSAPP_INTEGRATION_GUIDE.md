# WhatsApp Integration Guide for CareConnect

## Overview

CareConnect now supports WhatsApp integration using Twilio, allowing patients to interact with the AI chatbot directly through WhatsApp. This guide covers setup, configuration, and usage.

## Features

✅ **Phone-Based Authentication**: Users register with phone numbers (required)  
✅ **Country Code Support**: International phone numbers with validation  
✅ **WhatsApp Chatbot**: Full AI assistant access via WhatsApp  
✅ **Appointment Management**: Book, view, and manage appointments through WhatsApp  
✅ **Automatic Validation**: Phone number verification and duplicate prevention  
✅ **Portal Redirect**: Unregistered users receive a link to sign up  
✅ **Welcome Messages**: Automatic greeting on registration  

---

## Prerequisites

1. **Twilio Account** (free or paid)
2. **WhatsApp Business API Access** (via Twilio Sandbox for testing)
3. **Public HTTPS Endpoint** (for webhook - use ngrok for local development)

---

## Setup Instructions

### Step 1: Create Twilio Account

1. Go to [https://www.twilio.com/](https://www.twilio.com/)
2. Sign up for a free account
3. Verify your email and phone number

### Step 2: Set Up WhatsApp Sandbox (for Testing)

1. In Twilio Console, navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Follow instructions to activate your sandbox:
   - Send a WhatsApp message to the Twilio number (e.g., `+1 415 523 8886`)
   - Send the code: `join [your-sandbox-code]`
3. Note down:
   - **Account SID** (found in Dashboard)
   - **Auth Token** (found in Dashboard)
   - **WhatsApp Sandbox Number** (e.g., `whatsapp:+14155238886`)

### Step 3: Configure Environment Variables

Add these to your `.env` file in the `backend` directory:

```env
# WhatsApp Configuration (Twilio)
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=+14155238886
```

**Example:**
```env
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcdef
TWILIO_AUTH_TOKEN=your_32_char_auth_token_here
TWILIO_WHATSAPP_NUMBER=+14155238886
```

### Step 4: Set Up Public Webhook (Local Development)

For local testing, use **ngrok** to create a public HTTPS endpoint:

1. **Install ngrok**: Download from [https://ngrok.com/](https://ngrok.com/)
2. **Start ngrok**:
   ```bash
   ngrok http 8000
   ```
3. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### Step 5: Configure Twilio Webhook

1. In Twilio Console, go to **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
2. Set **When a message comes in** to:
   ```
   https://your-ngrok-url.ngrok.io/api/v1/whatsapp/webhook
   ```
   Replace `your-ngrok-url` with your actual ngrok URL
3. Method: **POST**
4. Save settings

### Step 6: Install Dependencies

```bash
cd backend
pip install twilio==9.0.4
```

Or rebuild Docker:
```bash
docker-compose down
docker-compose build backend
docker-compose up -d
```

---

## Testing the Integration

### 1. Register a New User with Phone Number

1. Go to the CareConnect login page: `http://localhost:5173`
2. Click **Register**
3. Fill in the form:
   - **Name**: John Doe
   - **Email**: john@example.com
   - **Country Code**: +961 (or your country)
   - **Phone**: 1234567 (your actual number)
   - **Password**: password123
   - **Confirm Password**: password123
4. Click **Create Account**

**Expected Result:**
- User is created successfully
- You receive a WhatsApp welcome message from CareConnect

### 2. Send a Message via WhatsApp

1. Open WhatsApp and go to the Twilio sandbox number
2. Send a message: `Hi`

**Expected Result:**
- Bot responds with a greeting and offers to help

### 3. Book an Appointment via WhatsApp

Send: `Book an appointment with Dr. Smith in cardiology for tomorrow at 2pm`

**Expected Result:**
- Bot searches for available slots
- Bot confirms the booking
- You receive confirmation with appointment details

### 4. Check Appointments

Send: `Show my appointments`

**Expected Result:**
- Bot lists all your appointments

### 5. Test Unregistered User

1. Use a different phone number (not registered)
2. Join the Twilio sandbox with that number
3. Send: `Hello`

**Expected Result:**
- Bot sends a link to the registration portal
- Message explains you need to register with your phone number

---

## Edge Cases Covered

### ✅ Phone Number Validation

- **Minimum 7 digits** required
- **Maximum 15 digits** allowed
- **Automatic cleaning** of spaces, hyphens, parentheses
- **Country code validation** against comprehensive list
- **Duplicate prevention**: Phone + country code must be unique

### ✅ User Authentication

- **Phone-based lookup**: Matches country code + phone number
- **Multiple country code formats**: Tries 1-4 digit country codes
- **Partial matching**: Falls back to last 10 digits if exact match fails

### ✅ Unregistered Users

- **Portal link sent automatically**
- **Message explains registration requirement**
- **User can register and return to WhatsApp**

### ✅ Appointment Handling

- **Context-aware**: Uses authenticated user's ID
- **Full booking flow**: Search, book, confirm
- **Email + WhatsApp notifications**: Dual confirmation

### ✅ Error Handling

- **Service gracefully disabled** if credentials missing
- **Logging**: All actions logged for debugging
- **No registration failure**: WhatsApp errors don't block signup

---

## Architecture

### Backend Components

1. **`app/models/user.py`**: Updated User model with `country_code`, `phone` (required), `whatsapp_verified`
2. **`app/schemas/user.py`**: Phone validation, country code list, registration schemas
3. **`app/services/whatsapp_service.py`**: Twilio integration service
4. **`app/api/v1/whatsapp.py`**: Webhook endpoint for incoming messages
5. **`app/api/v1/auth.py`**: Phone validation in registration
6. **`app/core/config.py`**: Twilio configuration settings

### Frontend Components

1. **`frontend/src/pages/Login.tsx`**: Country code dropdown, phone input (required)
2. **`frontend/src/lib/api.ts`**: Updated registration API call

### Database Schema

```sql
ALTER TABLE users ADD COLUMN country_code VARCHAR(10) NOT NULL DEFAULT '+961';
ALTER TABLE users ADD COLUMN whatsapp_verified BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users MODIFY COLUMN phone VARCHAR(50) NOT NULL;
ALTER TABLE users ADD CONSTRAINT uix_phone_country UNIQUE (phone, country_code);
```

---

## API Endpoints

### POST `/api/v1/whatsapp/webhook`

Receives incoming WhatsApp messages from Twilio.

**Request** (form-data from Twilio):
```
From: whatsapp:+9611234567
To: whatsapp:+14155238886
Body: Hi, I need help
MessageSid: SM1234567890
```

**Response**: `200 OK` (empty body)

### GET `/api/v1/whatsapp/webhook`

Webhook verification endpoint.

**Response**: `"WhatsApp webhook endpoint is active"`

### POST `/api/v1/auth/register`

Updated to require phone number and country code.

**Request Body:**
```json
{
  "email": "john@example.com",
  "name": "John Doe",
  "password": "password123",
  "confirm_password": "password123",
  "phone": "1234567",
  "country_code": "+961",
  "role": "patient"
}
```

### POST `/api/v1/auth/login/phone`

New endpoint for phone-based login.

**Request Body:**
```json
{
  "phone": "1234567",
  "country_code": "+961",
  "password": "password123"
}
```

---

## Production Deployment

### For Production (WhatsApp Business API)

1. **Apply for WhatsApp Business API**: Contact Twilio sales
2. **Get approved phone number**: Use your own business number
3. **Update webhook URL**: Use your production domain
4. **Set environment variables** in production:
   ```env
   TWILIO_ACCOUNT_SID=your_prod_account_sid
   TWILIO_AUTH_TOKEN=your_prod_auth_token
   TWILIO_WHATSAPP_NUMBER=+1234567890
   ```

### Security Considerations

- ✅ **Webhook validation**: Verify Twilio signature (TODO: implement)
- ✅ **Rate limiting**: Already implemented via slowapi
- ✅ **Phone number verification**: Comprehensive validation
- ✅ **User authentication**: Required before processing messages
- ✅ **Error handling**: Graceful degradation if service unavailable

---

## Troubleshooting

### Issue: Not receiving WhatsApp messages

**Solutions:**
1. Verify Twilio sandbox is active (send `join [code]` again)
2. Check ngrok is running and webhook URL is correct
3. Check backend logs for webhook calls
4. Verify phone number format matches database

### Issue: Bot not responding

**Solutions:**
1. Check Twilio credentials in `.env`
2. Verify backend is running: `docker-compose ps`
3. Check logs: `docker-compose logs backend`
4. Ensure user is registered with correct phone number

### Issue: Registration fails with phone number

**Solutions:**
1. Ensure phone number has at least 7 digits
2. Select correct country code from dropdown
3. Check for duplicate: Phone + country code must be unique
4. Remove spaces/special characters (frontend does this automatically)

### Issue: Webhook not receiving messages

**Solutions:**
1. Ensure ngrok is running: `ngrok http 8000`
2. Copy exact ngrok URL to Twilio (include `https://`)
3. Add `/api/v1/whatsapp/webhook` to the end
4. Test with GET request first: `curl https://your-url/api/v1/whatsapp/webhook`

---

## Country Codes Supported

The system supports 150+ country codes including:

- **Lebanon**: +961
- **USA/Canada**: +1
- **UK**: +44
- **UAE**: +971
- **Saudi Arabia**: +966
- **Egypt**: +20
- **Jordan**: +962
- **India**: +91
- **China**: +86
- **And many more...**

See `app/schemas/user.py` for the complete list.

---

## Future Enhancements

- [ ] WhatsApp message templates for automated notifications
- [ ] Rich media support (images, documents)
- [ ] WhatsApp status updates for appointments
- [ ] Multi-language support
- [ ] Voice messages support
- [ ] Group chat for family members
- [ ] Video call scheduling via WhatsApp

---

## Support

For issues or questions:
1. Check backend logs: `docker-compose logs backend -f`
2. Check Twilio console for webhook errors
3. Verify environment variables are set correctly
4. Test webhook manually with curl/Postman

---

## Summary

Your CareConnect application now has complete WhatsApp integration! Users can:
- ✅ Register with their phone number (mandatory)
- ✅ Chat with the AI assistant on WhatsApp
- ✅ Book and manage appointments
- ✅ Get appointment confirmations
- ✅ Receive helpful information

Unregistered users automatically get a link to sign up, ensuring seamless onboarding.
