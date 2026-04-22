from flask import Blueprint


api_bp = Blueprint("api", __name__, url_prefix="/api")


from . import agreements, auth, banners, dashboard, departments, doctors, health, news, orders, products, staff, uploads, users  # noqa: E402,F401
