from app.controllers import chat

from . import api_bp


@api_bp.get("/chat/conversations")
def list_conversations():
    return chat.list_conversations()


@api_bp.post("/chat/conversations")
def create_conversation():
    return chat.create_conversation()


@api_bp.post("/chat/customer-service-conversations")
def create_customer_service_conversation():
    return chat.create_customer_service_conversation()


@api_bp.post("/chat/health-manager-conversations")
def create_health_manager_conversation():
    return chat.create_health_manager_conversation()


@api_bp.post("/chat/assistant-user-conversations")
def create_assistant_user_conversation():
    return chat.create_assistant_user_conversation()


@api_bp.get("/chat/conversations/<int:conversation_id>")
def get_conversation(conversation_id: int):
    return chat.get_conversation(conversation_id)


@api_bp.get("/chat/conversations/<int:conversation_id>/messages")
def list_messages(conversation_id: int):
    return chat.list_messages(conversation_id)


@api_bp.post("/chat/conversations/<int:conversation_id>/messages")
def send_message(conversation_id: int):
    return chat.send_message(conversation_id)


@api_bp.post("/chat/conversations/<int:conversation_id>/read")
def mark_read(conversation_id: int):
    return chat.mark_read(conversation_id)
