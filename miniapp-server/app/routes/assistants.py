from app.controllers import assistants

from . import api_bp


@api_bp.get("/assistants")
def list_assistants():
    return assistants.list_assistants()


@api_bp.get("/assistants/me")
def get_current_assistant():
    return assistants.get_current_assistant()
