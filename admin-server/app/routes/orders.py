from app.controllers import orders

from . import api_bp


@api_bp.get("/orders")
def list_orders():
    return orders.list_orders()


@api_bp.get("/orders/<int:order_id>")
def get_order(order_id: int):
    return orders.get_order(order_id)


@api_bp.put("/orders/<int:order_id>/status")
def update_order_status(order_id: int):
    return orders.update_status(order_id)
