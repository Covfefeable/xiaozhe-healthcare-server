from datetime import date, datetime

from app.models import MiniappHealthRecord, MiniappUser
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
            "nickname": user.nickname or "",
            "avatar_url": user.avatar_url or "",
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
                        "image_urls": record.image_urls or [],
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
