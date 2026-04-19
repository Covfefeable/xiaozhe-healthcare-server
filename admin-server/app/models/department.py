from datetime import datetime

from app.extensions import db
from app.models.base import BaseModel


class Department(BaseModel):
    __tablename__ = "admin_departments"

    name = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False, default="")
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()
