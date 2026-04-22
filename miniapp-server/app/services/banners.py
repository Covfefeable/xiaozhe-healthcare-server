from app.models import Banner
from app.services.storage import StorageService


class BannerService:
    @staticmethod
    def serialize(banner: Banner) -> dict:
        return {
            "id": str(banner.id),
            "image_object_key": banner.image_object_key or "",
            "image": StorageService.sign_url(banner.image_object_key),
            "title": banner.title,
            "desc": banner.description or "",
        }

    @staticmethod
    def list_banners() -> list[dict]:
        items = (
            Banner.query.filter(Banner.deleted_at.is_(None))
            .order_by(Banner.created_at.desc())
            .all()
        )
        return [BannerService.serialize(item) for item in items]
