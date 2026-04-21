from flask import request

from app.services.agreements import AgreementError, AgreementService
from app.services.auth import AuthError, AuthService
from app.utils.response import error_response, success_response


def _require_auth():
    try:
        AuthService.get_current_user(request.headers.get("Authorization"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return None


def list_agreements():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        data = {"items": AgreementService.list_agreements()}
    except AgreementError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def get_agreement(agreement_type: str):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        agreement = AgreementService.get_agreement(agreement_type)
    except AgreementError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=AgreementService.serialize(agreement))


def update_agreement(agreement_type: str):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        agreement = AgreementService.update_agreement(
            agreement_type,
            request.get_json(silent=True) or {},
        )
    except AgreementError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=AgreementService.serialize(agreement), message="保存成功")
