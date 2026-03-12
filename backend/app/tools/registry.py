from app.constants import (
    CREATE_PAYMENT_LINK,
    CHECK_PAYMENT_STATUS,
    GET_RESERVE_BALANCE,
)

from app.tools.payments import (
    create_payment_link,
    check_payment_status,
    get_reserve_balance,
)

TOOL_REGISTRY = {
    CREATE_PAYMENT_LINK: create_payment_link,
    CHECK_PAYMENT_STATUS: check_payment_status,
    GET_RESERVE_BALANCE: get_reserve_balance,
}