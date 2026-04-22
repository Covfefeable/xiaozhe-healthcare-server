from app.extensions import db
from app.models.base import BaseModel


class MiniappUser(BaseModel):
    __tablename__ = "miniapp_users"

    openid = db.Column(db.String(64), nullable=False)
    unionid = db.Column(db.String(64), nullable=True)
    nickname = db.Column(db.String(50), nullable=False, default="")
    avatar_object_key = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(10), nullable=False, default="unknown")
    birthday = db.Column(db.Date, nullable=True)
    real_name = db.Column(db.String(50), nullable=False, default="")
    status = db.Column(db.String(20), nullable=False, default="active")
    membership_status = db.Column(db.String(20), nullable=False, default="none")
    membership_expires_at = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)


class Order(BaseModel):
    __tablename__ = "miniapp_orders"

    order_no = db.Column(db.String(32), nullable=False, unique=True, index=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("miniapp_users.id"), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, index=True)
    product_type = db.Column(db.String(20), nullable=False, index=True)
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


class MiniappHealthRecord(BaseModel):
    __tablename__ = "miniapp_health_records"

    user_id = db.Column(db.BigInteger, db.ForeignKey("miniapp_users.id"), nullable=False, index=True)
    record_type = db.Column(db.String(30), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False, default="")
    image_object_keys = db.Column(db.JSON, nullable=False, default=list)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    user = db.relationship("MiniappUser", lazy="joined")
