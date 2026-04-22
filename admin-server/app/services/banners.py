from app.extensions import db
from app.models import Banner
from app.services.storage import StorageService
from app.utils.time import beijing_iso


class BannerError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class BannerService:
    @staticmethod
    def serialize(banner: Banner) -> dict:
        return {
            "id": banner.id,
            "image_object_key": banner.image_object_key or "",
            "image_url": StorageService.sign_url(banner.image_object_key),
            "title": banner.title,
            "description": banner.description or "",
            "created_at": beijing_iso(banner.created_at),
            "updated_at": beijing_iso(banner.updated_at),
        }

    @staticmethod
    def list_banners(args) -> dict:
        page = BannerService._positive_int(args.get("page"), default=1)
        page_size = BannerService._positive_int(args.get("page_size"), default=20, maximum=100)
        keyword = (args.get("keyword") or "").strip()

        query = Banner.query.filter(Banner.deleted_at.is_(None))
        if keyword:
            query = query.filter(Banner.title.ilike(f"%{keyword}%"))

        total = query.count()
        items = (
            query.order_by(Banner.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": [BannerService.serialize(item) for item in items],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
            },
        }

    @staticmethod
    def get_banner(banner_id: int) -> Banner:
        banner = Banner.query.filter(
            Banner.id == banner_id,
            Banner.deleted_at.is_(None),
        ).first()
        if not banner:
            raise BannerError("Banner 不存在", 404)
        return banner

    @staticmethod
    def create_banner(data: dict) -> Banner:
        payload = BannerService._validate_payload(data)
        banner = Banner(**payload)
        db.session.add(banner)
        db.session.commit()
        return banner

    @staticmethod
    def update_banner(banner_id: int, data: dict) -> Banner:
        banner = BannerService.get_banner(banner_id)
        payload = BannerService._validate_payload(data)
        for key, value in payload.items():
            setattr(banner, key, value)
        db.session.commit()
        return banner

    @staticmethod
    def delete_banner(banner_id: int) -> None:
        banner = BannerService.get_banner(banner_id)
        banner.soft_delete()
        db.session.commit()

    @staticmethod
    def _validate_payload(data: dict) -> dict:
        title = (data.get("title") or "").strip()
        if not title:
            raise BannerError("Banner 标题不能为空")
        if len(title) > 80:
            raise BannerError("Banner 标题不能超过 80 个字符")

        description = (data.get("description") or "").strip()
        if len(description) > 255:
            raise BannerError("Banner 描述不能超过 255 个字符")

        return {
            "image_object_key": data.get("image_object_key") or "",
            "title": title,
            "description": description,
        }

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
