from datetime import datetime

from app.extensions import db
from app.models.base import BaseModel


class CartItem(BaseModel):
    __tablename__ = "miniapp_cart_items"

    user_id = db.Column(db.BigInteger, db.ForeignKey("miniapp_users.id"), nullable=False, index=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey("admin_products.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    product = db.relationship("Product", lazy="joined")

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()
