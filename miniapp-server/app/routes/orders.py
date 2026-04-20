from app.controllers import orders

from . import api_bp


@api_bp.post("/orders")
def create_order():
    return orders.create_order()


@api_bp.post("/orders/direct")
def create_direct_order():
    return orders.create_direct_order()


@api_bp.get("/orders")
def list_orders():
    return orders.list_orders()


@api_bp.get("/orders/<int:order_id>")
def get_order(order_id: int):
    return orders.get_order(order_id)


@api_bp.post("/orders/<int:order_id>/pay")
def pay_order(order_id: int):
    return orders.pay_order(order_id)
