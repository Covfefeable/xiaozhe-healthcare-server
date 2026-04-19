from app.controllers import chat

from . import api_bp


@api_bp.get("/chat/conversations")
def list_conversations():
    return chat.list_conversations()


@api_bp.post("/chat/conversations")
def create_conversation():
    return chat.create_conversation()


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
