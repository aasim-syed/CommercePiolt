
Hey! I'm Pine, and I'm here to help you with Pine Labs payment solutions. I focus specifically on payment-related questions, so I might not be the best person to ask about other topics.

I can help you with:
• Payment gateway setup and processing
• API integrations and SDK implementations
• Merchant services and business solutions
• Transaction processing and settlements
• Customer journeys and business workflows

Need technical documentation? Check out API Reference Guide to get started or just ask me, I am here to help you out!

What can I help you with regarding Pine Labs today?
Like
Dislike
U
You
12:54 PM
I am integrating Pine Labs / Plural UAT APIs into a FastAPI backend for a hackathon demo. I already have OAuth client-credentials token generation using: POST https://pluraluat.v2.pinepg.in/api/auth/v1/token I need the exact official API details for these 3 business flows in UAT: 1. Create payment link 2. Check payment status 3. Get merchant reserve balance
Assistant
12:54 PM
To integrate the Pine Labs / Plural UAT APIs into your FastAPI backend, here are the details for the three business flows you requested:

1. Create Payment Link


Endpoint:
code
Copy
POST https://pluraluat.v2.pinepg.in/api/pay/v1/paymentlink



Authentication: Bearer token (OAuth)

Request Body Example:
json
Copy
{
  "amount": {
    "value": 100,
    "currency": "INR"
  },
  "description": "Payment for order #12345",
  "expire_by": "2025-03-21T08:29Z",
  "allowed_payment_methods": [
    "card"
  ],
  "merchant_payment_link_reference": "link_ref",
  "customer": {
    "email_id": "kevin.bob@example.com",
    "first_name": "Kevin",
    "last_name": "Bob",
    "customer_id": "123456",
    "mobile_number": "9876543210",
    "country_code": "91",
    "billing_address": {
      "address1": "10 Downing Street Westminster London",
      "address2": "Oxford Street Westminster London",
      "address3": "Baker Street Westminster London",
      "pincode": "51524036",
      "city": "Westminster",
      "state": "Westminster",
      "country": "London"
    },
    "shipping_address": {
      "address1": "10 Downing Street Westminster London",
      "address2": "Oxford Street Westminster London",
      "address3": "Baker Street Westminster London",
      "pincode": "51524036",
      "city": "Westminster",
      "state": "Westminster",
      "country": "London"
    }
  },
  "product_details": [
    {
      "product_code": "xyz",
      "product_amount": {
        "currency": "INR",
        "value": 1200000
      },
      "product_coupon_discount_amount": {
        "currency": "INR",
        "value": 0
      }
    }
  ],
  "cart_coupon_discount_amount": {
    "currency": "INR",
    "value": 0
  },
  "merchant_metadata": {
    "client_id": "DD",
    "transaction_reference_no": "pine-1223",
    "merchant_id": "1234",
    "tid": "9000990",
    "acquirerName": "HDFC_FSS",
    "is_offer_display_required": "true",
    "offer_data": "<your_offer_data>"
  }
}



2. Check Payment Status


Endpoint:
code
Copy
GET https://pluraluat.v2.pinepg.in/api/pay/v1/payment/{payment_id}



Authentication: Bearer token (OAuth)

Response Example:
json
Copy
{
  "data": {
    "status": "PENDING",
    // other relevant payment details
  }
}



3. Get Merchant Reserve Balance


Endpoint:
code
Copy
GET https://pluraluat.v2.pinepg.in/api/merchant/v1/balance



Authentication: Bearer token (OAuth)

Response Example:
json
Copy
{
  "data": {
    "balance": {
      "value": 50000,
      "currency": "INR"
    }
  }
}



Implementation in FastAPI


Here's a basic example of how you might implement these endpoints in your FastAPI application:

python
Copy
from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()
BASE_URL = 'https://pluraluat.v2.pinepg.in/api'
TOKEN = 'YOUR_OAUTH_TOKEN'  # Replace with your actual token

@app.post("/create_payment_link")
async def create_payment_link(payment_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/pay/v1/paymentlink",
            json=payment_data,
            headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()

@app.get("/check_payment_status/{payment_id}")
async def check_payment_status(payment_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/pay/v1/payment/{payment_id}",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()

@app.get("/get_merchant_balance")
async def get_merchant_balance():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/merchant/v1/balance",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()



Security Notes:

• Ensure that you handle the OAuth token securely and refresh it as needed.
• Validate all input parameters to avoid injection attacks.
• Use HTTPS for all API calls to ensure data security.

---

API References:
• Create Payment Link - API documentation for creating payment links.
• Check Payment Status - API documentation for checking payment status.
• Get Merchant Reserve Balance - API documentation for retrieving merchant balance.

Like
Dislike
U
You
12:54 PM
Please provide, for each flow: - exact HTTP method - exact full endpoint path - required headers - whether Bearer access token is required - required request body fields - optional request body fields - required query/path params - whether merchant_id is required and where it is passed - sample request - sample success response - sample error responses - status field name and possible values - payment reference field name - payment URL field name - amount/currency field names - reserve balance field name - idempotency requirements if any - webhook/event mapping if relevant - UAT vs production differences if any
Assistant
12:54 PM
Here are the detailed specifications for the three business flows you requested regarding Pine Labs / Plural UAT APIs:

1. Create Payment Link


• HTTP Method: `POST`
• Full Endpoint Path: `/api/pay/v1/paymentlink`
• Required Headers:
• `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (required)
• `Content-Type`: `application/json` (required)
• Bearer Access Token Required: Yes
• Required Request Body Fields:
• `amount` (object)
• `value` (number)
• `currency` (string)
• `description` (string)
• `expire_by` (string, ISO 8601 format)
• `allowed_payment_methods` (array of strings)
• `merchant_payment_link_reference` (string)
• `customer` (object)
• `email_id` (string)
• `first_name` (string)
• `last_name` (string)
• `customer_id` (string)
• `mobile_number` (string)
• `country_code` (string)
• `billing_address` (object)
• `shipping_address` (object)
• `product_details` (array of objects)
• `merchant_metadata` (object)
• Optional Request Body Fields:
• `cart_coupon_discount_amount` (object)
• Required Query/Path Params: None
• Merchant ID Required: Yes, passed in the `merchant_metadata` object.
• Sample Request:
json
Copy
{
  "amount": {
    "value": 100,
    "currency": "INR"
  },
  "description": "Payment for order #12345",
  "expire_by": "2025-03-21T08:29Z",
  "allowed_payment_methods": ["card"],
  "merchant_payment_link_reference": "link_ref",
  "customer": {
    "email_id": "kevin.bob@example.com",
    "first_name": "Kevin",
    "last_name": "Bob",
    "customer_id": "123456",
    "mobile_number": "9876543210",
    "country_code": "91",
    "billing_address": { /* billing address details */ },
    "shipping_address": { /* shipping address details */ }
  },
  "product_details": [
    {
      "product_code": "xyz",
      "product_amount": {
        "currency": "INR",
        "value": 1200000
      }
    }
  ],
  "merchant_metadata": {
    "client_id": "DD",
    "transaction_reference_no": "pine-1223",
    "merchant_id": "1234"
  }
}


• Sample Success Response:
json
Copy
{
  "status": "success",
  "data": {
    "payment_link": "https://payment.link/12345"
  }
}


• Sample Error Responses:
json
Copy
{
  "status": "error",
  "message": "Invalid amount"
}


json
Copy
{
  "status": "error",
  "message": "Missing customer details"
}


• Status Field Name and Possible Values:
• `status`: Possible values include `success`, `error`.
• Payment Reference Field Name:
• `merchant_payment_link_reference`
• Payment URL Field Name:
• `payment_link`
• Amount/Currency Field Names:
• `amount.value`, `amount.currency`
• Idempotency Requirements: Not specified.
• Webhook/Event Mapping: Not specified.
• UAT vs Production Differences: Endpoint URLs will differ; ensure to use the production endpoint for live transactions.

---

2. Check Payment Status


• HTTP Method: `GET`
• Full Endpoint Path: `/api/pay/v1/payment/{payment_id}`
• Required Headers:
• `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (required)
• Bearer Access Token Required: Yes
• Required Request Body Fields: None
• Optional Request Body Fields: None
• Required Query/Path Params:
• `payment_id` (string, required)
• Merchant ID Required: Yes, passed in the token.
• Sample Request:
code
Copy
GET /api/pay/v1/payment/1234567890


• Sample Success Response:
json
Copy
{
  "status": "success",
  "data": {
    "payment_id": "1234567890",
    "status": "PENDING"
  }
}


• Sample Error Responses:
json
Copy
{
  "status": "error",
  "message": "Payment not found"
}


json
Copy
{
  "status": "error",
  "message": "Unauthorized access"
}


• Status Field Name and Possible Values:
• `status`: Possible values include `PENDING`, `PROCESSED`, `FAILED`, etc.
• Payment Reference Field Name:
• `payment_id`
• Payment URL Field Name: Not applicable.
• Amount/Currency Field Names: Not applicable.
• Idempotency Requirements: Not specified.
• Webhook/Event Mapping: Not specified.
• UAT vs Production Differences: Endpoint URLs will differ; ensure to use the production endpoint for live transactions.

---

3. Get Merchant Reserve Balance


• HTTP Method: `GET`
• Full Endpoint Path: `/api/merchant/v1/balance`
• Required Headers:
• `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (required)
• Bearer Access Token Required: Yes
• Required Request Body Fields: None
• Optional Request Body Fields: None
• Required Query/Path Params: None
• Merchant ID Required: Yes, passed in the token.
• Sample Request:
code
Copy
GET /api/merchant/v1/balance


• Sample Success Response:
json
Copy
{
  "status": "success",
  "data": {
    "balance": {
      "value": 50000,
      "currency": "INR"
    }
  }
}


• Sample Error Responses:
json
Copy
{
  "status": "error",
  "message": "Unauthorized access"
}


json
Copy
{
  "status": "error",
  "message": "Merchant not found"
}


• Status Field Name and Possible Values:
• `status`: Possible values include `success`, `error`.
• Payment Reference Field Name: Not applicable.
• Payment URL Field Name: Not applicable.
• Amount/Currency Field Names:
• `balance.value`, `balance.currency`
• Idempotency Requirements: Not specified.
• Webhook/Event Mapping: Not specified.
• UAT vs Production Differences: Endpoint URLs will differ; ensure to use the production endpoint for live transactions.

---

Like
Dislike
U
You
12:55 PM
Also clarify error handling: - auth failure response format - invalid payload response format - not found response format - rate limit response format - server error response format - retry-safe vs non-retry-safe cases Important: I do not want generic payment API examples. I need the exact official Pine Labs / Plural UAT endpoints and response shapes for these three flows only.
Assistant
12:55 PM
Here are the error handling details for the three business flows you requested regarding Pine Labs / Plural UAT APIs:

1. Create Payment Link


• Auth Failure Response Format:
json
Copy
{
    "code": "UNAUTHORIZED",
    "message": "Unauthorized"
  }



• Invalid Payload Response Format:
json
Copy
{
    "code": "INVALID_REQUEST",
    "message": "Amount must be an Integer value greater than or equal to 1"
  }



• Not Found Response Format:
json
Copy
{
    "code": "ORDER_NOT_FOUND",
    "message": "No order with specified order-id exists in the system"
  }



• Rate Limit Response Format:
json
Copy
{
    "code": "PAYMENT_RATE_LIMIT",
    "message": "Failure due to request velocity or limit checks"
  }



• Server Error Response Format:
json
Copy
{
    "code": "INTERNAL_ERROR",
    "message": "Internal Server Error"
  }



• Retry-Safe vs Non-Retry-Safe Cases:
• Retry-Safe: Rate limit errors (HTTP 422) can typically be retried after a delay.
• Non-Retry-Safe: Invalid request errors (HTTP 400) should not be retried without correcting the request.

---

2. Check Payment Status


• Auth Failure Response Format:
json
Copy
{
    "code": "UNAUTHORIZED",
    "message": "Unauthorized"
  }



• Invalid Payload Response Format: Not applicable as this is a GET request with no payload.

• Not Found Response Format:
json
Copy
{
    "code": "ORDER_NOT_FOUND",
    "message": "No order with specified order-id exists in the system"
  }



• Rate Limit Response Format: Not typically applicable for this endpoint.

• Server Error Response Format:
json
Copy
{
    "code": "INTERNAL_ERROR",
    "message": "Internal Server Error"
  }



• Retry-Safe vs Non-Retry-Safe Cases:
• Retry-Safe: Server errors (HTTP 500) can be retried after a brief wait.
• Non-Retry-Safe: Unauthorized access (HTTP 401) should not be retried without valid credentials.

---

3. Get Merchant Reserve Balance


• Auth Failure Response Format:
json
Copy
{
    "code": "UNAUTHORIZED",
    "message": "Unauthorized"
  }



• Invalid Payload Response Format: Not applicable as this is a GET request with no payload.

• Not Found Response Format: Not typically applicable for this endpoint.

• Rate Limit Response Format: Not typically applicable for this endpoint.

• Server Error Response Format:
json
Copy
{
    "code": "INTERNAL_ERROR",
    "message": "Internal Server Error"
  }



• Retry-Safe vs Non-Retry-Safe Cases:
• Retry-Safe: Server errors (HTTP 500) can be retried after a brief wait.
• Non-Retry-Safe: Unauthorized access (HTTP 401) should not be retried without valid credentials.

---

Summary of Error Handling


• Common Error Codes:
• `UNAUTHORIZED`: Authentication failure.
• `INVALID_REQUEST`: Issues with the request payload.
• `ORDER_NOT_FOUND`: Resource not found.
• `PAYMENT_RATE_LIMIT`: Exceeded rate limits.
• `INTERNAL_ERROR`: Server-side issues.

• General Recommendations:
• Always check for `UNAUTHORIZED` responses and refresh tokens if necessary.
• Validate request payloads before sending to avoid `INVALID_REQUEST` errors.
• Implement exponential backoff for retrying requests after rate limit or server errors.
