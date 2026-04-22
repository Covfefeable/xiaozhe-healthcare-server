from datetime import datetime

from app.extensions import db
from app.models import News
from app.services.storage import StorageService
from app.utils.time import beijing_iso


class NewsError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class NewsService:
    @staticmethod
    def serialize(news: News) -> dict:
        return {
            "id": news.id,
            "cover_image_object_key": news.cover_image_object_key or "",
            "cover_image_url": StorageService.sign_url(news.cover_image_object_key),
            "title": news.title,
            "published_at": beijing_iso(news.published_at),
            "content_markdown": news.content_markdown or "",
            "created_at": beijing_iso(news.created_at),
            "updated_at": beijing_iso(news.updated_at),
        }

    @staticmethod
    def list_news(args) -> dict:
        page = NewsService._positive_int(args.get("page"), default=1)
        page_size = NewsService._positive_int(args.get("page_size"), default=20, maximum=100)
        keyword = (args.get("keyword") or "").strip()

        query = News.query.filter(News.deleted_at.is_(None))
        if keyword:
            query = query.filter(News.title.ilike(f"%{keyword}%"))

        total = query.count()
        items = (
            query.order_by(News.published_at.desc(), News.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": [NewsService.serialize(item) for item in items],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
            },
        }

    @staticmethod
    def get_news(news_id: int) -> News:
        news = News.query.filter(
            News.id == news_id,
            News.deleted_at.is_(None),
        ).first()
        if not news:
            raise NewsError("资讯不存在", 404)
        return news

    @staticmethod
    def create_news(data: dict) -> News:
        payload = NewsService._validate_payload(data)
        news = News(**payload)
        db.session.add(news)
        db.session.commit()
        return news

    @staticmethod
    def update_news(news_id: int, data: dict) -> News:
        news = NewsService.get_news(news_id)
        payload = NewsService._validate_payload(data)
        for key, value in payload.items():
            setattr(news, key, value)
        db.session.commit()
        return news

    @staticmethod
    def delete_news(news_id: int) -> None:
        news = NewsService.get_news(news_id)
        news.soft_delete()
        db.session.commit()

    @staticmethod
    def _validate_payload(data: dict) -> dict:
        title = (data.get("title") or "").strip()
        if not title:
            raise NewsError("资讯标题不能为空")
        if len(title) > 120:
            raise NewsError("资讯标题不能超过 120 个字符")

        content = data.get("content_markdown") or ""
        return {
            "cover_image_object_key": data.get("cover_image_object_key") or "",
            "title": title,
            "published_at": NewsService._parse_datetime(data.get("published_at")),
            "content_markdown": content,
        }

    @staticmethod
    def _parse_datetime(value) -> datetime:
        if not value:
            return datetime.utcnow()
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            raise NewsError("发布时间格式不正确") from None

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
