from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse, ToolCall
from app.services.agent import handle_chat

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    reply, tool_called, session_state, data = handle_chat(
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
