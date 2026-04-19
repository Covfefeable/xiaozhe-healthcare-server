from app.services.news import NewsError, NewsService
from app.utils.response import error_response, success_response


def list_news():
    return success_response(data={"items": NewsService.list_news()})


def get_news(news_id: int):
    try:
        news = NewsService.get_news(news_id)
    except NewsError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=news)
