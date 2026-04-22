from flask import Blueprint


api_bp = Blueprint("api", __name__, url_prefix="/api")


from . import agreements, assistants, auth, banners, cart, chat, departments, doctors, health, health_archive, news, orders, products, uploads  # noqa: E402,F401
