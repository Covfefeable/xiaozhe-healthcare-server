from datetime import datetime

from sqlalchemy import func, or_

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
ASSISTANT_TYPE_LABELS = {
    "health_manager": "健康管家",
    "medical_assistant": "医疗助理",
}


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
            ChatService._ensure_conversation_member(conversation.id, "user", user.id)
            ChatService._ensure_conversation_member(conversation.id, "doctor", doctor.id)
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
        ChatService._ensure_conversation_member(conversation.id, "user", user.id)
        ChatService._ensure_conversation_member(conversation.id, "customer_service", customer_service.id)
        db.session.commit()
        return ChatService.serialize_conversation(conversation, user)

    @staticmethod
    def get_or_create_health_manager_conversation(user: MiniappUser) -> dict:
        conversation = ChatConversation.query.filter(
            ChatConversation.conversation_type == "single",
            ChatConversation.target_type == "assistant",
            ChatConversation.owner_user_id == user.id,
            ChatConversation.deleted_at.is_(None),
        ).first()
        if conversation:
            return ChatService.serialize_conversation(conversation, user)

        assistant = (
            Assistant.query.filter(
                Assistant.status == "active",
                Assistant.assistant_type == "health_manager",
                Assistant.deleted_at.is_(None),
            )
            .order_by(func.random())
            .first()
        )
        if not assistant:
            raise ChatError("暂无可用健康管家", 404)

        conversation = ChatConversation(
            conversation_type="single",
            target_type="assistant",
            title=assistant.name,
            owner_user_id=user.id,
            assistant_id=assistant.id,
        )
        db.session.add(conversation)
        db.session.flush()
        ChatService._ensure_conversation_member(conversation.id, "user", user.id)
        ChatService._ensure_conversation_member(conversation.id, "assistant", assistant.id)
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
        ChatService._ensure_conversation_member(conversation.id, "user", target_user.id)
        ChatService._ensure_conversation_member(conversation.id, "assistant", assistant.id)
        db.session.commit()
        return ChatService.serialize_conversation(conversation, user, "assistant")

    @staticmethod
    def search_users_for_assistant(user: MiniappUser, keyword: str = "") -> list[dict]:
        ChatService._staff_member(user, "assistant")
        normalized_keyword = (keyword or "").strip()
        query = MiniappUser.query.filter(
            MiniappUser.id != user.id,
            MiniappUser.status == "active",
            MiniappUser.phone.isnot(None),
            MiniappUser.deleted_at.is_(None),
        )
        if normalized_keyword:
            like = f"%{normalized_keyword}%"
            query = query.filter(
                or_(
                    MiniappUser.phone.ilike(like),
                    MiniappUser.real_name.ilike(like),
                    MiniappUser.nickname.ilike(like),
                )
            )
        users = query.order_by(MiniappUser.updated_at.desc()).limit(50).all()
        return [ChatService.serialize_chat_user(item) for item in users]

    @staticmethod
    def create_assistant_patient_conversation(user: MiniappUser, payload) -> dict:
        assistant = ChatService._staff_member(user, "assistant")
        payload = payload or {}
        phone_list = ChatService._normalize_string_list(payload.get("phones"))
        doctor_ids = ChatService._normalize_id_list(payload.get("doctor_ids"))
        assistant_ids = [
            item_id
            for item_id in ChatService._normalize_id_list(payload.get("assistant_ids"))
            if item_id != assistant.id
        ]
        selected_count = len(phone_list) + len(doctor_ids) + len(assistant_ids)
        if not selected_count:
            raise ChatError("请选择要发起聊天的用户")
        if selected_count == 1 and len(phone_list) == 1:
            return ChatService.get_or_create_assistant_user_conversation(user, phone_list[0])

        users = MiniappUser.query.filter(
            MiniappUser.phone.in_(phone_list),
            MiniappUser.status == "active",
            MiniappUser.deleted_at.is_(None),
        ).all() if phone_list else []
        user_by_phone = {item.phone: item for item in users}
        missing_phones = [phone for phone in phone_list if phone not in user_by_phone]
        if missing_phones:
            raise ChatError(f"未找到手机号：{missing_phones[0]}", 404)

        doctors = Doctor.query.filter(
            Doctor.id.in_(doctor_ids),
            Doctor.deleted_at.is_(None),
        ).all() if doctor_ids else []
        if len(doctors) != len(doctor_ids):
            raise ChatError("医生不存在", 404)

        assistants = Assistant.query.filter(
            Assistant.id.in_(assistant_ids),
            Assistant.status == "active",
            Assistant.deleted_at.is_(None),
        ).all() if assistant_ids else []
        if len(assistants) != len(assistant_ids):
            raise ChatError("助理不存在", 404)

        selected_members = (
            [("user", item.id) for item in users]
            + [("doctor", item.id) for item in doctors]
            + [("assistant", item.id) for item in assistants]
        )
        selected_profiles = [
            ChatService._member_profile(member_type, member_id)
            for member_type, member_id in selected_members
        ]
        if len(selected_members) == 1:
            target_type, target_id = selected_members[0]
            target_profile = selected_profiles[0]
            conversation = ChatConversation(
                conversation_type="single",
                target_type=target_type,
                title=target_profile["name"],
                owner_user_id=user.id,
                doctor_id=target_id if target_type == "doctor" else None,
                assistant_id=target_id if target_type == "assistant" else assistant.id,
            )
            db.session.add(conversation)
            db.session.flush()
            ChatService._ensure_conversation_member(conversation.id, "assistant", assistant.id)
            ChatService._ensure_conversation_member(
                conversation.id,
                target_type,
                target_id,
                invited_by_type="assistant",
                invited_by_id=assistant.id,
            )
            db.session.commit()
            return ChatService.serialize_conversation(conversation, user, "assistant")

        owner_user = users[0] if users else user
        title_names = [profile["name"] or "成员" for profile in selected_profiles[:2]]
        title = "、".join(title_names)
        if len(selected_profiles) > 2:
            title = f"{title}等{len(selected_profiles)}人"
        title = f"{title}的健康咨询"

        conversation = ChatConversation(
            conversation_type="group",
            target_type="assistant",
            title=title,
            owner_user_id=owner_user.id,
            assistant_id=assistant.id,
        )
        db.session.add(conversation)
        db.session.flush()
        ChatService._ensure_conversation_member(conversation.id, "assistant", assistant.id)
        joined_members = [
            ChatService._ensure_conversation_member(
                conversation.id,
                member_type,
                member_id,
                invited_by_type="assistant",
                invited_by_id=assistant.id,
            )
            for member_type, member_id in selected_members
        ]
        ChatService._add_join_messages(conversation, joined_members)
        db.session.commit()
        return ChatService.serialize_conversation(conversation, user, "assistant")

    @staticmethod
    def invite_doctors(user: MiniappUser, conversation_id: int, doctor_ids) -> dict:
        conversation, assistant = ChatService._conversation_for_health_manager(user, conversation_id)
        ids = ChatService._normalize_id_list(doctor_ids)
        if not ids:
            raise ChatError("请选择医生")
        existing_ids = ChatService._existing_member_ids(conversation.id, "doctor")
        ids = [item_id for item_id in ids if item_id not in existing_ids]
        if not ids:
            raise ChatError("选择的医生已在群聊中")
        doctors = Doctor.query.join(Doctor.department).filter(
            Doctor.id.in_(ids),
            Doctor.deleted_at.is_(None),
        ).all()
        available_doctors = [
            doctor for doctor in doctors if doctor.department and doctor.department.deleted_at is None
        ]
        if not available_doctors:
            raise ChatError("医生不存在", 404)
        ChatService._upgrade_to_group(conversation)
        joined_members = []
        for doctor in available_doctors:
            member = ChatService._ensure_conversation_member(
                conversation.id,
                "doctor",
                doctor.id,
                invited_by_type="assistant",
                invited_by_id=assistant.id,
            )
            joined_members.append(member)
        ChatService._add_join_messages(conversation, joined_members)
        db.session.commit()
        return ChatService.serialize_conversation(conversation, user, "assistant")

    @staticmethod
    def invite_assistants(user: MiniappUser, conversation_id: int, assistant_ids) -> dict:
        conversation, health_manager = ChatService._conversation_for_health_manager(user, conversation_id)
        ids = ChatService._normalize_id_list(assistant_ids)
        if not ids:
            raise ChatError("请选择医疗助理")
        existing_ids = ChatService._existing_member_ids(conversation.id, "assistant")
        ids = [item_id for item_id in ids if item_id not in existing_ids]
        if not ids:
            raise ChatError("选择的医疗助理已在群聊中")
        assistants = Assistant.query.filter(
            Assistant.id.in_(ids),
            Assistant.status == "active",
            Assistant.assistant_type == "medical_assistant",
            Assistant.deleted_at.is_(None),
        ).all()
        if not assistants:
            raise ChatError("医疗助理不存在", 404)
        ChatService._upgrade_to_group(conversation)
        joined_members = []
        for assistant in assistants:
            if assistant.id == health_manager.id:
                continue
            member = ChatService._ensure_conversation_member(
                conversation.id,
                "assistant",
                assistant.id,
                invited_by_type="assistant",
                invited_by_id=health_manager.id,
            )
            joined_members.append(member)
        ChatService._add_join_messages(conversation, joined_members)
        db.session.commit()
        return ChatService.serialize_conversation(conversation, user, "assistant")

    @staticmethod
    def list_members(user: MiniappUser, conversation_id: int, role: str = "user") -> list[dict]:
        conversation = ChatService.get_conversation(user, conversation_id, role)
        members = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.deleted_at.is_(None),
        ).order_by(ChatConversationMember.created_at.asc()).all()
        return [ChatService.serialize_member(member) for member in members]

    @staticmethod
    def list_conversations(user: MiniappUser, role: str = "user") -> list[dict]:
        member_type, member_id = ChatService._viewer_member(user, role)
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
        member_type, member_id = ChatService._viewer_member(user, role)
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
        return [
            ChatService.serialize_message(item, viewer_type=member_type, viewer_id=member_id)
            for item in reversed(messages)
        ]

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
        sender_profile = ChatService._member_profile(member_type, member_id)
        message = ChatMessage(
            conversation_id=conversation.id,
            sender_type=member_type,
            sender_id=member_id,
            sender_name=sender_profile["name"],
            sender_avatar=sender_profile["avatar"],
            sender_role_label=sender_profile["role_label"],
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
        target_members = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.deleted_at.is_(None),
        ).all()
        for target_member in target_members:
            if target_member.member_type == member_type and target_member.member_id == member_id:
                continue
            target_member.unread_count += 1
        db.session.commit()
        return ChatService.serialize_message(message, viewer_type=member_type, viewer_id=member_id)

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
        target = ChatService._target_profile(conversation, role, member_type, member_id)
        member = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.member_type == member_type,
            ChatConversationMember.member_id == member_id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        doctor = conversation.doctor
        can_invite = ChatService._can_invite_members(user, role, conversation)
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
            "can_invite_members": can_invite,
        }

    @staticmethod
    def serialize_message(message: ChatMessage, viewer_type: str | None = None, viewer_id: int | None = None) -> dict:
        role = message.sender_type if message.sender_type in {"user", "doctor", "assistant", "customer_service"} else "system"
        sender_profile = (
            {
                "name": message.sender_name,
                "avatar": message.sender_avatar,
                "role_label": message.sender_role_label,
            }
            if message.sender_name or message.sender_avatar or message.sender_role_label
            else ChatService._member_profile(message.sender_type, message.sender_id)
        )
        return {
            "id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "sender_type": message.sender_type,
            "sender_id": str(message.sender_id),
            "sender_name": sender_profile["name"],
            "sender_avatar": sender_profile["avatar"],
            "sender_role_label": sender_profile["role_label"],
            "is_mine": bool(viewer_type == message.sender_type and viewer_id == message.sender_id),
            "role": role,
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
    def serialize_member(member: ChatConversationMember) -> dict:
        profile = (
            {
                "name": member.display_name,
                "avatar": member.avatar_url,
                "role_label": member.role_label,
            }
            if member.display_name or member.avatar_url or member.role_label
            else ChatService._member_profile(member.member_type, member.member_id)
        )
        return {
            "id": str(member.id),
            "conversation_id": str(member.conversation_id),
            "member_type": member.member_type,
            "member_id": str(member.member_id),
            "display_name": profile["name"],
            "avatar_url": profile["avatar"],
            "role_label": profile["role_label"],
        }

    @staticmethod
    def serialize_chat_user(user: MiniappUser) -> dict:
        return {
            "id": str(user.id),
            "name": user.real_name or user.nickname or user.phone or "用户",
            "phone": user.phone or "",
            "avatar_url": user.avatar_url or "",
            "membership_status": user.membership_status,
        }

    @staticmethod
    def _message_preview(message_type: str, content: str) -> str:
        if message_type == "image":
            return "[图片]"
        if message_type == "video":
            return "[视频]"
        return content.strip()[:255]

    @staticmethod
    def _add_join_messages(conversation: ChatConversation, joined_members: list[ChatConversationMember]) -> None:
        for joined_member in joined_members:
            name = joined_member.display_name or "成员"
            content = f"{name}已加入群聊，现在可以开始聊天了"
            now = datetime.utcnow()
            message = ChatMessage(
                conversation_id=conversation.id,
                sender_type="system",
                sender_id=0,
                sender_name="系统",
                sender_avatar="",
                sender_role_label="系统",
                message_type="text",
                content=content,
                sent_at=now,
            )
            db.session.add(message)
            db.session.flush()
            conversation.last_message_id = message.id
            conversation.last_message_type = "text"
            conversation.last_message_preview = content
            conversation.last_message_at = now
            members = ChatConversationMember.query.filter(
                ChatConversationMember.conversation_id == conversation.id,
                ChatConversationMember.deleted_at.is_(None),
            ).all()
            for member in members:
                member.unread_count += 1

    @staticmethod
    def _target_profile(
        conversation: ChatConversation,
        role: str = "user",
        viewer_type: str | None = None,
        viewer_id: int | None = None,
    ) -> dict:
        if conversation.conversation_type == "group":
            user = conversation.owner_user
            name = conversation.title or ((user.real_name or user.nickname or user.phone or "用户") if user else "健康咨询")
            return {
                "id": conversation.id,
                "name": name,
                "title": "群聊",
                "label": "健康咨询",
                "avatar": user.avatar_url if user else "",
            }
        if role in {"doctor", "assistant"} and viewer_type and viewer_id:
            other_member = (
                ChatConversationMember.query.filter(
                    ChatConversationMember.conversation_id == conversation.id,
                    ChatConversationMember.deleted_at.is_(None),
                )
                .filter(
                    or_(
                        ChatConversationMember.member_type != viewer_type,
                        ChatConversationMember.member_id != viewer_id,
                    )
                )
                .order_by(ChatConversationMember.created_at.asc())
                .first()
            )
            if other_member:
                profile = ChatService._member_profile(other_member.member_type, other_member.member_id)
                return {
                    "id": profile["id"],
                    "name": profile["name"],
                    "title": profile["role_label"],
                    "label": profile["role_label"],
                    "avatar": profile["avatar"],
                }
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
                "title": "健康管家",
                "label": "健康管家",
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
    def _conversation_for_health_manager(user: MiniappUser, conversation_id: int):
        assistant = ChatService._staff_member(user, "assistant")
        if assistant.assistant_type != "health_manager":
            raise ChatError("仅健康管家可以邀请成员", 403)
        conversation = ChatService.get_conversation(user, conversation_id, "assistant")
        member = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.member_type == "assistant",
            ChatConversationMember.member_id == assistant.id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        if not member:
            raise ChatError("无权操作该会话", 403)
        return conversation, assistant

    @staticmethod
    def _upgrade_to_group(conversation: ChatConversation) -> None:
        if conversation.conversation_type == "group":
            return
        conversation.conversation_type = "group"
        conversation.target_type = "assistant"
        owner = conversation.owner_user
        owner_name = (owner.real_name or owner.nickname or owner.phone or "用户") if owner else "用户"
        conversation.title = f"{owner_name}的健康咨询"

    @staticmethod
    def _ensure_conversation_member(
        conversation_id: int,
        member_type: str,
        member_id: int,
        invited_by_type: str = "",
        invited_by_id: int | None = None,
    ) -> ChatConversationMember:
        member = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation_id,
            ChatConversationMember.member_type == member_type,
            ChatConversationMember.member_id == member_id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        profile = ChatService._member_profile(member_type, member_id)
        if member:
            member.display_name = member.display_name or profile["name"]
            member.avatar_url = member.avatar_url or profile["avatar"]
            member.role_label = member.role_label or profile["role_label"]
            return member
        member = ChatConversationMember(
            conversation_id=conversation_id,
            member_type=member_type,
            member_id=member_id,
            display_name=profile["name"],
            avatar_url=profile["avatar"],
            role_label=profile["role_label"],
            invited_by_type=invited_by_type,
            invited_by_id=invited_by_id,
        )
        db.session.add(member)
        return member

    @staticmethod
    def _member_profile(member_type: str, member_id: int | None) -> dict:
        fallback = {"id": member_id, "name": "", "avatar": "", "role_label": ""}
        if member_id is None:
            return fallback
        if member_type == "user":
            user = MiniappUser.query.filter(MiniappUser.id == member_id).first()
            return {
                "id": member_id,
                "name": (user.real_name or user.nickname or user.phone or "用户") if user else "用户",
                "avatar": user.avatar_url if user else "",
                "role_label": "就诊者",
            }
        if member_type == "assistant":
            assistant = Assistant.query.filter(Assistant.id == member_id).first()
            assistant_type = assistant.assistant_type if assistant else "health_manager"
            return {
                "id": member_id,
                "name": assistant.name if assistant else "助理",
                "avatar": assistant.avatar_url if assistant else "",
                "role_label": ASSISTANT_TYPE_LABELS.get(assistant_type, "健康管家"),
            }
        if member_type == "doctor":
            doctor = Doctor.query.filter(Doctor.id == member_id).first()
            return {
                "id": member_id,
                "name": doctor.name if doctor else "医生",
                "avatar": doctor.avatar_url if doctor else "",
                "role_label": doctor.title if doctor and doctor.title else "医生",
            }
        if member_type == "customer_service":
            customer_service = CustomerService.query.filter(CustomerService.id == member_id).first()
            return {
                "id": member_id,
                "name": customer_service.name if customer_service else "客服",
                "avatar": customer_service.avatar_url if customer_service else "",
                "role_label": "客服",
            }
        return fallback

    @staticmethod
    def _can_invite_members(user: MiniappUser, role: str, conversation: ChatConversation) -> bool:
        if role != "assistant":
            return False
        try:
            assistant = ChatService._staff_member(user, "assistant")
        except ChatError:
            return False
        return bool(assistant.assistant_type == "health_manager" and ChatService._is_member(conversation.id, "assistant", assistant.id))

    @staticmethod
    def _normalize_id_list(values) -> list[int]:
        if values is None:
            return []
        if not isinstance(values, list):
            values = [values]
        ids: list[int] = []
        for value in values:
            try:
                number = int(value)
            except (TypeError, ValueError):
                continue
            if number > 0 and number not in ids:
                ids.append(number)
        return ids

    @staticmethod
    def _normalize_string_list(values) -> list[str]:
        if values is None:
            return []
        if not isinstance(values, list):
            values = [values]
        items: list[str] = []
        for value in values:
            text = str(value or "").strip()
            if text and text not in items:
                items.append(text)
        return items

    @staticmethod
    def _existing_member_ids(conversation_id: int, member_type: str) -> set[int]:
        members = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation_id,
            ChatConversationMember.member_type == member_type,
            ChatConversationMember.deleted_at.is_(None),
        ).all()
        return {member.member_id for member in members}

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
