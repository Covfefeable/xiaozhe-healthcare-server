from flask import Blueprint


api_bp = Blueprint("api", __name__, url_prefix="/api")


from . import auth, health, products  # noqa: E402,F401
