from app.controllers import cart

from . import api_bp


@api_bp.get("/cart/items")
def list_cart_items():
    return cart.list_items()


@api_bp.post("/cart/items")
def add_cart_item():
    return cart.add_item()


@api_bp.put("/cart/items/<int:item_id>")
def update_cart_item(item_id: int):
    return cart.update_item(item_id)


@api_bp.delete("/cart/items/<int:item_id>")
def delete_cart_item(item_id: int):
    return cart.delete_item(item_id)
