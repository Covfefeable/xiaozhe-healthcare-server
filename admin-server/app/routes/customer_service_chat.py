from app.controllers import customer_service_chat

from . import api_bp


@api_bp.get("/customer-service-chat/conversations")
def list_customer_service_conversations():
    return customer_service_chat.list_conversations()


@api_bp.get("/customer-service-chat/conversations/<int:conversation_id>/messages")
def list_customer_service_messages(conversation_id: int):
    return customer_service_chat.list_messages(conversation_id)


@api_bp.post("/customer-service-chat/conversations/<int:conversation_id>/messages")
def send_customer_service_message(conversation_id: int):
    return customer_service_chat.send_message(conversation_id)


@api_bp.post("/customer-service-chat/conversations/<int:conversation_id>/health-manager-card")
def send_customer_service_health_manager_card(conversation_id: int):
    return customer_service_chat.send_health_manager_card(conversation_id)


@api_bp.post("/customer-service-chat/conversations/<int:conversation_id>/read")
def mark_customer_service_conversation_read(conversation_id: int):
    return customer_service_chat.mark_read(conversation_id)
