from flask import Blueprint


api_bp = Blueprint("api", __name__, url_prefix="/api")


from . import agreements, auth, banners, departments, doctors, health, news, orders, products, staff, users  # noqa: E402,F401
