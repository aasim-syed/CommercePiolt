from __future__ import annotations

import httpx
from typing import Any

from app.config import settings
from app.exceptions import AgentExecutionError
from app.services.logger import get_logger
from app.providers.pine_labs_mock import PineLabsMockProvider
from app.providers.pine_labs_http import PineLabsHttpProvider

logger = get_logger("pine_labs")


class PineLabsClient:
    def __init__(self) -> None:
        self.base_url = settings.pine_labs_base_url.rstrip("/")
        self.api_key = settings.pine_labs_api_key
        self.timeout = httpx.Timeout(20.0)

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"

        logger.info(
            "pine_labs_request_started",
            extra={
                "extra_data": {
                    "method": method,
                    "url": url,
                }
            },
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._headers(),
                    json=payload,
                )
        except httpx.RequestError as exc:
            logger.exception(
                "pine_labs_network_error",
                extra={"extra_data": {"url": url}},
            )
            raise AgentExecutionError(f"Pine Labs network error: {exc}") from exc

        if response.status_code >= 400:
            logger.error(
                "pine_labs_api_error",
                extra={
                    "extra_data": {
                        "url": url,
                        "status_code": response.status_code,
                        "response": response.text,
                    }
                },
            )
            raise AgentExecutionError(
                f"Pine Labs API error {response.status_code}: {response.text}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            logger.exception(
                "pine_labs_invalid_json",
                extra={"extra_data": {"url": url}},
            )
            raise AgentExecutionError("Pine Labs returned invalid JSON.") from exc

        logger.info(
            "pine_labs_request_completed",
            extra={
                "extra_data": {
                    "url": url,
                    "status_code": response.status_code,
                }
            },
        )

        return data


pine_labs_client = PineLabsClient()


def get_pine_labs_provider():
    if getattr(settings, "use_mock_pine_labs", True):
        return PineLabsMockProvider()
    return PineLabsHttpProvider()