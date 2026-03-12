from __future__ import annotations

from typing import Any

from app.constants import (
    CHECK_PAYMENT_STATUS,
    CREATE_PAYMENT_LINK,
    GET_RESERVE_BALANCE,
    MAX_MESSAGE_LENGTH,
)
from app.exceptions import AgentExecutionError, ToolValidationError
from app.services.agent_router import resolve_route
from app.tools.registry import TOOL_REGISTRY
from app.schemas.agent import SessionState, RouteResolution, ToolExecutionResult

SESSION_STORE: dict[str, SessionState] = {}


def get_or_create_session(session_id: str | None) -> tuple[str, SessionState]:
    if not session_id:
        session_id = "demo-session"

    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = SessionState()

    return session_id, SESSION_STORE[session_id]


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

    _session_id, state = get_or_create_session(session_id)

    if merchant_id:
        state["merchant_id"] = merchant_id

    try:
        route_dict = await resolve_route(message=message, session_state=state.model_dump())
        route = RouteResolution(**route_dict)
        intent = route["intent"]
        extracted_args = route["args"]
        route_source = route["source"]

        if intent is None:
            return (
                "I can help with creating payment links, checking payment status, "
                "and fetching reserve balance.",
                None,
                state,
                None,
            )

        if intent == CREATE_PAYMENT_LINK:
            amount = extracted_args.get("amount")
            if amount is None:
                return (
                    "Please specify an amount like 1200.",
                    None,
                    state,
                    None,
                )

            merchant_for_call = extracted_args.get("merchant_id") or state.merchant_id

            tool = TOOL_REGISTRY[CREATE_PAYMENT_LINK]
            result = await tool(
                amount=float(amount),
                merchant_id=merchant_for_call,
            )

            state.last_payment_ref = result.get("payment_ref")
            state["last_order_id"] = result.get("order_id")
            state["last_tool_call"] = CREATE_PAYMENT_LINK

            reply = (
                f"Created payment link for ₹{result['amount']:.2f}. "
                f"Payment ref: {result['payment_ref']}. "
                f"URL: {result['payment_url']}"
            )

            return (
                reply,
                {
                    "tool_name": CREATE_PAYMENT_LINK,
                    "arguments": {
                        "amount": float(amount),
                        "merchant_id": merchant_for_call,
                        "route_source": route_source,
                    },
                },
                state,
                result,
            )

        if intent == CHECK_PAYMENT_STATUS:
            payment_ref = extracted_args.get("payment_ref") or state.get("last_payment_ref")
            if not payment_ref:
                return (
                    "Please provide a payment reference.",
                    None,
                    state,
                    None,
                )

            tool = TOOL_REGISTRY[CHECK_PAYMENT_STATUS]
            result = await tool(payment_ref=str(payment_ref))

            state["last_tool_call"] = CHECK_PAYMENT_STATUS

            reply = f"Payment {payment_ref} status: {result['status']}."

            return (
                reply,
                {
                    "tool_name": CHECK_PAYMENT_STATUS,
                    "arguments": {
                        "payment_ref": str(payment_ref),
                        "route_source": route_source,
                    },
                },
                state,
                result,
            )

        if intent == GET_RESERVE_BALANCE:
            merchant_for_call = extracted_args.get("merchant_id") or state.merchant_id

            tool = TOOL_REGISTRY[GET_RESERVE_BALANCE]
            result = await tool(merchant_id=merchant_for_call)

            state["last_tool_call"] = GET_RESERVE_BALANCE

            reply = (
                f"Your reserve balance is "
                f"₹{result['available_balance']:.2f} {result['currency']}."
            )

            return (
                reply,
                {
                    "tool_name": GET_RESERVE_BALANCE,
                    "arguments": {
                        "merchant_id": merchant_for_call,
                        "route_source": route_source,
                    },
                },
                state,
                result,
            )

        return (
            "Unsupported action.",
            None,
            state,
            None,
        )

    except ToolValidationError:
        raise
    except Exception as exc:
        raise AgentExecutionError(f"Agent failure: {exc}") from exc