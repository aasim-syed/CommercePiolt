# backend/app/services/session_store.py

from __future__ import annotations

from typing import Dict

from app.schemas.agent import SessionState


class SessionStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create(self, session_id: str | None) -> tuple[str, SessionState]:
        if not session_id or not session_id.strip():
            session_id = "demo-session"

        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState()

        return session_id, self._sessions[session_id]

    def get(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    def update(self, session_id: str, state: SessionState) -> None:
        self._sessions[session_id] = state

    def delete(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]

    def clear(self) -> None:
        self._sessions.clear()

    def find_session_by_payment_ref(self, payment_ref: str) -> tuple[str, SessionState] | None:
        for session_id, state in self._sessions.items():
            if state.last_payment_ref == payment_ref:
                return session_id, state
        return None

    def update_payment_status(self, payment_ref: str, status: str) -> bool:
        found = self.find_session_by_payment_ref(payment_ref)
        if not found:
            return False

        session_id, state = found
        state.last_payment_status = status
        self._sessions[session_id] = state
        return True