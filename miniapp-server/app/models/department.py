from app.extensions import db
from app.models.base import BaseModel


class Department(BaseModel):
    __tablename__ = "admin_departments"

    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    deleted_at = db.Column(db.DateTime, nullable=True)
