from app.extensions import db
from app.models.base import BaseModel


class CustomerService(BaseModel):
    __tablename__ = "admin_customer_services"

    avatar_url = db.Column(db.Text, nullable=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    remark = db.Column(db.String(255), nullable=False, default="")
    deleted_at = db.Column(db.DateTime, nullable=True)


class Assistant(BaseModel):
    __tablename__ = "admin_assistants"

    avatar_url = db.Column(db.Text, nullable=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    assistant_type = db.Column(db.String(30), nullable=False, default="health_manager")
    remark = db.Column(db.String(255), nullable=False, default="")
    deleted_at = db.Column(db.DateTime, nullable=True)
