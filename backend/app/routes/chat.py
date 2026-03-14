from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.exceptions import AgentExecutionError, PineLabsAPIError, ToolValidationError
from app.schemas.chat import ChatRequest, ChatResponse, ToolCall
from app.services.agent import handle_chat
from app.services.logger import get_logger

router = APIRouter(prefix="/agent", tags=["agent"])
logger = get_logger("chat")


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    try:
        reply, tool_called, session_state, data = await handle_chat(
            message=payload.message,
            session_id=payload.session_id,
            merchant_id=payload.merchant_id,
        )

        return ChatResponse(
            reply=reply,
            tool_called=ToolCall(**tool_called) if tool_called else None,
            data=data,
            session_state=session_state,
        )

    except ToolValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc

    except PineLabsAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    except AgentExecutionError as exc:
        raise HTTPException(status_code=500, detail=exc.message) from exc

    except Exception as exc:
        logger.exception(
            "chat_endpoint_failure",
            extra={
                "extra_data": {
                    "message": payload.message,
                    "session_id": payload.session_id,
                    "merchant_id": payload.merchant_id,
                }
            },
        )
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error",
        ) from exc