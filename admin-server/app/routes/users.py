from app.controllers import users

from . import api_bp


@api_bp.get("/users")
def list_users():
    return users.list_users()


@api_bp.get("/users/<int:user_id>")
def get_user(user_id: int):
    return users.get_user(user_id)


@api_bp.put("/users/<int:user_id>/membership")
def renew_membership(user_id: int):
    return users.renew_membership(user_id)


@api_bp.put("/users/<int:user_id>/health-manager")
def assign_health_manager(user_id: int):
    return users.assign_health_manager(user_id)
