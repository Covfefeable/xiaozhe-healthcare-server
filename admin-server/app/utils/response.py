from flask import jsonify


def success_response(
    data=None,
    message: str = "success",
    code: int = 0,
    status_code: int = 200,
):
    return jsonify(
        {
            "code": code,
            "message": message,
            "data": data,
        }
    ), status_code


def error_response(message: str = "error", code: int = 400, data=None, status_code=None):
    return jsonify(
        {
            "code": code,
            "message": message,
            "data": data,
        }
    ), status_code or code
