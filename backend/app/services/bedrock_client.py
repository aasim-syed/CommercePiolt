from __future__ import annotations

import json

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings
from app.exceptions import AgentExecutionError
from app.services.logger import get_logger

logger = get_logger("bedrock")


class BedrockClient:
    def __init__(self) -> None:
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
        self.model_id = settings.bedrock_model_id

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 400,
    ) -> str:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt,
                        }
                    ],
                }
            ],
        }

        logger.info(
            "bedrock_request_started",
            extra={
                "extra_data": {
                    "model_id": self.model_id,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }
            },
        )

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
            )
        except (ClientError, BotoCoreError) as exc:
            logger.exception("bedrock_request_failed")
            raise AgentExecutionError(f"Bedrock request failed: {exc}") from exc

        try:
            raw_body = response["body"].read()
            payload = json.loads(raw_body)
            content = payload.get("content", [])
            text_parts = [
                item.get("text", "")
                for item in content
                if item.get("type") == "text"
            ]
            final_text = "\n".join(part for part in text_parts if part).strip()
        except Exception as exc:
            logger.exception("bedrock_response_parse_failed")
            raise AgentExecutionError("Failed to parse Bedrock response") from exc

        if not final_text:
            raise AgentExecutionError("Bedrock returned an empty response")

        logger.info(
            "bedrock_request_completed",
            extra={
                "extra_data": {
                    "model_id": self.model_id,
                    "response_length": len(final_text),
                }
            },
        )

        return final_text


_bedrock_client: BedrockClient | None = None


def get_bedrock_client() -> BedrockClient:
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = BedrockClient()
    return _bedrock_client