from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CommercePilot Backend"
    app_env: str = "dev"

    pine_labs_base_url: str = "https://sandbox.example.com"
    pine_labs_api_key: str = "demo-key"
    pine_labs_webhook_secret: str = "change-this-secret"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"

    use_mock_pine_labs: bool = True
    sandbox_payment_base_url: str = "https://sandbox.payments.local"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()