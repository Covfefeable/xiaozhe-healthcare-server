from app.extensions import db
from app.models.base import BaseModel


class Product(BaseModel):
    __tablename__ = "admin_products"

    name = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.String(20), nullable=False, default="")
    price_cents = db.Column(db.Integer, nullable=False)
    validity_days = db.Column(db.Integer, nullable=False)
    product_type = db.Column(db.String(20), nullable=False, default="other")
    image_url = db.Column(db.Text, nullable=True)
    detail_markdown = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(16), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    deleted_at = db.Column(db.DateTime, nullable=True)
