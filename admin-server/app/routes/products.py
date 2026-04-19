from app.controllers import products

from . import api_bp


@api_bp.get("/products")
def list_products():
    return products.list_products()


@api_bp.post("/products")
def create_product():
    return products.create_product()


@api_bp.get("/products/<int:product_id>")
def get_product(product_id: int):
    return products.get_product(product_id)


@api_bp.put("/products/<int:product_id>")
def update_product(product_id: int):
    return products.update_product(product_id)


@api_bp.delete("/products/<int:product_id>")
def delete_product(product_id: int):
    return products.delete_product(product_id)


@api_bp.post("/products/<int:product_id>/publish")
def publish_product(product_id: int):
    return products.publish_product(product_id)


@api_bp.post("/products/<int:product_id>/unpublish")
def unpublish_product(product_id: int):
    return products.unpublish_product(product_id)
