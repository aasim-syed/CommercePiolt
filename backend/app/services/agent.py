from __future__ import annotations

from app.config import settings
from app.constants import (
    CHECK_PAYMENT_STATUS,
    CREATE_PAYMENT_LINK,
    GET_RESERVE_BALANCE,
    MAX_MESSAGE_LENGTH,
    STATUS_LINK_CREATED,
)
from app.exceptions import AgentExecutionError, ToolValidationError
from app.schemas.agent import RouteResolution
from app.services.agent_router import resolve_route
from app.services.logger import get_logger
from app.services.session_store import session_store
from app.tools.registry import TOOL_REGISTRY

logger = get_logger("agent")


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
                "I can help with creating payment links, checking payment status, and fetching reserve balance.",
                None,
                state.model_dump(),
                None,
            )

        if route.intent == CREATE_PAYMENT_LINK:
            amount = route.args.get("amount")
            currency = route.args.get("currency")
            if amount is None:
                return (
                    "Please specify an amount like 1200.",
                    None,
                    state.model_dump(),
                    None,
                )

            merchant_for_call = (
                route.args.get("merchant_id")
                or state.merchant_id
                or settings.pine_labs_merchant_id
            )

            tool = TOOL_REGISTRY[CREATE_PAYMENT_LINK]
            result = await tool(
                amount=float(amount),
                currency=str(currency).upper() if currency else None,
                merchant_id=merchant_for_call,
            )

            state.merchant_id = merchant_for_call
            state.last_payment_ref = result.get("payment_ref")
            state.last_order_id = result.get("order_id")
            state.last_tool_call = CREATE_PAYMENT_LINK
            state.last_payment_status = result.get("status", STATUS_LINK_CREATED)
            session_store.update(resolved_session_id, state)

            amount_value = float(result.get("amount", amount))
            payment_ref = result.get("payment_ref")
            payment_url = result.get("payment_url")
            currency = result.get("currency", "INR")

            reply = (
                f"Created payment link for {currency} {amount_value:.2f}. "
                f"Payment ref: {payment_ref}. "
                f"URL: {payment_url}"
            )

            return (
                reply,
                {
                    "tool_name": CREATE_PAYMENT_LINK,
                    "arguments": {
                        "amount": float(amount),
                        "currency": str(currency).upper() if currency else None,
                        "merchant_id": merchant_for_call,
                        "route_source": route.source,
                    },
                },
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
            result = await tool(
                payment_ref=str(payment_ref),
                current_status=state.last_payment_status,
            )

            state.last_tool_call = CHECK_PAYMENT_STATUS
            state.last_payment_ref = str(payment_ref)
            state.last_payment_status = result.get("status")
            session_store.update(resolved_session_id, state)

            reply = f"Payment {payment_ref} status: {result['status']}."

            return (
                reply,
                {
                    "tool_name": CHECK_PAYMENT_STATUS,
                    "arguments": {
                        "payment_ref": str(payment_ref),
                        "route_source": route.source,
                    },
                },
                state.model_dump(),
                result,
            )

        if route.intent == GET_RESERVE_BALANCE:
            merchant_for_call = (
                route.args.get("merchant_id")
                or state.merchant_id
                or settings.pine_labs_merchant_id
            )

            tool = TOOL_REGISTRY[GET_RESERVE_BALANCE]
            result = await tool(merchant_id=merchant_for_call)

            state.merchant_id = merchant_for_call
            state.last_tool_call = GET_RESERVE_BALANCE
            session_store.update(resolved_session_id, state)

            balance_value = result.get("available_balance")
            currency = result.get("currency", "INR")

            if balance_value is None:
                reply = f"Reserve balance fetched successfully for merchant {merchant_for_call}."
            else:
                reply = f"Your reserve balance is ₹{float(balance_value):.2f} {currency}."

            return (
                reply,
                {
                    "tool_name": GET_RESERVE_BALANCE,
                    "arguments": {
                        "merchant_id": merchant_for_call,
                        "route_source": route.source,
                    },
                },
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
    except AgentExecutionError:
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
        raise AgentExecutionError("Something went wrong while processing the request.") from exc
