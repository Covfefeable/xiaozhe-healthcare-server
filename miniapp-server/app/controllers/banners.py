from app.services.banners import BannerService
from app.utils.response import success_response


def list_banners():
    return success_response(data={"items": BannerService.list_banners()})
