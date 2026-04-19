from app.models import Banner


class BannerService:
    @staticmethod
    def serialize(banner: Banner) -> dict:
        return {
            "id": str(banner.id),
            "image": banner.image_url or "",
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
