from app.services.products import ProductError, ProductService
from app.utils.response import error_response, success_response


def list_products():
    return success_response(data={"items": ProductService.list_products()})


def get_product(product_id: int):
    try:
        product = ProductService.get_product(product_id)
    except ProductError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=product)
