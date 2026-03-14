from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, object]:
    return {
        "ok": True,
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "pine_labs_mode": "mock" if settings.use_mock_pine_labs else "http",
        "pine_labs_base_url_configured": bool(settings.pine_labs_base_url),
        "pine_labs_merchant_id_configured": bool(settings.pine_labs_merchant_id),
        "bedrock_configured": bool(
            settings.aws_region
            and settings.aws_access_key_id
            and settings.aws_secret_access_key
            and settings.bedrock_model_id
        ),
    }