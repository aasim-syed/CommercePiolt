# backend/app/services/agent.py

from __future__ import annotations

from app.constants import (
    CHECK_PAYMENT_STATUS,
    CREATE_PAYMENT_LINK,
    GET_RESERVE_BALANCE,
    MAX_MESSAGE_LENGTH,
)
from app.exceptions import AgentExecutionError, ToolValidationError
from app.schemas.agent import RouteResolution, SessionState
from app.services.agent_router import resolve_route
from app.services.logger import get_logger
from app.services.session_store import SessionStore
from app.tools.registry import TOOL_REGISTRY

logger = get_logger("agent")
session_store = SessionStore()


async def handle_chat(
    message: str,
    session_id: str | None = None,
    merchant_id: str | None = None,
) -> tuple[str, dict[str, object] | None, dict[str, object], dict[str, object] | None]:
    if not message or not message.strip():
        raise ToolValidationError("Message cannot be empty.")

    if len(message) > MAX_MESSAGE_LENGTH:
        raise ToolValidationError(
            f"Message is too long. Maximum allowed length is {MAX_MESSAGE_LENGTH}."
        )

    resolved_session_id, state = session_store.get_or_create(session_id)

    logger.info(
        "agent_request_received",
        extra={
            "extra_data": {
                "session_id": resolved_session_id,
                "merchant_id": merchant_id,
                "message": message,
            }
        },
    )

    if merchant_id:
        state.merchant_id = merchant_id
        session_store.update(resolved_session_id, state)

    try:
        route_dict = await resolve_route(
            message=message,
            session_state=state.model_dump(),
        )
        route = RouteResolution(**route_dict)

        logger.info(
            "agent_route_resolved",
            extra={
                "extra_data": {
                    "session_id": resolved_session_id,
                    "intent": route.intent,
                    "route_source": route.source,
                    "route_args": route.args,
                }
            },
        )

        if route.intent is None:
            return (
                "I can help with creating payment links, checking payment status, "
                "and fetching reserve balance.",
                None,
                state.model_dump(),
                None,
            )

        if route.intent == CREATE_PAYMENT_LINK:
            amount = route.args.get("amount")
            if amount is None:
                return (
                    "Please specify an amount like 1200.",
                    None,
                    state.model_dump(),
                    None,
                )

            merchant_for_call = route.args.get("merchant_id") or state.merchant_id

            tool = TOOL_REGISTRY[CREATE_PAYMENT_LINK]
            result = await tool(
                amount=float(amount),
                merchant_id=merchant_for_call,
            )

            state.last_payment_ref = result.get("payment_ref")
            state.last_order_id = result.get("order_id")
            state.last_tool_call = CREATE_PAYMENT_LINK
            session_store.update(resolved_session_id, state)

            logger.info(
                "tool_executed",
                extra={
                    "extra_data": {
                        "session_id": resolved_session_id,
                        "tool_name": CREATE_PAYMENT_LINK,
                        "payment_ref": result.get("payment_ref"),
                        "order_id": result.get("order_id"),
                    }
                },
            )

            reply = (
                f"Created payment link for ₹{result['amount']:.2f}. "
                f"Payment ref: {result['payment_ref']}. "
                f"URL: {result['payment_url']}"
            )

            tool_called = {
                "tool_name": CREATE_PAYMENT_LINK,
                "arguments": {
                    "amount": float(amount),
                    "merchant_id": merchant_for_call,
                    "route_source": route.source,
                },
            }

            return (
                reply,
                tool_called,
                state.model_dump(),
                result,
            )

        if route.intent == CHECK_PAYMENT_STATUS:
            payment_ref = route.args.get("payment_ref") or state.last_payment_ref
            if not payment_ref:
                return (
                    "Please provide a payment reference.",
                    None,
                    state.model_dump(),
                    None,
                )

            tool = TOOL_REGISTRY[CHECK_PAYMENT_STATUS]
            result = await tool(payment_ref=str(payment_ref))

            state.last_tool_call = CHECK_PAYMENT_STATUS
            session_store.update(resolved_session_id, state)

            logger.info(
                "tool_executed",
                extra={
                    "extra_data": {
                        "session_id": resolved_session_id,
                        "tool_name": CHECK_PAYMENT_STATUS,
                        "payment_ref": str(payment_ref),
                        "status": result.get("status"),
                    }
                },
            )

            reply = f"Payment {payment_ref} status: {result['status']}."

            tool_called = {
                "tool_name": CHECK_PAYMENT_STATUS,
                "arguments": {
                    "payment_ref": str(payment_ref),
                    "route_source": route.source,
                },
            }

            return (
                reply,
                tool_called,
                state.model_dump(),
                result,
            )

        if route.intent == GET_RESERVE_BALANCE:
            merchant_for_call = route.args.get("merchant_id") or state.merchant_id

            tool = TOOL_REGISTRY[GET_RESERVE_BALANCE]
            result = await tool(merchant_id=merchant_for_call)

            state.last_tool_call = GET_RESERVE_BALANCE
            session_store.update(resolved_session_id, state)

            logger.info(
                "tool_executed",
                extra={
                    "extra_data": {
                        "session_id": resolved_session_id,
                        "tool_name": GET_RESERVE_BALANCE,
                        "merchant_id": merchant_for_call,
                    }
                },
            )

            reply = (
                f"Your reserve balance is "
                f"₹{result['available_balance']:.2f} {result['currency']}."
            )

            tool_called = {
                "tool_name": GET_RESERVE_BALANCE,
                "arguments": {
                    "merchant_id": merchant_for_call,
                    "route_source": route.source,
                },
            }

            return (
                reply,
                tool_called,
                state.model_dump(),
                result,
            )

        return (
            "Unsupported action.",
            None,
            state.model_dump(),
            None,
        )

    except ToolValidationError:
        raise
    except Exception as exc:
        logger.exception(
            "agent_failure",
            extra={
                "extra_data": {
                    "session_id": resolved_session_id,
                    "message": message,
                }
            },
        )
        raise AgentExecutionError(f"Agent failure: {exc}") from exc