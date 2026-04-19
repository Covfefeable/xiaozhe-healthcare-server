from app.controllers import auth

from . import api_bp


@api_bp.post("/auth/phone-login")
def phone_login():
    return auth.phone_login()


@api_bp.post("/auth/wechat-login")
def wechat_login():
    return auth.wechat_login()


@api_bp.get("/me")
def me():
    return auth.me()
