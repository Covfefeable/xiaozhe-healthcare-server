from app.models import Agreement
from app.utils.time import beijing_iso


DEFAULT_AGREEMENTS = {
    "user": {
        "agreement_type": "user_agreement",
        "nav_title": "用户协议",
        "title": "用户协议",
        "content": "# 用户协议\n\n请在后台维护正式的用户协议内容。",
    },
    "privacy": {
        "agreement_type": "privacy_policy",
        "nav_title": "隐私政策",
        "title": "隐私政策",
        "content": "# 隐私政策\n\n请在后台维护正式的隐私政策内容。",
    },
}


class AgreementService:
    @staticmethod
    def get_agreement(raw_type: str | None) -> dict:
        key = "privacy" if raw_type in {"privacy", "privacy_policy"} else "user"
        default = DEFAULT_AGREEMENTS[key]
        agreement = Agreement.query.filter(
            Agreement.agreement_type == default["agreement_type"],
        ).first()
        if not agreement:
            return {
                "navTitle": default["nav_title"],
                "title": default["title"],
                "updatedAt": "",
                "content": default["content"],
            }
        return {
            "navTitle": agreement.title,
            "title": agreement.title,
            "updatedAt": beijing_iso(agreement.updated_at) or "",
            "content": agreement.content_markdown or "",
        }
