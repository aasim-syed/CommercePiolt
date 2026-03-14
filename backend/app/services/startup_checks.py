from __future__ import annotations
from contextlib import asynccontextmanager
from app.config import settings
from app.services.logger import get_logger

logger = get_logger("startup")

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_startup_checks()
    yield

def run_startup_checks() -> None:
    pine_labs_mode = "mock" if settings.use_mock_pine_labs else "http"

    logger.info(
        "startup_config_summary",
        extra={
            "extra_data": {
                "app_env": settings.app_env,
                "pine_labs_mode": pine_labs_mode,
                "pine_labs_base_url": settings.pine_labs_base_url,
                "pine_labs_merchant_id_present": bool(settings.pine_labs_merchant_id),
                "bedrock_model_id": settings.bedrock_model_id,
                "aws_region": settings.aws_region,
                "allowed_origins": settings.allowed_origins_list,
            }
        },
    )

    if not settings.use_mock_pine_labs:
        missing = []

        if not settings.pine_labs_base_url:
            missing.append("PINE_LABS_BASE_URL")
        if not settings.pine_labs_api_key:
            missing.append("PINE_LABS_API_KEY")
        if not settings.pine_labs_merchant_id:
            missing.append("PINE_LABS_MERCHANT_ID")

        if missing:
            raise RuntimeError(
                f"Missing required Pine Labs config for HTTP mode: {', '.join(missing)}"
            )

    missing_bedrock = []

    if not settings.aws_region:
        missing_bedrock.append("AWS_REGION")
    if not settings.aws_access_key_id:
        missing_bedrock.append("AWS_ACCESS_KEY_ID")
    if not settings.aws_secret_access_key:
        missing_bedrock.append("AWS_SECRET_ACCESS_KEY")
    if not settings.bedrock_model_id:
        missing_bedrock.append("BEDROCK_MODEL_ID")

    if missing_bedrock:
        logger.warning(
            "bedrock_config_incomplete",
            extra={"extra_data": {"missing": missing_bedrock}},
        )
