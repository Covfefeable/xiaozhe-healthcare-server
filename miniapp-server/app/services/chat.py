from datetime import datetime

from sqlalchemy import func

from app.extensions import db
from app.models import (
    Assistant,
    ChatConversation,
    ChatConversationMember,
    ChatMessage,
    ChatMessageAttachment,
    CustomerService,
    Doctor,
    MiniappUser,
)
from app.utils.time import beijing_iso


class ChatError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


MESSAGE_TYPES = {"text", "image", "video"}


class ChatService:
    @staticmethod
    def get_or_create_single_conversation(user: MiniappUser, doctor_id) -> dict:
        if not ChatService._has_active_membership(user):
            raise ChatError("请充值会员后再咨询医生")
        try:
            doctor_id = int(doctor_id)
        except (TypeError, ValueError):
            raise ChatError("请选择医生") from None
        doctor = Doctor.query.filter(Doctor.id == doctor_id, Doctor.deleted_at.is_(None)).first()
        if not doctor or not doctor.department or doctor.department.deleted_at is not None:
            raise ChatError("医生不存在", 404)
        conversation = ChatConversation.query.filter(
            ChatConversation.conversation_type == "single",
            ChatConversation.target_type == "doctor",
            ChatConversation.owner_user_id == user.id,
            ChatConversation.doctor_id == doctor.id,
            ChatConversation.deleted_at.is_(None),
        ).first()
        if not conversation:
            conversation = ChatConversation(
                conversation_type="single",
                target_type="doctor",
                title=doctor.name,
                owner_user_id=user.id,
                doctor_id=doctor.id,
            )
            db.session.add(conversation)
            db.session.flush()
            db.session.add_all(
                [
                    ChatConversationMember(
                        conversation_id=conversation.id,
                        member_type="user",
                        member_id=user.id,
                    ),
                    ChatConversationMember(
                        conversation_id=conversation.id,
                        member_type="doctor",
                        member_id=doctor.id,
                    ),
                ]
            )
            db.session.commit()
        return ChatService.serialize_conversation(conversation, user)

    @staticmethod
    def get_or_create_customer_service_conversation(user: MiniappUser) -> dict:
        conversation = ChatConversation.query.filter(
            ChatConversation.conversation_type == "single",
            ChatConversation.target_type == "customer_service",
            ChatConversation.owner_user_id == user.id,
            ChatConversation.deleted_at.is_(None),
        ).first()
        if conversation:
            return ChatService.serialize_conversation(conversation, user)

        customer_service = (
            CustomerService.query.filter(
                CustomerService.status == "active",
                CustomerService.deleted_at.is_(None),
            )
            .order_by(func.random())
            .first()
        )
        if not customer_service:
            raise ChatError("暂无可用客服", 404)

        conversation = ChatConversation(
            conversation_type="single",
            target_type="customer_service",
            title=customer_service.name,
            owner_user_id=user.id,
            customer_service_id=customer_service.id,
        )
        db.session.add(conversation)
        db.session.flush()
        db.session.add_all(
            [
                ChatConversationMember(
                    conversation_id=conversation.id,
                    member_type="user",
                    member_id=user.id,
                ),
                ChatConversationMember(
                    conversation_id=conversation.id,
                    member_type="customer_service",
                    member_id=customer_service.id,
                ),
            ]
        )
        db.session.commit()
        return ChatService.serialize_conversation(conversation, user)

    @staticmethod
    def get_or_create_assistant_user_conversation(user: MiniappUser, phone: str) -> dict:
        assistant = ChatService._staff_member(user, "assistant")
        target_phone = (phone or "").strip()
        if not target_phone:
            raise ChatError("请输入用户手机号")
        target_user = MiniappUser.query.filter(
            MiniappUser.phone == target_phone,
            MiniappUser.deleted_at.is_(None),
        ).first()
        if not target_user:
            raise ChatError("未找到该手机号用户", 404)

        conversation = ChatConversation.query.filter(
            ChatConversation.conversation_type == "single",
            ChatConversation.target_type == "assistant",
            ChatConversation.owner_user_id == target_user.id,
            ChatConversation.assistant_id == assistant.id,
            ChatConversation.deleted_at.is_(None),
        ).first()
        if conversation:
            return ChatService.serialize_conversation(conversation, user, "assistant")

        conversation = ChatConversation(
            conversation_type="single",
            target_type="assistant",
            title=assistant.name,
            owner_user_id=target_user.id,
            assistant_id=assistant.id,
        )
        db.session.add(conversation)
        db.session.flush()
        db.session.add_all(
            [
                ChatConversationMember(
                    conversation_id=conversation.id,
                    member_type="user",
                    member_id=target_user.id,
                ),
                ChatConversationMember(
                    conversation_id=conversation.id,
                    member_type="assistant",
                    member_id=assistant.id,
                ),
            ]
        )
        db.session.commit()
        return ChatService.serialize_conversation(conversation, user, "assistant")

    @staticmethod
    def list_conversations(user: MiniappUser, role: str = "user") -> list[dict]:
        member_type, member_id = ChatService._viewer_member(user, role)
        if member_type == "user":
            query = ChatConversation.query.filter(
                ChatConversation.owner_user_id == member_id,
                ChatConversation.deleted_at.is_(None),
            )
        else:
            query = (
                ChatConversation.query.join(
                    ChatConversationMember,
                    ChatConversationMember.conversation_id == ChatConversation.id,
                )
                .filter(
                    ChatConversationMember.member_type == member_type,
                    ChatConversationMember.member_id == member_id,
                    ChatConversationMember.deleted_at.is_(None),
                    ChatConversation.deleted_at.is_(None),
                )
            )
        conversations = query.order_by(
            ChatConversation.last_message_at.desc().nullslast(),
            ChatConversation.created_at.desc(),
        ).all()
        return [ChatService.serialize_conversation(item, user, role) for item in conversations]

    @staticmethod
    def get_conversation(user: MiniappUser, conversation_id: int, role: str = "user") -> ChatConversation:
        member_type, member_id = ChatService._viewer_member(user, role)
        conversation = ChatConversation.query.filter(
            ChatConversation.id == conversation_id,
            ChatConversation.deleted_at.is_(None),
        ).first()
        if not conversation or not ChatService._is_member(conversation.id, member_type, member_id):
            raise ChatError("会话不存在", 404)
        return conversation

    @staticmethod
    def list_messages(user: MiniappUser, conversation_id: int, args, role: str = "user") -> list[dict]:
        conversation = ChatService.get_conversation(user, conversation_id, role)
        limit = ChatService._positive_int(args.get("limit"), default=20, maximum=50)
        before_id = args.get("before_id")
        query = ChatMessage.query.filter(
            ChatMessage.conversation_id == conversation.id,
            ChatMessage.deleted_at.is_(None),
        )
        if before_id:
            try:
                query = query.filter(ChatMessage.id < int(before_id))
            except (TypeError, ValueError):
                raise ChatError("消息游标不正确") from None
        messages = query.order_by(ChatMessage.id.desc()).limit(limit).all()
        return [ChatService.serialize_message(item) for item in reversed(messages)]

    @staticmethod
    def send_message(user: MiniappUser, conversation_id: int, data: dict, role: str = "user") -> dict:
        conversation = ChatService.get_conversation(user, conversation_id, role)
        member_type, member_id = ChatService._viewer_member(user, role)
        if role == "user" and conversation.target_type == "doctor" and not ChatService._has_active_membership(user):
            raise ChatError("请充值会员后再咨询医生")
        message_type = data.get("message_type") or "text"
        if message_type not in MESSAGE_TYPES:
            raise ChatError("消息类型不支持")
        content = data.get("content") or ""
        attachments = data.get("attachments") or []
        if message_type == "text" and not content.strip():
            raise ChatError("消息内容不能为空")
        if message_type in {"image", "video"} and not attachments:
            raise ChatError("请上传附件")

        now = datetime.utcnow()
        message = ChatMessage(
            conversation_id=conversation.id,
            sender_type=member_type,
            sender_id=member_id,
            message_type=message_type,
            content=content,
            sent_at=now,
        )
        db.session.add(message)
        db.session.flush()

        for attachment in attachments:
            db.session.add(
                ChatMessageAttachment(
                    message_id=message.id,
                    file_type=attachment.get("file_type") or message_type,
                    file_url=attachment.get("file_url") or "",
                    thumbnail_url=attachment.get("thumbnail_url") or "",
                    file_name=attachment.get("file_name") or "",
                    mime_type=attachment.get("mime_type") or "",
                    file_size=attachment.get("file_size"),
                    duration_seconds=attachment.get("duration_seconds"),
                    width=attachment.get("width"),
                    height=attachment.get("height"),
                )
            )

        conversation.last_message_id = message.id
        conversation.last_message_type = message_type
        conversation.last_message_preview = ChatService._message_preview(message_type, content)
        conversation.last_message_at = now
        target_member_type, target_member_id = ChatService._target_member(conversation, member_type)
        target_member = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.member_type == target_member_type,
            ChatConversationMember.member_id == target_member_id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        if target_member:
            target_member.unread_count += 1
        db.session.commit()
        return ChatService.serialize_message(message)

    @staticmethod
    def mark_read(user: MiniappUser, conversation_id: int, role: str = "user") -> None:
        conversation = ChatService.get_conversation(user, conversation_id, role)
        member_type, member_id = ChatService._viewer_member(user, role)
        member = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.member_type == member_type,
            ChatConversationMember.member_id == member_id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        if member:
            member.unread_count = 0
            member.last_read_at = datetime.utcnow()
            db.session.commit()

    @staticmethod
    def serialize_conversation(conversation: ChatConversation, user: MiniappUser, role: str = "user") -> dict:
        member_type, member_id = ChatService._viewer_member(user, role)
        target = ChatService._target_profile(conversation, role)
        member = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.member_type == member_type,
            ChatConversationMember.member_id == member_id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        doctor = conversation.doctor
        return {
            "id": str(conversation.id),
            "conversation_type": conversation.conversation_type,
            "target_type": conversation.target_type,
            "target_id": str(target["id"]) if target["id"] else "",
            "target_name": target["name"],
            "target_title": target["title"],
            "target_label": target["label"],
            "target_avatar": target["avatar"],
            "doctor_id": str(doctor.id) if doctor else "",
            "doctor_name": doctor.name if doctor else target["name"],
            "doctor_title": doctor.title if doctor else target["title"],
            "department_name": doctor.department.name if doctor and doctor.department else target["label"],
            "doctor_avatar": doctor.avatar_url if doctor else target["avatar"],
            "last_message_preview": conversation.last_message_preview or "",
            "last_message_type": conversation.last_message_type or "",
            "last_message_at": beijing_iso(conversation.last_message_at),
            "unread_count": member.unread_count if member else 0,
        }

    @staticmethod
    def serialize_message(message: ChatMessage) -> dict:
        return {
            "id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "sender_type": message.sender_type,
            "sender_id": str(message.sender_id),
            "role": "user" if message.sender_type == "user" else "doctor",
            "message_type": message.message_type,
            "content": message.content or "",
            "status": message.status,
            "sent_at": beijing_iso(message.sent_at),
            "attachments": [
                {
                    "id": str(item.id),
                    "file_type": item.file_type,
                    "file_url": item.file_url,
                    "thumbnail_url": item.thumbnail_url,
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
    def _message_preview(message_type: str, content: str) -> str:
        if message_type == "image":
            return "[图片]"
        if message_type == "video":
            return "[视频]"
        return content.strip()[:255]

    @staticmethod
    def _target_profile(conversation: ChatConversation, role: str = "user") -> dict:
        if role in {"doctor", "assistant"}:
            user = conversation.owner_user
            return {
                "id": user.id if user else conversation.owner_user_id,
                "name": (user.real_name or user.nickname or user.phone or "患者") if user else conversation.title,
                "title": "患者",
                "label": user.phone if user else "患者",
                "avatar": user.avatar_url if user else "",
            }
        if conversation.target_type == "customer_service":
            item = conversation.customer_service
            return {
                "id": item.id if item else conversation.customer_service_id,
                "name": item.name if item else conversation.title,
                "title": "客服",
                "label": "客服",
                "avatar": item.avatar_url if item else "",
            }
        if conversation.target_type == "assistant":
            item = conversation.assistant
            return {
                "id": item.id if item else conversation.assistant_id,
                "name": item.name if item else conversation.title,
                "title": "助理",
                "label": "助理",
                "avatar": item.avatar_url if item else "",
            }
        doctor = conversation.doctor
        return {
            "id": doctor.id if doctor else conversation.doctor_id,
            "name": doctor.name if doctor else conversation.title,
            "title": doctor.title if doctor else "",
            "label": doctor.department.name if doctor and doctor.department else "",
            "avatar": doctor.avatar_url if doctor else "",
        }

    @staticmethod
    def _target_member(conversation: ChatConversation, sender_type: str = "user") -> tuple[str, int | None]:
        if sender_type != "user":
            return "user", conversation.owner_user_id
        if conversation.target_type == "customer_service":
            return "customer_service", conversation.customer_service_id
        if conversation.target_type == "assistant":
            return "assistant", conversation.assistant_id
        return "doctor", conversation.doctor_id

    @staticmethod
    def _viewer_member(user: MiniappUser, role: str = "user") -> tuple[str, int]:
        normalized_role = role if role in {"user", "doctor", "assistant"} else "user"
        if normalized_role == "user":
            return "user", user.id
        staff = ChatService._staff_member(user, normalized_role)
        return normalized_role, staff.id

    @staticmethod
    def _staff_member(user: MiniappUser, role: str):
        phone = (user.phone or "").strip()
        if not phone:
            raise ChatError("当前登录用户未绑定手机号", 403)
        if role == "doctor":
            doctor = Doctor.query.filter(
                Doctor.phone == phone,
                Doctor.deleted_at.is_(None),
            ).first()
            if doctor and doctor.department and doctor.department.deleted_at is None:
                return doctor
            raise ChatError("当前账号不是医生身份", 403)
        if role == "assistant":
            assistant = Assistant.query.filter(
                Assistant.phone == phone,
                Assistant.status == "active",
                Assistant.deleted_at.is_(None),
            ).first()
            if assistant:
                return assistant
            raise ChatError("当前账号不是助理身份", 403)
        raise ChatError("角色不支持", 400)

    @staticmethod
    def _is_member(conversation_id: int, member_type: str, member_id: int) -> bool:
        return (
            ChatConversationMember.query.filter(
                ChatConversationMember.conversation_id == conversation_id,
                ChatConversationMember.member_type == member_type,
                ChatConversationMember.member_id == member_id,
                ChatConversationMember.deleted_at.is_(None),
            ).first()
            is not None
        )

    @staticmethod
    def _has_active_membership(user: MiniappUser) -> bool:
        return bool(user.membership_expires_at and user.membership_expires_at > datetime.utcnow())

    @staticmethod
    def _positive_int(value, default: int, maximum: int | None = None) -> int:
        try:
            number = int(value)
        except (TypeError, ValueError):
            number = default
        if number < 1:
            number = default
        if maximum is not None:
            number = min(number, maximum)
        return number
