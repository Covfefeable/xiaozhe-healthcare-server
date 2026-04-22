from app.extensions import db
from app.models.base import BaseModel


class Order(BaseModel):
    __tablename__ = "miniapp_orders"

    order_no = db.Column(db.String(32), nullable=False, unique=True, index=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("miniapp_users.id"), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="pending_payment", index=True)
    product_type = db.Column(db.String(20), nullable=False, default="other", index=True)
    total_amount_cents = db.Column(db.Integer, nullable=False, default=0)
    paid_amount_cents = db.Column(db.Integer, nullable=False, default=0)
    payment_method = db.Column(db.String(30), nullable=False, default="")
    service_user_name = db.Column(db.String(50), nullable=False, default="")
    paid_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    refunded_at = db.Column(db.DateTime, nullable=True)
    refund_reason = db.Column(db.String(100), nullable=False, default="")
    refund_description = db.Column(db.Text, nullable=False, default="")
    refund_image_object_keys = db.Column(db.JSON, nullable=False, default=list)
    refund_requested_at = db.Column(db.DateTime, nullable=True)
    refund_handled_at = db.Column(db.DateTime, nullable=True)
    refund_reject_reason = db.Column(db.String(255), nullable=False, default="")
    remark = db.Column(db.String(255), nullable=False, default="")
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    user = db.relationship("MiniappUser", lazy="joined")
    items = db.relationship("OrderItem", lazy="selectin")


class OrderItem(BaseModel):
    __tablename__ = "miniapp_order_items"

    order_id = db.Column(db.BigInteger, db.ForeignKey("miniapp_orders.id"), nullable=False, index=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey("admin_products.id"), nullable=True, index=True)
    product_name_snapshot = db.Column(db.String(100), nullable=False)
    product_type_snapshot = db.Column(db.String(20), nullable=False)
    product_summary_snapshot = db.Column(db.String(120), nullable=False, default="")
    price_cents_snapshot = db.Column(db.Integer, nullable=False)
    validity_days_snapshot = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal_cents = db.Column(db.Integer, nullable=False)
    image_object_key_snapshot = db.Column(db.Text, nullable=True)

    product = db.relationship("Product", lazy="joined")
