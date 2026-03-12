# backend/app/tools/registry.py

from collections.abc import Callable, Awaitable
from typing import Any

from app.constants import (
    CHECK_PAYMENT_STATUS,
    CREATE_PAYMENT_LINK,
    GET_RESERVE_BALANCE,
)
from app.tools.payments import (
    check_payment_status,
    create_payment_link,
    get_reserve_balance,
)

Tool = Callable[..., Awaitable[dict[str, Any]]]

TOOL_REGISTRY: dict[str, Tool] = {
    CREATE_PAYMENT_LINK: create_payment_link,
    CHECK_PAYMENT_STATUS: check_payment_status,
    GET_RESERVE_BALANCE: get_reserve_balance,
}