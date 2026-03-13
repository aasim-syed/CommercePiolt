from __future__ import annotations

from app.config import settings
from app.providers.pine_labs_http import PineLabsHTTPProvider
from app.providers.pine_labs_mock import PineLabsMockProvider


def get_pine_labs_provider():
    if settings.use_mock_pine_labs:
        return PineLabsMockProvider()
    return PineLabsHTTPProvider()