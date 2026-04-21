from datetime import datetime

from app.extensions import db
from app.models.base import BaseModel


class StaffMixin:
    avatar_url = db.Column(db.Text, nullable=True)
    name = db.Column(db.String(50), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="active", index=True)
    remark = db.Column(db.String(255), nullable=False, default="")
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()


class Assistant(StaffMixin, BaseModel):
    __tablename__ = "admin_assistants"

    assistant_type = db.Column(db.String(30), nullable=False, default="health_manager", index=True)


class CustomerService(StaffMixin, BaseModel):
    __tablename__ = "admin_customer_services"
