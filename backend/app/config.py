from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CommercePilot Backend"
    app_env: str = "dev"
    pine_labs_base_url: str = "https://sandbox.example.com"
    pine_labs_api_key: str = "demo-key"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
