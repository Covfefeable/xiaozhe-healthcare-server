from app.controllers import auth

from . import api_bp


@api_bp.post("/auth/register")
def register():
    return auth.register()


@api_bp.post("/auth/login")
def login():
    return auth.login()


@api_bp.get("/auth/me")
def me():
    return auth.me()


@api_bp.post("/auth/logout")
def logout():
    return auth.logout()


@api_bp.get("/auth/config")
def config():
    return auth.config()
