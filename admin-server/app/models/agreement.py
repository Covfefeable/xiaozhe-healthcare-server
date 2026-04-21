from enum import Enum

from app.extensions import db
from app.models.base import BaseModel


class AgreementType(str, Enum):
    USER_AGREEMENT = "user_agreement"
    PRIVACY_POLICY = "privacy_policy"


class Agreement(BaseModel):
    __tablename__ = "admin_agreements"

    agreement_type = db.Column(db.String(30), nullable=False, unique=True, index=True)
    title = db.Column(db.String(80), nullable=False)
    content_markdown = db.Column(db.Text, nullable=False, default="")
