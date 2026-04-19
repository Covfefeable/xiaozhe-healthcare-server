from app.services.health import HealthService
from app.utils.response import success_response


def get_health():
    return success_response(data=HealthService.get_status())

