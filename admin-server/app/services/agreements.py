from app.extensions import db
from app.models import Agreement, AgreementType
from app.utils.time import beijing_iso


DEFAULT_AGREEMENTS = {
    AgreementType.USER_AGREEMENT.value: {
        "title": "用户协议",
        "content_markdown": "# 用户协议\n\n请在后台维护正式的用户协议内容。",
    },
    AgreementType.PRIVACY_POLICY.value: {
        "title": "隐私政策",
        "content_markdown": "# 隐私政策\n\n请在后台维护正式的隐私政策内容。",
    },
}


class AgreementError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class AgreementService:
    @staticmethod
    def serialize(agreement: Agreement) -> dict:
        return {
            "id": agreement.id,
            "agreement_type": agreement.agreement_type,
            "title": agreement.title,
            "content_markdown": agreement.content_markdown or "",
            "created_at": beijing_iso(agreement.created_at),
            "updated_at": beijing_iso(agreement.updated_at),
        }

    @staticmethod
    def list_agreements() -> list[dict]:
        AgreementService.ensure_defaults()
        order = {
            AgreementType.USER_AGREEMENT.value: 1,
            AgreementType.PRIVACY_POLICY.value: 2,
        }
        items = Agreement.query.order_by(Agreement.agreement_type.asc()).all()
        items.sort(key=lambda item: order.get(item.agreement_type, 99))
        return [AgreementService.serialize(item) for item in items]

    @staticmethod
    def get_agreement(agreement_type: str) -> Agreement:
        agreement_type = AgreementService._parse_type(agreement_type)
        AgreementService.ensure_defaults()
        agreement = Agreement.query.filter(Agreement.agreement_type == agreement_type).first()
        if not agreement:
            raise AgreementError("协议不存在", 404)
        return agreement

    @staticmethod
    def update_agreement(agreement_type: str, data: dict) -> Agreement:
        agreement = AgreementService.get_agreement(agreement_type)
        title = (data.get("title") or "").strip()
        if not title:
            raise AgreementError("协议标题不能为空")
        if len(title) > 80:
            raise AgreementError("协议标题不能超过 80 个字符")

        agreement.title = title
        agreement.content_markdown = data.get("content_markdown") or ""
        db.session.commit()
        return agreement

    @staticmethod
    def ensure_defaults() -> None:
        changed = False
        for agreement_type, payload in DEFAULT_AGREEMENTS.items():
            exists = Agreement.query.filter(Agreement.agreement_type == agreement_type).first()
            if exists:
                continue
            db.session.add(Agreement(agreement_type=agreement_type, **payload))
            changed = True
        if changed:
            db.session.commit()

    @staticmethod
    def _parse_type(value: str) -> str:
        if value in {"user", AgreementType.USER_AGREEMENT.value}:
            return AgreementType.USER_AGREEMENT.value
        if value in {"privacy", AgreementType.PRIVACY_POLICY.value}:
            return AgreementType.PRIVACY_POLICY.value
        raise AgreementError("协议类型不正确", 404)
