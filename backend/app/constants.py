# backend/app/constants.py

# Tool names
CREATE_PAYMENT_LINK = "create_payment_link"
CHECK_PAYMENT_STATUS = "check_payment_status"
GET_RESERVE_BALANCE = "get_reserve_balance"

# Payment statuses
STATUS_LINK_CREATED = "LINK_CREATED"
STATUS_PENDING = "PENDING"
STATUS_SUCCESS = "SUCCESS"
STATUS_FAILED = "FAILED"

# Currency
DEFAULT_CURRENCY = "INR"

# Agent limits
AGENT_TIMEOUT_SECONDS = 10
MAX_MESSAGE_LENGTH = 2000