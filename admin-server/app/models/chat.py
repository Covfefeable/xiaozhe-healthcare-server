from app.extensions import db
from app.models.base import BaseModel


class ChatConversation(BaseModel):
    __tablename__ = "miniapp_chat_conversations"

    conversation_type = db.Column(db.String(20), nullable=False, default="single", index=True)
    target_type = db.Column(db.String(30), nullable=False, default="doctor", index=True)
    title = db.Column(db.String(100), nullable=False, default="")
    doctor_id = db.Column(db.BigInteger, db.ForeignKey("admin_doctors.id"), nullable=True, index=True)
    customer_service_id = db.Column(
        db.BigInteger,
        db.ForeignKey("admin_customer_services.id"),
        nullable=True,
        index=True,
    )
    assistant_id = db.Column(db.BigInteger, db.ForeignKey("admin_assistants.id"), nullable=True, index=True)
    owner_user_id = db.Column(db.BigInteger, db.ForeignKey("miniapp_users.id"), nullable=False, index=True)
    last_message_id = db.Column(db.BigInteger, nullable=True)
    last_message_preview = db.Column(db.String(255), nullable=False, default="")
    last_message_type = db.Column(db.String(20), nullable=False, default="")
    last_message_at = db.Column(db.DateTime, nullable=True, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    customer_service = db.relationship("CustomerService", lazy="joined")
    owner_user = db.relationship("MiniappUser", lazy="joined")


class ChatConversationMember(BaseModel):
    __tablename__ = "miniapp_chat_conversation_members"

    conversation_id = db.Column(
        db.BigInteger,
        db.ForeignKey("miniapp_chat_conversations.id"),
        nullable=False,
        index=True,
    )
    member_type = db.Column(db.String(20), nullable=False, index=True)
    member_id = db.Column(db.BigInteger, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=False, default="")
    avatar_object_key = db.Column(db.Text, nullable=False, default="")
    role_label = db.Column(db.String(30), nullable=False, default="")
    invited_by_type = db.Column(db.String(20), nullable=False, default="")
    invited_by_id = db.Column(db.BigInteger, nullable=True)
    unread_count = db.Column(db.Integer, nullable=False, default=0)
    last_read_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)


class ChatMessage(BaseModel):
    __tablename__ = "miniapp_chat_messages"

    conversation_id = db.Column(
        db.BigInteger,
        db.ForeignKey("miniapp_chat_conversations.id"),
        nullable=False,
        index=True,
    )
    sender_type = db.Column(db.String(20), nullable=False, index=True)
    sender_id = db.Column(db.BigInteger, nullable=False, index=True)
    sender_name = db.Column(db.String(100), nullable=False, default="")
    sender_avatar = db.Column(db.Text, nullable=False, default="")
    sender_role_label = db.Column(db.String(30), nullable=False, default="")
    message_type = db.Column(db.String(20), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String(20), nullable=False, default="sent", index=True)
    sent_at = db.Column(db.DateTime, nullable=False, index=True)
    recalled_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    attachments = db.relationship("ChatMessageAttachment", lazy="selectin")


class ChatMessageAttachment(BaseModel):
    __tablename__ = "miniapp_chat_message_attachments"

    message_id = db.Column(
        db.BigInteger,
        db.ForeignKey("miniapp_chat_messages.id"),
        nullable=False,
        index=True,
    )
    file_type = db.Column(db.String(20), nullable=False, index=True)
    file_object_key = db.Column(db.Text, nullable=False)
    thumbnail_object_key = db.Column(db.Text, nullable=False, default="")
    file_name = db.Column(db.String(255), nullable=False, default="")
    mime_type = db.Column(db.String(100), nullable=False, default="")
    file_size = db.Column(db.BigInteger, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
