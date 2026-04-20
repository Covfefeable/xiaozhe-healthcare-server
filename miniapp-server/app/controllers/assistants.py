from flask import request

from app.services.assistants import AssistantError, AssistantService
from app.services.auth import AuthError, AuthService
from app.utils.response import error_response, success_response


def get_current_assistant():
    try:
        user = AuthService.get_current_user(request.headers.get("Authorization"))
        assistant = AssistantService.get_current_assistant(user)
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    except AssistantError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=assistant)
