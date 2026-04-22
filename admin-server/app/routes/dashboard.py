from app.controllers import dashboard

from . import api_bp


@api_bp.get("/dashboard")
def get_dashboard():
    return dashboard.get_dashboard()
