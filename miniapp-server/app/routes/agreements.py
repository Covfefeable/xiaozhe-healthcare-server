from app.controllers import agreements

from . import api_bp


@api_bp.get("/agreements/<agreement_type>")
def get_agreement(agreement_type: str):
    return agreements.get_agreement(agreement_type)
