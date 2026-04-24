from flask import request

from app.services.auth import AuthError, AuthService
from app.services.customer_service_chat import CustomerServiceChatError, CustomerServiceChatService
from app.utils.response import error_response, success_response


def _current_user():
    return AuthService.get_current_user(request.headers.get("Authorization"))


def list_conversations():
    try:
        user = _current_user()
        data = CustomerServiceChatService.list_conversations(
            user,
            request.args.get("page") or 1,
            request.args.get("page_size") or 20,
        )
    except (AuthError, CustomerServiceChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def list_messages(conversation_id: int):
    try:
        user = _current_user()
        items = CustomerServiceChatService.get_messages(
            user,
            conversation_id,
            request.args.get("before_id"),
            request.args.get("limit") or 20,
        )
    except (AuthError, CustomerServiceChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data={"items": items})


def send_message(conversation_id: int):
    try:
        user = _current_user()
        message = CustomerServiceChatService.send_message(user, conversation_id, request.get_json(silent=True) or {})
    except (AuthError, CustomerServiceChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=message, message="发送成功")


def send_health_manager_card(conversation_id: int):
    try:
        user = _current_user()
        message = CustomerServiceChatService.send_health_manager_card(
            user,
            conversation_id,
            request.get_json(silent=True) or {},
        )
    except (AuthError, CustomerServiceChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=message, message="发送成功")


def mark_read(conversation_id: int):
    try:
        user = _current_user()
        CustomerServiceChatService.mark_read(user, conversation_id)
    except (AuthError, CustomerServiceChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=None)
