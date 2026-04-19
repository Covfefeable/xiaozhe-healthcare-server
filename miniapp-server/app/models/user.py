from app.extensions import db
from app.models.base import BaseModel


class MiniappUser(BaseModel):
    __tablename__ = "miniapp_users"

    openid = db.Column(db.String(64), nullable=False, unique=True, index=True)
    unionid = db.Column(db.String(64), nullable=True, index=True)
    nickname = db.Column(db.String(50), nullable=False, default="")
    avatar_url = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True, index=True)
    gender = db.Column(db.String(10), nullable=False, default="unknown")
    birthday = db.Column(db.Date, nullable=True)
    real_name = db.Column(db.String(50), nullable=False, default="")
    status = db.Column(db.String(20), nullable=False, default="active", index=True)
    membership_status = db.Column(db.String(20), nullable=False, default="none")
    membership_expires_at = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)


class MiniappUserMembership(BaseModel):
    __tablename__ = "miniapp_user_memberships"

    user_id = db.Column(db.BigInteger, db.ForeignKey("miniapp_users.id"), nullable=False, index=True)
    product_id = db.Column(db.BigInteger, nullable=True, index=True)
    level = db.Column(db.String(30), nullable=False, default="standard")
    status = db.Column(db.String(20), nullable=False, default="active", index=True)
    starts_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    source_type = db.Column(db.String(30), nullable=False, default="manual_grant")
    source_id = db.Column(db.BigInteger, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    user = db.relationship("MiniappUser", lazy="joined")
