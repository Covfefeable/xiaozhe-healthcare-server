from app.services.agreements import AgreementService
from app.utils.response import success_response


def get_agreement(agreement_type: str):
    return success_response(data=AgreementService.get_agreement(agreement_type))
