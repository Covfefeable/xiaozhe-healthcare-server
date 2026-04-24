import json
import time
import urllib.parse
import urllib.request
from datetime import datetime

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.extensions import db
from app.models import Assistant, Doctor, MiniappUser
from app.services.storage import StorageService
from app.utils.time import beijing_iso, beijing_strftime


class AuthError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class AuthService:
    @staticmethod
    def get_roles(user: MiniappUser) -> dict:
        roles = [{"key": "user", "label": "用户端"}]
        phone = (user.phone or "").strip()

        if phone:
            doctor = Doctor.query.filter(
                Doctor.phone == phone,
                Doctor.deleted_at.is_(None),
            ).first()
            if doctor:
                roles.append({"key": "doctor", "label": "医生端"})

            assistant = Assistant.query.filter(
                Assistant.phone == phone,
                Assistant.status == "active",
                Assistant.deleted_at.is_(None),
            ).first()
            if assistant:
                roles.append({"key": "assistant", "label": "助理端"})

        return {
            "default_role": "user",
            "roles": roles,
            "can_switch": len(roles) > 1,
        }

    @staticmethod
    def serialize_user(user: MiniappUser) -> dict:
        now = datetime.utcnow()
        is_member = bool(user.membership_expires_at and user.membership_expires_at > now)
        return {
            "id": str(user.id),
            "nickname": user.nickname or "",
            "avatar_object_key": user.avatar_object_key or "",
            "avatar_url": StorageService.sign_url(user.avatar_object_key),
            "phone": user.phone or "",
            "masked_phone": AuthService._mask_phone(user.phone),
            "gender": user.gender,
            "real_name": user.real_name or "",
            "status": user.status,
            "membership_status": "active" if is_member else "none",
            "membership_label": "会员用户" if is_member else "普通用户",
            "membership_expires_at": beijing_iso(user.membership_expires_at),
            "membership_expire_date": beijing_strftime(user.membership_expires_at, "%Y-%m-%d")
            if user.membership_expires_at
            else "",
            "health_manager_id": str(user.health_manager_id) if user.health_manager_id else "",
            "health_manager_name": user.health_manager.name if user.health_manager and user.health_manager.deleted_at is None else "",
        }

    @staticmethod
    def login_by_phone(data: dict) -> dict:
        phone = (data.get("phone") or "").strip()
        if not phone:
            raise AuthError("请输入手机号")
        if len(phone) > 20:
            raise AuthError("手机号格式不正确")
        user = AuthService._get_or_create_user(openid=f"phone:{phone}", phone=phone)
        return AuthService._login_result(user)

    @staticmethod
    def login_by_wechat(data: dict) -> dict:
        login_code = (data.get("login_code") or "").strip()
        phone_code = (data.get("phone_code") or "").strip()
        if not login_code:
            raise AuthError("缺少微信登录凭证")
        if not phone_code:
            raise AuthError("缺少手机号授权凭证")

        session = AuthService._code_to_session(login_code)
        phone = AuthService._phone_code_to_number(phone_code)
        user = AuthService._get_or_create_user(
            openid=session["openid"],
            phone=phone,
            unionid=session.get("unionid"),
        )
        return AuthService._login_result(user)

    @staticmethod
    def get_current_user(auth_header: str | None) -> MiniappUser:
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthError("请先登录", 401)
        token = auth_header.replace("Bearer ", "", 1).strip()
        serializer = AuthService._serializer()
        try:
            payload = serializer.loads(
                token,
                max_age=current_app.config["MINIAPP_TOKEN_EXPIRES"],
            )
        except SignatureExpired:
            raise AuthError("登录已过期，请重新登录", 401) from None
        except BadSignature:
            raise AuthError("登录凭证无效", 401) from None
        user = MiniappUser.query.filter(
            MiniappUser.id == payload.get("user_id"),
            MiniappUser.deleted_at.is_(None),
        ).first()
        if not user or user.status != "active":
            raise AuthError("用户不可用", 401)
        return user

    @staticmethod
    def update_profile(user: MiniappUser, data: dict) -> dict:
        avatar_object_key = data.get("avatar_object_key")
        nickname = data.get("nickname")
        if avatar_object_key is not None:
            user.avatar_object_key = str(avatar_object_key).strip()
        if nickname is not None:
            user.nickname = str(nickname).strip()[:50]
        db.session.commit()
        return AuthService.serialize_user(user)

    @staticmethod
    def _login_result(user: MiniappUser) -> dict:
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        return {
            "token": AuthService._create_token(user),
            "user": AuthService.serialize_user(user),
        }

    @staticmethod
    def _get_or_create_user(openid: str, phone: str | None = None, unionid: str | None = None) -> MiniappUser:
        user = MiniappUser.query.filter(MiniappUser.openid == openid).first()
        if not user:
            user = MiniappUser(openid=openid, phone=phone, unionid=unionid)
            db.session.add(user)
        else:
            if phone:
                user.phone = phone
            if unionid:
                user.unionid = unionid
        db.session.commit()
        return user

    @staticmethod
    def _create_token(user: MiniappUser) -> str:
        return AuthService._serializer().dumps({"user_id": user.id})

    @staticmethod
    def _serializer() -> URLSafeTimedSerializer:
        return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="miniapp-auth")

    @staticmethod
    def _mask_phone(phone: str | None) -> str:
        if not phone or len(phone) < 7:
            return phone or ""
        return f"{phone[:3]}****{phone[-4:]}"

    @staticmethod
    def _code_to_session(code: str) -> dict:
        app_id = current_app.config["WECHAT_APP_ID"]
        app_secret = current_app.config["WECHAT_APP_SECRET"]
        if not app_id or not app_secret:
            return {"openid": f"dev:{code}", "unionid": None}
        params = urllib.parse.urlencode(
            {
                "appid": app_id,
                "secret": app_secret,
                "js_code": code,
                "grant_type": "authorization_code",
            }
        )
        payload = AuthService._request_json(
            f"https://api.weixin.qq.com/sns/jscode2session?{params}",
        )
        if payload.get("errcode"):
            raise AuthError(payload.get("errmsg") or "微信登录失败")
        if not payload.get("openid"):
            raise AuthError("微信登录未返回 openid")
        return payload

    @staticmethod
    def _phone_code_to_number(code: str) -> str:
        app_id = current_app.config["WECHAT_APP_ID"]
        app_secret = current_app.config["WECHAT_APP_SECRET"]
        if not app_id or not app_secret:
            return "13800000000"
        access_token = AuthService._get_access_token(app_id, app_secret)
        payload = AuthService._request_json(
            f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}",
            data={"code": code},
        )
        if payload.get("errcode"):
            raise AuthError(payload.get("errmsg") or "获取手机号失败")
        phone_info = payload.get("phone_info") or {}
        phone = phone_info.get("phoneNumber")
        if not phone:
            raise AuthError("微信未返回手机号")
        return phone

    @staticmethod
    def _get_access_token(app_id: str, app_secret: str) -> str:
        cache_key = "wechat:access_token"
        redis_client = current_app.extensions["redis"]
        cached = redis_client.get(cache_key)
        if cached:
            return cached.decode("utf-8")
        params = urllib.parse.urlencode(
            {
                "grant_type": "client_credential",
                "appid": app_id,
                "secret": app_secret,
            }
        )
        payload = AuthService._request_json(
            f"https://api.weixin.qq.com/cgi-bin/token?{params}",
        )
        if payload.get("errcode"):
            raise AuthError(payload.get("errmsg") or "获取微信 access_token 失败")
        access_token = payload.get("access_token")
        if not access_token:
            raise AuthError("微信未返回 access_token")
        expires_in = int(payload.get("expires_in") or 7200)
        redis_client.setex(cache_key, max(expires_in - 300, 60), access_token)
        return access_token

    @staticmethod
    def _request_json(url: str, data: dict | None = None) -> dict:
        body = json.dumps(data).encode("utf-8") if data is not None else None
        request = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST" if data is not None else "GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=current_app.config["WECHAT_API_TIMEOUT"]) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise AuthError(f"微信接口请求失败：{exc}") from None
