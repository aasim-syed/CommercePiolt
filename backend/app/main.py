# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.request_logger import RequestLoggerMiddleware
from app.routes.chat import router as chat_router
from app.routes.health import router as health_router
from app.routes.webhooks import router as webhook_router
from app.services.startup_checks import run_startup_checks

app = FastAPI(title=settings.app_name)

app.add_middleware(RequestLoggerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)

app.include_router(chat_router)
app.include_router(webhook_router)