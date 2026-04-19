from flask import Blueprint


api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health_check():
    return {
        "service": "admin-server",
        "status": "ok",
    }

