Please give the exact official UAT API specification for these Pine Labs / Plural flows, not a summary:

1. Create payment link
2. Check payment status
3. Get merchant reserve balance

For each one, provide:

- exact full UAT URL
- HTTP method
- required headers
- exact request body schema
- exact response schema
- exact error schema
- exact field name for payment reference / payment id
- exact field name for payment URL
- exact field name for payment status
- exact possible payment status values
- exact field name for reserve balance value
- whether merchant_id is required, and exactly where it must be passed
- whether bearer token alone is sufficient or merchant-specific headers are also required

Here are the exact official UAT API specifications for the three Pine Labs / Plural flows you requested:

1. Create Payment Link


• Full UAT URL:
code
Copy
https://pluraluat.v2.pinepg.in/api/pay/v1/paymentlink



• HTTP Method:
code
Copy
POST



• Required Headers:
• `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (required)
• `Content-Type`: `application/json` (required)

• Exact Request Body Schema:
json
Copy
{
  "amount": {
    "value": "integer",
    "currency": "string"
  },
  "description": "string",
  "expire_by": "string (ISO 8601 format)",
  "allowed_payment_methods": ["string"],
  "merchant_payment_link_reference": "string",
  "customer": {
    "email_id": "string",
    "first_name": "string",
    "last_name": "string",
    "customer_id": "string",
    "mobile_number": "string",
    "country_code": "string",
    "billing_address": {
      "address1": "string",
      "address2": "string",
      "address3": "string",
      "pincode": "string",
      "city": "string",
      "state": "string",
      "country": "string"
    },
    "shipping_address": {
      "address1": "string",
      "address2": "string",
      "address3": "string",
      "pincode": "string",
      "city": "string",
      "state": "string",
      "country": "string"
    }
  },
  "product_details": [
    {
      "product_code": "string",
      "product_amount": {
        "currency": "string",
        "value": "integer"
      },
      "product_coupon_discount_amount": {
        "currency": "string",
        "value": "integer"
      }
    }
  ],
  "cart_coupon_discount_amount": {
    "currency": "string",
    "value": "integer"
  },
  "merchant_metadata": {
    "client_id": "string",
    "transaction_reference_no": "string",
    "merchant_id": "string",
    "tid": "string",
    "acquirerName": "string",
    "is_offer_display_required": "boolean",
    "offer_data": "string"
  }
}



• Exact Response Schema:
json
Copy
{
  "status": "string",
  "data": {
    "payment_link": "string"
  }
}



• Exact Error Schema:
json
Copy
{
  "code": "string",
  "message": "string"
}



• Field Name for Payment Reference:
code
Copy
merchant_payment_link_reference



• Field Name for Payment URL:
code
Copy
payment_link



• Field Name for Payment Status:
code
Copy
status



• Possible Payment Status Values:
code
Copy
success, error



• Field Name for Reserve Balance Value: Not applicable for this flow.

• Is merchant_id Required?: Yes, it must be passed in the `merchant_metadata` object.

• Is Bearer Token Alone Sufficient?: Yes, no additional merchant-specific headers are required.

---

2. Check Payment Status


• Full UAT URL:
code
Copy
https://pluraluat.v2.pinepg.in/api/pay/v1/payment/{payment_id}



• HTTP Method:
code
Copy
GET



• Required Headers:
• `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (required)

• Exact Request Body Schema: None (GET request)

• Exact Response Schema:
json
Copy
{
  "status": "string",
  "data": {
    "payment_id": "string",
    "status": "string"
  }
}



• Exact Error Schema:
json
Copy
{
  "code": "string",
  "message": "string"
}



• Field Name for Payment Reference:
code
Copy
payment_id



• Field Name for Payment URL: Not applicable for this flow.

• Field Name for Payment Status:
code
Copy
status



• Possible Payment Status Values:
code
Copy
PENDING, PROCESSED, FAILED, AUTHORIZED, CANCELLED, ATTEMPTED, FULLY_REFUNDED, PARTIALLY_REFUNDED



• Field Name for Reserve Balance Value: Not applicable for this flow.

• Is merchant_id Required?: Yes, it is passed in the token.

• Is Bearer Token Alone Sufficient?: Yes, no additional merchant-specific headers are required.

---

3. Get Merchant Reserve Balance


• Full UAT URL:
code
Copy
https://pluraluat.v2.pinepg.in/api/merchant/v1/balance



• HTTP Method:
code
Copy
GET



• Required Headers:
• `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (required)

• Exact Request Body Schema: None (GET request)

• Exact Response Schema:
json
Copy
{
  "status": "string",
  "data": {
    "balance": {
      "value": "integer",
      "currency": "string"
    }
  }
}



• Exact Error Schema:
json
Copy
{
  "code": "string",
  "message": "string"
}



• Field Name for Payment Reference: Not applicable for this flow.

• Field Name for Payment URL: Not applicable for this flow.

• Field Name for Payment Status: Not applicable for this flow.

• Possible Payment Status Values: Not applicable for this flow.

• Field Name for Reserve Balance Value:
code
Copy
balance.value



• Is merchant_id Required?: Yes, it is passed in the token.

• Is Bearer Token Alone Sufficient?: Yes, no additional merchant-specific headers are required.

---

Summary of Error Handling


For all flows, the error response structure is consistent and includes a `code` and `message` field to identify the error type and description.

If you need any further details or examples, feel free to ask!

---

API References:
• Create Payment Link
• Check Payment Status
• Get Merchant Reserve Balance




For create payment link specifically, confirm:
- the minimum required request body for a valid request
- which fields are mandatory vs optional
- the exact success response body including the payment URL and payment identifier

Create Payment Link


• Full UAT URL:
code
Copy
https://pluraluat.v2.pinepg.in/api/pay/v1/paymentlink



• HTTP Method:
code
Copy
POST



• Required Headers:
• `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (required)
• `Content-Type`: `application/json` (required)

• Minimum Required Request Body:
json
Copy
{
  "amount": {
    "value": 1,
    "currency": "INR"
  },
  "merchant_payment_link_reference": "link_ref",
  "customer": {
    "email_id": "customer@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "customer_id": "123456",
    "mobile_number": "9876543210",
    "country_code": "91",
    "billing_address": {
      "address1": "123 Main St",
      "city": "City",
      "state": "State",
      "country": "Country",
      "pincode": "123456"
    },
    "shipping_address": {
      "address1": "123 Main St",
      "city": "City",
      "state": "State",
      "country": "Country",
      "pincode": "123456"
    }
  }
}



• Mandatory Fields:
• `amount` (object)
• `value` (number)
• `currency` (string)
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

• Optional Fields:
• `description` (string)
• `expire_by` (string, ISO 8601 format)
• `allowed_payment_methods` (array of strings)
• `product_details` (array of objects)
• `cart_coupon_discount_amount` (object)
• `merchant_metadata` (object)

• Exact Success Response Body:
json
Copy
{
  "status": "success",
  "data": {
    "payment_link": "https://shortener.v2.pinepg.in/PLUTUS/3rh4jtd",
    "payment_link_id": "pl-v1-250306082755-aa-uT0noy",
    "merchant_payment_link_reference": "link_ref",
    "status": "CREATED"
  }
}



Key Field Names:

• Payment Reference Field Name:
code
Copy
merchant_payment_link_reference



• Payment URL Field Name:
code
Copy
payment_link



• Payment Status Field Name:
code
Copy
status



• Possible Payment Status Values:
code
Copy
CREATED, CLICKED, PAYMENT_INITIATED, PROCESSED, PARTIAL_PROCESSED, EXPIRED, CANCELLED



• Field Name for Reserve Balance Value: Not applicable for this flow.

• Is merchant_id Required?: Yes, it must be passed in the `merchant_metadata` object if included.

• Is Bearer Token Alone Sufficient?: Yes, no additional merchant-specific headers are required.

---

If you need further details or have additional questions, feel free to ask!

---

API References:
• Create Payment Link - API documentation for creating payment links.


For payment status specifically, confirm:
- whether the path parameter is payment_id, order_id, merchant_payment_link_reference, or another field
- which returned field should be treated as the canonical payment status
For the "Check Payment Status" API, here are the specific details you requested:

Check Payment Status


• Path Parameter:
• The path parameter is `payment_id`.

• Canonical Payment Status Field:
• The field that should be treated as the canonical payment status is:
code
Copy
status



Additional Information


• Possible Payment Status Values:
code
Copy
PENDING, PROCESSED, FAILED, AUTHORIZED, CANCELLED, ATTEMPTED, FULLY_REFUNDED, PARTIALLY_REFUNDED



For reserve balance specifically, confirm:
- whether the endpoint is truly `/api/merchant/v1/balance`
- whether any merchant identifier or query param is required
onfirmations for Get Merchant Reserve Balance


• Endpoint: Yes, the endpoint for getting the merchant reserve balance is indeed:
code
Copy
/api/merchant/v1/balance



• Merchant Identifier Requirement: No additional merchant identifier or query parameter is required. The merchant ID is included in the authentication token (Bearer token) that you provide in the request headers.

Summary of API Call


• Full UAT URL:
code
Copy
https://pluraluat.v2.pinepg.in/api/merchant/v1/balance



• HTTP Method:
code
Copy
GET



• Required Headers:
• `Authorization`: `Bearer YOUR_ACCESS_TOKEN` (required)

• Request Body: None (GET request)

• Response Schema:
json
Copy
{
  "status": "string",
  "data": {
    "balance": {
      "value": "integer",
      "currency": "string"
    }
  }
}



Also provide one real example each for:
- successful create link response
- successful payment status response
- successful reserve balance response
- 400 error
- 401/403 error
- 404 error
Here are examples of various API responses for the Pine Labs payment gateway, including successful responses and error responses:

1. Successful Create Payment Link Response

json
Copy
{
  "status": "success",
  "data": {
    "payment_link": "https://shortener.v2.pinepg.in/PLUTUS/3rh4jtd",
    "payment_link_id": "pl-v1-250306082755-aa-uT0noy",
    "merchant_payment_link_reference": "link_ref",
    "status": "CREATED",
    "amount": {
      "value": 100,
      "currency": "INR"
    },
    "amount_due": {
      "value": 100,
      "currency": "INR"
    },
    "order_id": "v1-250131113650-aa-TUzeRY",
    "description": "Payment for order #12345",
    "expire_by": "2025-03-21T08:29Z",
    "allowed_payment_methods": ["NETBANKING"],
    "customer": {
      "email_id": "kevin.bob@example.com",
      "first_name": "Kevin",
      "last_name": "Bob",
      "customer_id": "123456",
      "mobile_number": "9876543210",
      "country_code": "91",
      "billing_address": {
        "address1": "10 Downing Street Westminster London",
        "city": "Westminster",
        "state": "Westminster",
        "country": "London",
        "pincode": "51524036"
      },
      "shipping_address": {
        "address1": "10 Downing Street Westminster London",
        "city": "Westminster",
        "state": "Westminster",
        "country": "London",
        "pincode": "51524036"
      }
    }
  }
}



2. Successful Payment Status Response

json
Copy
{
  "status": "success",
  "data": {
    "payment_id": "v1-250131113650-aa-TUzeRY",
    "status": "PROCESSED"
  }
}



3. Successful Reserve Balance Response

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



4. 400 Error Response

json
Copy
{
  "code": "400",
  "message": "Bad Request - Invalid parameters provided."
}



5. 401/403 Error Response

json
Copy
{
  "code": "401",
  "message": "Unauthorized - Invalid or expired access token."
}



6. 404 Error Response

json
Copy
{
  "code": "404",
  "message": "Not Found - The requested resource could not be found."
}

For the payment status response, the canonical field to be treated as the payment status is the top-level `status` field. This field indicates the overall status of the payment transaction.

Summary:

• Canonical Payment Status Field:
code
Copy
status (top-level)



If you have any further questions or need additional details, feel free to ask!