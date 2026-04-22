from app.controllers import uploads

from . import api_bp


@api_bp.post("/uploads")
def upload_file():
    return uploads.upload_file()
