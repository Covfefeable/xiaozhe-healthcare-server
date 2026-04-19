from app.controllers import banners

from . import api_bp


@api_bp.get("/banners")
def list_banners():
    return banners.list_banners()


@api_bp.post("/banners")
def create_banner():
    return banners.create_banner()


@api_bp.get("/banners/<int:banner_id>")
def get_banner(banner_id: int):
    return banners.get_banner(banner_id)


@api_bp.put("/banners/<int:banner_id>")
def update_banner(banner_id: int):
    return banners.update_banner(banner_id)


@api_bp.delete("/banners/<int:banner_id>")
def delete_banner(banner_id: int):
    return banners.delete_banner(banner_id)
