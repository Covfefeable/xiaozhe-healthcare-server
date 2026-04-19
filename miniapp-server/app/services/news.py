from app.models import News


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
            "date": news.published_at.isoformat() if news.published_at else None,
            "published_at": news.published_at.isoformat() if news.published_at else None,
            "image": news.cover_image_url or "",
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
