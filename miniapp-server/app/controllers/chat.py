from flask import request

from app.services.auth import AuthError, AuthService
from app.services.chat import ChatError, ChatService
from app.utils.response import error_response, success_response


def _current_user():
    return AuthService.get_current_user(request.headers.get("Authorization"))


def create_conversation():
    try:
        user = _current_user()
        conversation = ChatService.get_or_create_single_conversation(
            user,
            (request.get_json(silent=True) or {}).get("doctor_id"),
        )
    except (AuthError, ChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=conversation)


def create_customer_service_conversation():
    try:
        user = _current_user()
        conversation = ChatService.get_or_create_customer_service_conversation(user)
    except (AuthError, ChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=conversation)


def create_health_manager_conversation():
    try:
        user = _current_user()
        conversation = ChatService.get_or_create_health_manager_conversation(user)
    except (AuthError, ChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=conversation)


def create_assistant_user_conversation():
    try:
        user = _current_user()
        conversation = ChatService.get_or_create_assistant_user_conversation(
            user,
            (request.get_json(silent=True) or {}).get("phone"),
        )
    except (AuthError, ChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=conversation)


def list_conversations():
    try:
        user = _current_user()
        items = ChatService.list_conversations(user, request.args.get("role") or "user")
    except (AuthError, ChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data={"items": items})


def get_conversation(conversation_id: int):
    try:
        user = _current_user()
        role = request.args.get("role") or "user"
        conversation = ChatService.get_conversation(user, conversation_id, role)
    except (AuthError, ChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=ChatService.serialize_conversation(conversation, user, role))


def list_messages(conversation_id: int):
    try:
        user = _current_user()
        items = ChatService.list_messages(user, conversation_id, request.args, request.args.get("role") or "user")
    except (AuthError, ChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data={"items": items})


def send_message(conversation_id: int):
    try:
        user = _current_user()
        data = request.get_json(silent=True) or {}
        message = ChatService.send_message(
            user,
            conversation_id,
            data,
            data.get("role") or request.args.get("role") or "user",
        )
    except (AuthError, ChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=message, message="发送成功", code=200)


def mark_read(conversation_id: int):
    try:
        user = _current_user()
        ChatService.mark_read(user, conversation_id, request.args.get("role") or "user")
    except (AuthError, ChatError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=None)
