from flask import Blueprint, current_app, request

from app.utils.response import error_response


api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.before_request
def require_api_token():
    if request.method == "OPTIONS":
        return None

    if request.endpoint and request.endpoint.endswith("health_check"):
        return None

    expected_token = current_app.config.get("API_AUTH_TOKEN")
    if not expected_token:
        return None

    token = request.headers.get("Authorization", "")
    if token.startswith("Bearer "):
        token = token.removeprefix("Bearer ").strip()

    if token != expected_token:
        return error_response(message="Unauthorized", code=401)

    return None


from . import health  # noqa: E402,F401

