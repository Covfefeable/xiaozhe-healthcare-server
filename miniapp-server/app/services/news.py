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
    def serialize(news: News, include_content: bool = False) -> dict:
        data = {
            "id": str(news.id),
            "title": news.title,
            "date": beijing_iso(news.published_at),
            "published_at": beijing_iso(news.published_at),
            "cover_image_object_key": news.cover_image_object_key or "",
            "image": StorageService.sign_url(news.cover_image_object_key),
        }
        if include_content:
            data["content"] = news.content_markdown or ""
        return data

    @staticmethod
    def list_news() -> list[dict]:
        items = (
            News.query.filter(News.deleted_at.is_(None))
            .order_by(News.published_at.desc(), News.created_at.desc())
            .all()
        )
        return [NewsService.serialize(item) for item in items]

    @staticmethod
    def get_news(news_id: int) -> dict:
        news = News.query.filter(
            News.id == news_id,
            News.deleted_at.is_(None),
        ).first()
        if not news:
            raise NewsError("资讯不存在", 404)
        return NewsService.serialize(news, include_content=True)
