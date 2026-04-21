from app.controllers import agreements

from . import api_bp


@api_bp.get("/agreements")
def list_agreements():
    return agreements.list_agreements()


@api_bp.get("/agreements/<agreement_type>")
def get_agreement(agreement_type: str):
    return agreements.get_agreement(agreement_type)


@api_bp.put("/agreements/<agreement_type>")
def update_agreement(agreement_type: str):
    return agreements.update_agreement(agreement_type)
