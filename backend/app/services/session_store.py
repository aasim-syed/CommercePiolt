from __future__ import annotations

from typing import Dict

from app.schemas.agent import SessionState


class SessionStore:
    """
    In-memory session store.

    Later this can be replaced by Redis without touching the agent logic.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create(self, session_id: str | None) -> tuple[str, SessionState]:
        if not session_id:
            session_id = "demo-session"

        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState()

        return session_id, self._sessions[session_id]

    def update(self, session_id: str, state: SessionState) -> None:
        self._sessions[session_id] = state

    def get(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]