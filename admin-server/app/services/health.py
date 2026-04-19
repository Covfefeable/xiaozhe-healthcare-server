class HealthService:
    @staticmethod
    def get_status() -> dict:
        return {
            "service": "admin-server",
            "status": "ok",
        }

