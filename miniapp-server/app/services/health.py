class HealthService:
    @staticmethod
    def get_status() -> dict:
        return {
            "service": "miniapp-server",
            "status": "ok",
        }

