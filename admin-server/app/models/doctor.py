from datetime import datetime

from app.extensions import db
from app.models.base import BaseModel


class Doctor(BaseModel):
    __tablename__ = "admin_doctors"

    department_id = db.Column(
        db.BigInteger,
        db.ForeignKey("admin_departments.id"),
        nullable=False,
        index=True,
    )
    avatar_url = db.Column(db.Text, nullable=True)
    name = db.Column(db.String(50), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(50), nullable=False, default="")
    hospital = db.Column(db.String(100), nullable=False, default="")
    summary = db.Column(db.String(120), nullable=False, default="")
    specialty_tags = db.Column(db.JSON, nullable=False, default=list)
    introduction = db.Column(db.Text, nullable=False, default="")
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    department = db.relationship("Department", lazy="joined")

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()
