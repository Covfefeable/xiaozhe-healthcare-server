from app.controllers.health import get_health

from . import api_bp


@api_bp.get("/health")
def health_check():
    return get_health()

