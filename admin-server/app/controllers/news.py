from flask import request

from app.services.auth import AuthError, AuthService
from app.services.news import NewsError, NewsService
from app.utils.response import error_response, success_response


def _require_auth():
    try:
        AuthService.get_current_user(request.headers.get("Authorization"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return None


def list_news():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        data = NewsService.list_news(request.args)
    except NewsError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def get_news(news_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        news = NewsService.get_news(news_id)
    except NewsError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=NewsService.serialize(news))


def create_news():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        news = NewsService.create_news(request.get_json(silent=True) or {})
    except NewsError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(
        data=NewsService.serialize(news),
        message="创建成功",
        status_code=201,
    )


def update_news(news_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        news = NewsService.update_news(news_id, request.get_json(silent=True) or {})
    except NewsError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=NewsService.serialize(news), message="保存成功")


def delete_news(news_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        NewsService.delete_news(news_id)
    except NewsError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=None, message="删除成功")
