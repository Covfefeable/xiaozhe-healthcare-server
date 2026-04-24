from datetime import date, datetime, timedelta, timezone

from app.extensions import db
from sqlalchemy import func
from sqlalchemy import text

from app.models import Assistant, MiniappHealthRecord, MiniappUser
from app.services.storage import StorageService
from app.utils.time import beijing_iso, beijing_strftime


class UserError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class UserService:
    @staticmethod
    def serialize_user(user: MiniappUser, with_archive: bool = False) -> dict:
        now = date.today()
        age = None
        if user.birthday:
            age = now.year - user.birthday.year - ((now.month, now.day) < (user.birthday.month, user.birthday.day))
        data = {
            "id": user.id,
            "openid": user.openid or "",
            "nickname": user.nickname or "",
            "avatar_object_key": user.avatar_object_key or "",
            "avatar_url": StorageService.sign_url(user.avatar_object_key),
            "phone": user.phone or "",
            "real_name": user.real_name or "",
            "display_name": user.real_name or user.nickname or user.phone or f"用户 {user.id}",
            "gender": user.gender or "unknown",
            "gender_label": {"male": "男", "female": "女"}.get(user.gender or "", "未填写"),
            "birthday": user.birthday.isoformat() if user.birthday else "",
            "age": age,
            "status": user.status,
            "membership_status": "active" if user.membership_expires_at and user.membership_expires_at > datetime.utcnow() else "none",
            "membership_expires_at": beijing_strftime(user.membership_expires_at, "%Y-%m-%d") if user.membership_expires_at else "",
            "membership_expires_at_datetime": beijing_iso(user.membership_expires_at),
            "health_manager_id": user.health_manager_id,
            "health_manager_name": user.health_manager.name if user.health_manager and user.health_manager.deleted_at is None else "",
            "health_manager_phone": user.health_manager.phone if user.health_manager and user.health_manager.deleted_at is None else "",
            "last_login_at": beijing_iso(user.last_login_at),
            "created_at": beijing_iso(user.created_at),
        }
        if with_archive:
            data["archive"] = UserService.serialize_archive(user)
        return data

    @staticmethod
    def serialize_archive(user: MiniappUser) -> dict:
        records = (
            MiniappHealthRecord.query.filter(
                MiniappHealthRecord.user_id == user.id,
                MiniappHealthRecord.deleted_at.is_(None),
            )
            .order_by(MiniappHealthRecord.record_type.asc(), MiniappHealthRecord.sort_order.asc(), MiniappHealthRecord.id.asc())
            .all()
        )
        grouped = {"medical_history": [], "medication": []}
        for record in records:
            if record.record_type in grouped:
                grouped[record.record_type].append(
                    {
                        "id": record.id,
                        "content": record.content or "",
                        "image_object_keys": record.image_object_keys or [],
                        "image_urls": StorageService.sign_urls(record.image_object_keys),
                    }
                )
        return {
            "medical_histories": grouped["medical_history"],
            "medication_records": grouped["medication"],
        }

    @staticmethod
    def list_users(args) -> dict:
        page = UserService._positive_int(args.get("page"), default=1)
        page_size = UserService._positive_int(args.get("page_size"), default=20, maximum=100)
        keyword = (args.get("keyword") or "").strip()
        query = MiniappUser.query.filter(MiniappUser.deleted_at.is_(None))
        if keyword:
            query = query.filter(
                (MiniappUser.phone.ilike(f"%{keyword}%"))
                | (MiniappUser.real_name.ilike(f"%{keyword}%"))
                | (MiniappUser.nickname.ilike(f"%{keyword}%"))
            )
        total = query.count()
        users = query.order_by(MiniappUser.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return {
            "items": [UserService.serialize_user(user) for user in users],
            "pagination": {"page": page, "page_size": page_size, "total": total},
        }

    @staticmethod
    def get_user(user_id: int) -> dict:
        user = MiniappUser.query.filter(MiniappUser.id == user_id, MiniappUser.deleted_at.is_(None)).first()
        if not user:
            raise UserError("用户不存在", 404)
        return UserService.serialize_user(user, with_archive=True)

    @staticmethod
    def renew_membership(user_id: int, data: dict) -> dict:
        user = MiniappUser.query.filter(MiniappUser.id == user_id, MiniappUser.deleted_at.is_(None)).first()
        if not user:
            raise UserError("用户不存在", 404)

        expires_at = UserService._parse_beijing_datetime(data.get("membership_expires_at"))
        user.membership_expires_at = expires_at
        user.membership_status = "active" if expires_at > datetime.utcnow() else "none"
        db.session.commit()
        return UserService.serialize_user(user, with_archive=True)

    @staticmethod
    def assign_health_manager(user_id: int, data: dict) -> dict:
        user = MiniappUser.query.filter(MiniappUser.id == user_id, MiniappUser.deleted_at.is_(None)).first()
        if not user:
            raise UserError("用户不存在", 404)

        mode = str(data.get("mode") or "").strip()
        assistant = None
        if mode == "random":
            assistant = UserService._random_health_manager()
        elif mode == "specified":
            assistant = UserService._specified_health_manager(data.get("assistant_id"))
        else:
            raise UserError("分配方式不正确")

        user.health_manager_id = assistant.id
        UserService._sync_health_manager_conversations(user.id, assistant)
        db.session.commit()
        return UserService.serialize_user(user, with_archive=True)

    @staticmethod
    def _random_health_manager() -> Assistant:
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
            raise UserError("暂无可用健康管家", 404)
        return assistant

    @staticmethod
    def _specified_health_manager(assistant_id) -> Assistant:
        try:
            assistant_id = int(assistant_id)
        except (TypeError, ValueError):
            raise UserError("请选择健康管家") from None

        assistant = Assistant.query.filter(
            Assistant.id == assistant_id,
            Assistant.status == "active",
            Assistant.assistant_type == "health_manager",
            Assistant.deleted_at.is_(None),
        ).first()
        if not assistant:
            raise UserError("健康管家不存在", 404)
        return assistant

    @staticmethod
    def _sync_health_manager_conversations(user_id: int, assistant: Assistant) -> None:
        rows = db.session.execute(
            text(
                """
                SELECT c.id
                FROM miniapp_chat_conversations AS c
                JOIN admin_assistants AS a ON a.id = c.assistant_id
                WHERE c.owner_user_id = :user_id
                  AND c.conversation_type = 'single'
                  AND c.target_type = 'assistant'
                  AND c.deleted_at IS NULL
                  AND a.assistant_type = 'health_manager'
                  AND a.deleted_at IS NULL
                """
            ),
            {"user_id": user_id},
        ).fetchall()
        if not rows:
            return

        now = datetime.utcnow()
        for row in rows:
            conversation_id = row[0]
            db.session.execute(
                text(
                    """
                    UPDATE miniapp_chat_conversations
                    SET assistant_id = :assistant_id,
                        title = :assistant_name,
                        updated_at = :updated_at
                    WHERE id = :conversation_id
                    """
                ),
                {
                    "assistant_id": assistant.id,
                    "assistant_name": assistant.name,
                    "updated_at": now,
                    "conversation_id": conversation_id,
                },
            )
            db.session.execute(
                text(
                    """
                    UPDATE miniapp_chat_conversation_members
                    SET member_id = :assistant_id,
                        display_name = :assistant_name,
                        avatar_object_key = :avatar_object_key,
                        role_label = '健康管家',
                        updated_at = :updated_at
                    WHERE conversation_id = :conversation_id
                      AND member_type = 'assistant'
                      AND deleted_at IS NULL
                    """
                ),
                {
                    "assistant_id": assistant.id,
                    "assistant_name": assistant.name,
                    "avatar_object_key": assistant.avatar_object_key or "",
                    "updated_at": now,
                    "conversation_id": conversation_id,
                },
            )

    @staticmethod
    def _parse_beijing_datetime(value) -> datetime:
        if not value:
            raise UserError("请选择会员有效期")
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            raise UserError("会员有效期格式不正确") from None

        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed - timedelta(hours=8)

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
