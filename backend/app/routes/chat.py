# backend/app/routes/chat.py

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent import handle_chat
from app.services.logger import get_logger

router = APIRouter(prefix="/agent", tags=["agent"])

logger = get_logger("chat")


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    try:
        reply, tool_called, session_state, tool_result = await handle_chat(
            message=payload.message,
            session_id=payload.session_id,
            merchant_id=payload.merchant_id,
        )

        return ChatResponse(
            reply=reply,
            tool_called=tool_called,
            session_state=session_state,
            tool_result=tool_result,
        )

    except Exception as exc:
        logger.exception(
            "chat_endpoint_failure",
            extra={"extra_data": {"message": payload.message}},
        )
        raise HTTPException(status_code=500, detail=str(exc))