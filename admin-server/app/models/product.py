from datetime import datetime
from enum import Enum

from app.extensions import db
from app.models.base import BaseModel


class ProductStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"


class Product(BaseModel):
    __tablename__ = "admin_products"

    name = db.Column(db.String(100), nullable=False, index=True)
    price_cents = db.Column(db.Integer, nullable=False)
    validity_days = db.Column(db.Integer, nullable=False)
    detail_markdown = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.String(16),
        nullable=False,
        default=ProductStatus.DRAFT.value,
        index=True,
    )
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()
