from app.controllers import news

from . import api_bp


@api_bp.get("/news")
def list_news():
    return news.list_news()


@api_bp.post("/news")
def create_news():
    return news.create_news()


@api_bp.get("/news/<int:news_id>")
def get_news(news_id: int):
    return news.get_news(news_id)


@api_bp.put("/news/<int:news_id>")
def update_news(news_id: int):
    return news.update_news(news_id)


@api_bp.delete("/news/<int:news_id>")
def delete_news(news_id: int):
    return news.delete_news(news_id)
