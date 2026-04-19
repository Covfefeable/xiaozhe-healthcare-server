from app.controllers import products

from . import api_bp


@api_bp.get("/products")
def list_products():
    return products.list_products()


@api_bp.get("/products/<int:product_id>")
def get_product(product_id: int):
    return products.get_product(product_id)
