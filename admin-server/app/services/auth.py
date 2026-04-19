import jwt
from flask import current_app

from app.extensions import db
from app.models import AdminUser
from app.utils.jwt import create_access_token, decode_access_token, get_bearer_token
from app.utils.security import hash_password, verify_password


class AuthError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class AuthService:
    @staticmethod
    def serialize_user(user: AdminUser) -> dict:
        return {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
        }

    @staticmethod
    def register(data: dict) -> AdminUser:
        if not current_app.config["ALLOW_REGISTER"]:
            raise AuthError("当前环境不允许注册", 403)

        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        display_name = (data.get("display_name") or "").strip()

        if not username or not password or not display_name:
            raise AuthError("用户名、密码和展示名称不能为空", 400)

        if AdminUser.query.filter_by(username=username).first():
            raise AuthError("用户名已存在", 409)

        user = AdminUser(
            username=username,
            password_hash=hash_password(password),
            display_name=display_name,
            email=data.get("email"),
            phone=data.get("phone"),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def login(username: str, password: str) -> dict:
        username = (username or "").strip()
        if not username or not password:
            raise AuthError("用户名和密码不能为空", 400)

        user = AdminUser.query.filter_by(username=username).first()
        if not user or not verify_password(password, user.password_hash):
            raise AuthError("用户名或密码错误", 401)

        if not user.is_active:
            raise AuthError("账号已被禁用", 403)

        user.mark_logged_in()
        db.session.commit()

        return {
            "access_token": create_access_token(user.id),
            "token_type": "Bearer",
            "expires_in": current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
            "user": AuthService.serialize_user(user),
        }

    @staticmethod
    def get_current_user(authorization: str | None) -> AdminUser:
        token = get_bearer_token(authorization)
        if not token:
            raise AuthError("未登录或登录已失效", 401)

        try:
            payload = decode_access_token(token)
        except jwt.ExpiredSignatureError as exc:
            raise AuthError("登录已过期", 401) from exc
        except jwt.InvalidTokenError as exc:
            raise AuthError("无效的登录凭证", 401) from exc

        user = AdminUser.query.get(int(payload["sub"]))
        if not user or not user.is_active:
            raise AuthError("账号不存在或已被禁用", 401)

        return user

