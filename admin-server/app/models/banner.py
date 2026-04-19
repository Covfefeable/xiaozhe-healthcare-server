from datetime import datetime

from app.extensions import db
from app.models.base import BaseModel


class Banner(BaseModel):
    __tablename__ = "admin_banners"

    image_url = db.Column(db.Text, nullable=True)
    title = db.Column(db.String(80), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False, default="")
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()
