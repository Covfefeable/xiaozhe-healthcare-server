from app.controllers import assistants

from . import api_bp


@api_bp.get("/assistants/me")
def get_current_assistant():
    return assistants.get_current_assistant()
