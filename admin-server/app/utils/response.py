from flask import jsonify


def success_response(data=None, message: str = "操作成功", code: int = 200):
    return jsonify(
        {
            "code": code,
            "message": message,
            "data": data,
        }
    ), code


def error_response(message: str = "操作失败", code: int = 400, data=None):
    return jsonify(
        {
            "code": code,
            "message": message,
            "data": data,
        }
    ), code

