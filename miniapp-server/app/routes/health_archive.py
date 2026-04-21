from app.controllers import health_archive

from . import api_bp


@api_bp.get("/health-archive")
def get_my_archive():
    return health_archive.get_my_archive()


@api_bp.put("/health-archive")
def update_my_archive():
    return health_archive.update_my_archive()


@api_bp.get("/chat/conversations/<int:conversation_id>/user-archive")
def get_conversation_user_archive(conversation_id: int):
    return health_archive.get_conversation_user_archive(conversation_id)


@api_bp.get("/chat/conversations/<int:conversation_id>/members/<member_type>/<int:member_id>/profile")
def get_conversation_member_profile(conversation_id: int, member_type: str, member_id: int):
    return health_archive.get_conversation_member_profile(conversation_id, member_type, member_id)
