from app.controllers import news

from . import api_bp


@api_bp.get("/news")
def list_news():
    return news.list_news()


@api_bp.get("/news/<int:news_id>")
def get_news(news_id: int):
    return news.get_news(news_id)
