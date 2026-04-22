from app.extensions import db
from app.models.base import BaseModel


class Banner(BaseModel):
    __tablename__ = "admin_banners"

    image_object_key = db.Column(db.Text, nullable=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")
    deleted_at = db.Column(db.DateTime, nullable=True)
