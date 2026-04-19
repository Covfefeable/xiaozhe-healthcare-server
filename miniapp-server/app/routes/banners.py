from app.controllers import banners

from . import api_bp


@api_bp.get("/banners")
def list_banners():
    return banners.list_banners()
