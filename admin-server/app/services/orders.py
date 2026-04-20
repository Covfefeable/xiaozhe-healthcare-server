from datetime import datetime
from decimal import Decimal

from app.extensions import db
from app.models import MiniappUser, Order


class OrderError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


ORDER_STATUS = {"pending_payment", "in_progress", "completed", "refunded"}
ORDER_STATUS_LABEL = {
    "pending_payment": "待支付",
    "in_progress": "进行中",
    "completed": "已完成",
    "refunded": "已退款",
}


def _format_price(price_cents: int) -> str:
    return f"{Decimal(price_cents) / Decimal(100):.2f}"


class OrderService:
    @staticmethod
    def serialize(order: Order) -> dict:
        items = [
            {
                "id": item.id,
                "product_name": item.product_name_snapshot,
                "product_type": item.product_type_snapshot,
                "quantity": item.quantity,
                "subtotal_cents": item.subtotal_cents,
                "subtotal": _format_price(item.subtotal_cents),
            }
            for item in order.items
        ]
        return {
            "id": order.id,
            "order_no": order.order_no,
            "user_phone": order.user.phone if order.user else "",
            "service_user_name": order.service_user_name,
            "status": order.status,
            "status_label": ORDER_STATUS_LABEL.get(order.status, order.status),
            "product_type": order.product_type,
            "product_summary": "、".join(item["product_name"] for item in items),
            "total_amount_cents": order.total_amount_cents,
            "total_amount": _format_price(order.total_amount_cents),
            "paid_amount_cents": order.paid_amount_cents,
            "payment_method": order.payment_method,
            "paid_at": order.paid_at.isoformat() if order.paid_at else None,
            "completed_at": order.completed_at.isoformat() if order.completed_at else None,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            "items": items,
        }

    @staticmethod
    def list_orders(args) -> dict:
        page = OrderService._positive_int(args.get("page"), default=1)
        page_size = OrderService._positive_int(args.get("page_size"), default=20, maximum=100)
        keyword = (args.get("keyword") or "").strip()
        status = (args.get("status") or "").strip()
        query = Order.query.outerjoin(MiniappUser).filter(Order.deleted_at.is_(None))
        if keyword:
            query = query.filter(
                db.or_(
                    Order.order_no.ilike(f"%{keyword}%"),
                    MiniappUser.phone.ilike(f"%{keyword}%"),
                    Order.service_user_name.ilike(f"%{keyword}%"),
                )
            )
        if status:
            if status not in ORDER_STATUS:
                raise OrderError("订单状态不正确")
            query = query.filter(Order.status == status)
        total = query.count()
        orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return {
            "items": [OrderService.serialize(order) for order in orders],
            "pagination": {"page": page, "page_size": page_size, "total": total},
        }

    @staticmethod
    def get_order(order_id: int) -> Order:
        order = Order.query.filter(Order.id == order_id, Order.deleted_at.is_(None)).first()
        if not order:
            raise OrderError("订单不存在", 404)
        return order

    @staticmethod
    def update_status(order_id: int, status: str) -> Order:
        if status not in {"completed", "refunded"}:
            raise OrderError("当前仅支持更新为已完成或已退款")
        order = OrderService.get_order(order_id)
        if order.product_type == "membership" and status == "completed":
            raise OrderError("会员订单无需后台手动完成")
        if order.status != "in_progress":
            raise OrderError("只有进行中的订单可以更新状态")
        order.status = status
        now = datetime.utcnow()
        if status == "completed":
            order.completed_at = now
        if status == "refunded":
            order.refunded_at = now
        db.session.commit()
        return order

    @staticmethod
    def _positive_int(value, default: int, maximum: int | None = None) -> int:
        try:
            number = int(value)
        except (TypeError, ValueError):
            number = default
        if number < 1:
            number = default
        if maximum is not None:
            number = min(number, maximum)
        return number
