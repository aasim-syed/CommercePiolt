from __future__ import annotations

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CommercePilot Backend"
    app_env: str = "dev"

    use_mock_pine_labs: bool = True
    pine_labs_base_url: str | None = None
    pine_labs_payouts_base_url: str | None = None
    pine_labs_api_key: str | None = None
    pine_labs_client_id: str | None = None
    pine_labs_client_secret: str | None = None
    pine_labs_grant_type: str | None = None
    pine_labs_merchant_id: str | None = None
    pine_labs_webhook_secret: str | None = None
    sandbox_payment_base_url: str | None = None

    aws_region: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_session_token: str | None = None
    bedrock_model_id: str | None = None

    allowed_origins: str | None = None

    ollama_base_url: str | None = None
    ollama_model: str | None = None

    @computed_field
    @property
    def allowed_origins_list(self) -> list[str]:
        if not self.allowed_origins:
            return [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
