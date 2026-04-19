from app.extensions import db
from app.models.base import BaseModel


class News(BaseModel):
    __tablename__ = "admin_news"

    cover_image_url = db.Column(db.Text, nullable=True)
    title = db.Column(db.String(120), nullable=False)
    published_at = db.Column(db.DateTime, nullable=False)
    content_markdown = db.Column(db.Text, nullable=False, default="")
    deleted_at = db.Column(db.DateTime, nullable=True)
