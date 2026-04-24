import json
from datetime import datetime

from app.extensions import db
from app.models import (
    AdminUser,
    Assistant,
    ChatConversation,
    ChatConversationMember,
    ChatMessage,
    ChatMessageAttachment,
    CustomerService,
)
from app.services.storage import StorageService
from app.services.users import UserService
from app.utils.time import beijing_iso


CHAT_MESSAGE_TYPES = {"text", "image", "video", "assistant_card"}


class CustomerServiceChatError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class CustomerServiceChatService:
    @staticmethod
    def list_conversations(admin_user: AdminUser, page: int = 1, page_size: int = 20) -> dict:
        customer_service = CustomerServiceChatService._customer_service_member(admin_user)
        page = max(int(page or 1), 1)
        page_size = min(max(int(page_size or 20), 1), 100)
        query = (
            ChatConversation.query.join(
                ChatConversationMember,
                ChatConversationMember.conversation_id == ChatConversation.id,
            )
            .filter(
                ChatConversation.target_type == "customer_service",
                ChatConversationMember.member_type == "customer_service",
                ChatConversationMember.member_id == customer_service.id,
                ChatConversationMember.deleted_at.is_(None),
                ChatConversation.deleted_at.is_(None),
            )
        )
        pagination = query.order_by(
            ChatConversation.last_message_at.desc().nullslast(),
            ChatConversation.created_at.desc(),
        ).paginate(page=page, per_page=page_size, error_out=False)
        return {
            "items": [
                CustomerServiceChatService.serialize_conversation(item, customer_service.id)
                for item in pagination.items
            ],
            "pagination": {
                "page": pagination.page,
                "page_size": pagination.per_page,
                "total": pagination.total,
            },
        }

    @staticmethod
    def get_messages(admin_user: AdminUser, conversation_id: int, before_id=None, limit: int = 20) -> list[dict]:
        customer_service = CustomerServiceChatService._customer_service_member(admin_user)
        conversation = CustomerServiceChatService._conversation_for_customer_service(customer_service.id, conversation_id)
        query = ChatMessage.query.filter(
            ChatMessage.conversation_id == conversation.id,
            ChatMessage.deleted_at.is_(None),
        )
        if before_id:
            try:
                query = query.filter(ChatMessage.id < int(before_id))
            except (TypeError, ValueError):
                raise CustomerServiceChatError("消息游标不正确") from None
        messages = query.order_by(ChatMessage.id.desc()).limit(min(max(int(limit or 20), 1), 50)).all()
        return [
            CustomerServiceChatService.serialize_message(item, customer_service.id)
            for item in reversed(messages)
        ]

    @staticmethod
    def send_message(admin_user: AdminUser, conversation_id: int, data: dict) -> dict:
        customer_service = CustomerServiceChatService._customer_service_member(admin_user)
        conversation = CustomerServiceChatService._conversation_for_customer_service(customer_service.id, conversation_id)
        message_type = str(data.get("message_type") or "text").strip()
        if message_type not in {"text", "image", "video"}:
            raise CustomerServiceChatError("消息类型不支持")

        content = str(data.get("content") or "")
        attachments = data.get("attachments") or []
        if message_type == "text" and not content.strip():
            raise CustomerServiceChatError("消息内容不能为空")
        if message_type in {"image", "video"} and not attachments:
            raise CustomerServiceChatError("请上传附件")

        now = datetime.utcnow()
        message = ChatMessage(
            conversation_id=conversation.id,
            sender_type="customer_service",
            sender_id=customer_service.id,
            sender_name=customer_service.name,
            sender_avatar=StorageService.sign_url(customer_service.avatar_object_key),
            sender_role_label="客服",
            message_type=message_type,
            content=content.strip(),
            sent_at=now,
        )
        db.session.add(message)
        db.session.flush()

        for attachment in attachments:
            db.session.add(
                ChatMessageAttachment(
                    message_id=message.id,
                    file_type=attachment.get("file_type") or message_type,
                    file_object_key=attachment.get("file_object_key") or "",
                    thumbnail_object_key=attachment.get("thumbnail_object_key") or "",
                    file_name=attachment.get("file_name") or "",
                    mime_type=attachment.get("mime_type") or "",
                    file_size=attachment.get("file_size"),
                    duration_seconds=attachment.get("duration_seconds"),
                    width=attachment.get("width"),
                    height=attachment.get("height"),
                )
            )

        CustomerServiceChatService._update_conversation_after_send(
            conversation,
            message,
            exclude_member=("customer_service", customer_service.id),
        )
        db.session.commit()
        return CustomerServiceChatService.serialize_message(message, customer_service.id)

    @staticmethod
    def send_health_manager_card(admin_user: AdminUser, conversation_id: int, data: dict) -> dict:
        customer_service = CustomerServiceChatService._customer_service_member(admin_user)
        conversation = CustomerServiceChatService._conversation_for_customer_service(customer_service.id, conversation_id)
        if not conversation.owner_user or conversation.owner_user.deleted_at is not None:
            raise CustomerServiceChatError("会话用户不存在", 404)

        assigned_user = UserService.assign_health_manager(conversation.owner_user_id, data)
        assistant = Assistant.query.filter(
            Assistant.id == assigned_user["health_manager_id"],
            Assistant.deleted_at.is_(None),
        ).first()
        if not assistant:
            raise CustomerServiceChatError("健康管家不存在", 404)

        payload = {
            "assistant_id": str(assistant.id),
            "assistant_name": assistant.name,
            "assistant_type": assistant.assistant_type or "health_manager",
            "assistant_phone": assistant.phone,
            "assistant_avatar": StorageService.sign_url(assistant.avatar_object_key),
            "assistant_avatar_object_key": assistant.avatar_object_key or "",
            "assistant_title": "健康管家",
            "message": f"已为您安排专属健康管家：{assistant.name}",
        }
        now = datetime.utcnow()
        message = ChatMessage(
            conversation_id=conversation.id,
            sender_type="customer_service",
            sender_id=customer_service.id,
            sender_name=customer_service.name,
            sender_avatar=StorageService.sign_url(customer_service.avatar_object_key),
            sender_role_label="客服",
            message_type="assistant_card",
            content=json.dumps(payload, ensure_ascii=False),
            sent_at=now,
        )
        db.session.add(message)
        db.session.flush()
        CustomerServiceChatService._update_conversation_after_send(
            conversation,
            message,
            exclude_member=("customer_service", customer_service.id),
        )
        db.session.commit()
        return CustomerServiceChatService.serialize_message(message, customer_service.id)

    @staticmethod
    def mark_read(admin_user: AdminUser, conversation_id: int) -> None:
        customer_service = CustomerServiceChatService._customer_service_member(admin_user)
        member = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation_id,
            ChatConversationMember.member_type == "customer_service",
            ChatConversationMember.member_id == customer_service.id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        if not member:
            raise CustomerServiceChatError("会话不存在", 404)
        member.unread_count = 0
        member.last_read_at = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def serialize_conversation(conversation: ChatConversation, customer_service_id: int) -> dict:
        user = conversation.owner_user
        member = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.member_type == "customer_service",
            ChatConversationMember.member_id == customer_service_id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        return {
            "id": str(conversation.id),
            "conversation_type": conversation.conversation_type,
            "target_type": conversation.target_type,
            "target_id": str(user.id if user else conversation.owner_user_id),
            "target_name": (user.real_name or user.nickname or user.phone or "用户") if user else "用户",
            "target_title": "就诊者",
            "target_label": user.phone if user and user.phone else "",
            "target_avatar": StorageService.sign_url(user.avatar_object_key) if user else "",
            "last_message_preview": conversation.last_message_preview or "",
            "last_message_type": conversation.last_message_type or "",
            "last_message_at": beijing_iso(conversation.last_message_at),
            "unread_count": member.unread_count if member else 0,
        }

    @staticmethod
    def serialize_message(message: ChatMessage, customer_service_id: int) -> dict:
        card_payload = CustomerServiceChatService._parse_card_payload(message)
        return {
            "id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "sender_type": message.sender_type,
            "sender_id": str(message.sender_id),
            "sender_name": message.sender_name or "",
            "sender_avatar": message.sender_avatar or "",
            "sender_role_label": message.sender_role_label or "",
            "is_mine": message.sender_type == "customer_service" and message.sender_id == customer_service_id,
            "message_type": message.message_type,
            "content": message.content or "",
            "status": message.status,
            "sent_at": beijing_iso(message.sent_at),
            "card_payload": card_payload,
            "attachments": [
                {
                    "id": str(item.id),
                    "file_type": item.file_type,
                    "file_object_key": item.file_object_key,
                    "file_url": StorageService.sign_url(item.file_object_key),
                    "thumbnail_object_key": item.thumbnail_object_key,
                    "thumbnail_url": StorageService.sign_url(item.thumbnail_object_key),
                    "file_name": item.file_name,
                    "mime_type": item.mime_type,
                    "file_size": item.file_size,
                    "duration_seconds": item.duration_seconds,
                    "width": item.width,
                    "height": item.height,
                }
                for item in message.attachments
            ],
        }

    @staticmethod
    def _parse_card_payload(message: ChatMessage) -> dict | None:
        if message.message_type != "assistant_card":
            return None
        try:
            payload = json.loads(message.content or "{}")
        except json.JSONDecodeError:
            return None
        if not isinstance(payload, dict):
            return None
        return payload

    @staticmethod
    def _message_preview(message_type: str, content: str) -> str:
        if message_type == "image":
            return "[图片]"
        if message_type == "video":
            return "[视频]"
        if message_type == "assistant_card":
            return "[健康管家名片]"
        return content.strip()[:255]

    @staticmethod
    def _update_conversation_after_send(
        conversation: ChatConversation,
        message: ChatMessage,
        exclude_member: tuple[str, int] | None = None,
    ) -> None:
        conversation.last_message_id = message.id
        conversation.last_message_type = message.message_type
        conversation.last_message_preview = CustomerServiceChatService._message_preview(
            message.message_type,
            message.content or "",
        )
        conversation.last_message_at = message.sent_at
        members = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.deleted_at.is_(None),
        ).all()
        for member in members:
            if exclude_member and member.member_type == exclude_member[0] and member.member_id == exclude_member[1]:
                continue
            member.unread_count += 1

    @staticmethod
    def _customer_service_member(admin_user: AdminUser) -> CustomerService:
        phone = (admin_user.phone or "").strip()
        if not phone:
            raise CustomerServiceChatError("当前后台账号未绑定手机号，无法使用客服消息", 403)
        customer_service = CustomerService.query.filter(
            CustomerService.phone == phone,
            CustomerService.status == "active",
            CustomerService.deleted_at.is_(None),
        ).first()
        if not customer_service:
            raise CustomerServiceChatError("当前后台账号未匹配到客服身份", 403)
        return customer_service

    @staticmethod
    def _conversation_for_customer_service(customer_service_id: int, conversation_id: int) -> ChatConversation:
        conversation = ChatConversation.query.filter(
            ChatConversation.id == conversation_id,
            ChatConversation.deleted_at.is_(None),
        ).first()
        if not conversation:
            raise CustomerServiceChatError("会话不存在", 404)
        member = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.member_type == "customer_service",
            ChatConversationMember.member_id == customer_service_id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        if not member:
            raise CustomerServiceChatError("无权查看该会话", 403)
        return conversation
