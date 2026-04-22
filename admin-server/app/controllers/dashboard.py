from flask import request

from app.services.auth import AuthError, AuthService
from app.services.dashboard import DashboardService
from app.utils.response import error_response, success_response


def get_dashboard():
    try:
        AuthService.get_current_user(request.headers.get("Authorization"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=DashboardService.get_dashboard())
