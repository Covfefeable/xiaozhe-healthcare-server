from datetime import datetime

from app.extensions import db
from app.models.base import BaseModel


class News(BaseModel):
    __tablename__ = "admin_news"

    cover_image_object_key = db.Column(db.Text, nullable=True)
    title = db.Column(db.String(120), nullable=False, index=True)
    published_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    content_markdown = db.Column(db.Text, nullable=False, default="")
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()
