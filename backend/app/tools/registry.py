from app.tools.payments import (
    check_payment_status,
    create_payment_link,
    get_reserve_balance,
)

CREATE_PAYMENT_LINK = "create_payment_link"
CHECK_PAYMENT_STATUS = "check_payment_status"
GET_RESERVE_BALANCE = "get_reserve_balance"

TOOL_REGISTRY = {
    CREATE_PAYMENT_LINK: create_payment_link,
    CHECK_PAYMENT_STATUS: check_payment_status,
    GET_RESERVE_BALANCE: get_reserve_balance,
}