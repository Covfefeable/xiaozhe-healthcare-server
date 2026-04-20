from flask import Blueprint


api_bp = Blueprint("api", __name__, url_prefix="/api")


from . import assistants, auth, banners, cart, chat, departments, doctors, health, news, orders, products  # noqa: E402,F401
