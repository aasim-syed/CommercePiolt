# backend/app/services/agent.py

from __future__ import annotations

import re
from typing import Any

from app.constants import (
    CHECK_PAYMENT_STATUS,
    CREATE_PAYMENT_LINK,
    GET_RESERVE_BALANCE,
    MAX_MESSAGE_LENGTH,
)
from app.exceptions import AgentExecutionError, ToolValidationError
from app.tools.registry import TOOL_REGISTRY

SESSION_STORE: dict[str, dict[str, Any]] = {}


def _get_or_create_session(session_id: str | None) -> tuple[str, dict[str, Any]]:
    if not session_id:
        session_id = "demo-session"

    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = {
            "merchant_id": None,
            "last_payment_ref": None,
            "last_order_id": None,
            "last_tool_call": None,
        }

    return session_id, SESSION_STORE[session_id]


def _extract_amount(message: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d{1,2})?)", message)
    if not match:
        return None
    return float(match.group(1))


def _extract_payment_ref(message: str) -> str | None:
    match = re.search(r"(pay_[a-zA-Z0-9]+)", message)
    if not match:
        return None
    return match.group(1)


async def handle_chat(
    message: str,
    session_id: str | None = None,
    merchant_id: str | None = None,
) -> tuple[str, dict[str, Any] | None, dict[str, Any], dict[str, Any] | None]:
    if not message or not message.strip():
        raise ToolValidationError("Message cannot be empty.")

    if len(message) > MAX_MESSAGE_LENGTH:
        raise ToolValidationError(
            f"Message is too long. Maximum allowed length is {MAX_MESSAGE_LENGTH}."
        )

    normalized = message.strip().lower()
    session_id, state = _get_or_create_session(session_id)

    if merchant_id:
        state["merchant_id"] = merchant_id

    active_merchant_id = state.get("merchant_id") or merchant_id

    try:
        if "payment link" in normalized or "pay" in normalized or "collect" in normalized:
            amount = _extract_amount(message)
            if amount is None:
                reply = "I could not find the amount. Please specify an amount like 1200."
                return reply, None, state, None

            tool = TOOL_REGISTRY[CREATE_PAYMENT_LINK]
            result = await tool(amount=amount, merchant_id=active_merchant_id)

            state["last_payment_ref"] = result.get("payment_ref")
            state["last_order_id"] = result.get("order_id")
            state["last_tool_call"] = CREATE_PAYMENT_LINK

            reply = (
                f"Created payment link for ₹{result['amount']:.2f}. "
                f"Payment ref: {result['payment_ref']}. "
                f"URL: {result['payment_url']}"
            )

            return (
                reply,
                {"tool_name": CREATE_PAYMENT_LINK, "arguments": {"amount": amount}},
                state,
                result,
            )

        if "status" in normalized:
            payment_ref = _extract_payment_ref(message) or state.get("last_payment_ref")
            if not payment_ref:
                reply = "I could not find a payment reference. Please share one like pay_abc123."
                return reply, None, state, None

            tool = TOOL_REGISTRY[CHECK_PAYMENT_STATUS]
            result = await tool(payment_ref=payment_ref)

            state["last_tool_call"] = CHECK_PAYMENT_STATUS

            reply = f"Payment {result['payment_ref']} status: {result['status']}."
            return (
                reply,
                {
                    "tool_name": CHECK_PAYMENT_STATUS,
                    "arguments": {"payment_ref": payment_ref},
                },
                state,
                result,
            )

        if "balance" in normalized or "reserve" in normalized:
            tool = TOOL_REGISTRY[GET_RESERVE_BALANCE]
            result = await tool(merchant_id=active_merchant_id)

            state["last_tool_call"] = GET_RESERVE_BALANCE

            reply = (
                f"Your reserve balance is ₹{result['available_balance']:.2f} "
                f"{result['currency']}."
            )
            return (
                reply,
                {
                    "tool_name": GET_RESERVE_BALANCE,
                    "arguments": {"merchant_id": active_merchant_id},
                },
                state,
                result,
            )

        reply = (
            "I can help with creating payment links, checking payment status, "
            "and fetching reserve balance."
        )
        return reply, None, state, None

    except ToolValidationError:
        raise
    except Exception as exc:
        raise AgentExecutionError(f"Agent failed to process request: {exc}") from exc