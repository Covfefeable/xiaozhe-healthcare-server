from datetime import datetime

from app.extensions import db
from app.models.base import BaseModel


class AdminUser(BaseModel):
    __tablename__ = "admin_users"

    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), nullable=True)
    phone = db.Column(db.String(32), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime, nullable=True)

    def mark_logged_in(self) -> None:
        self.last_login_at = datetime.utcnow()

