from datetime import datetime, timedelta
from decimal import Decimal
from random import randint

from app.extensions import db
from app.models import CartItem, MiniappUser, MiniappUserMembership, Order, OrderItem, Product


class OrderError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


ORDER_STATUS = {"pending_payment", "in_progress", "completed", "refunded"}
ORDER_STATUS_LABEL = {
    "pending_payment": "待支付",
    "in_progress": "服务进行中",
    "completed": "已完成",
    "refunded": "已退款",
}


def _format_price(price_cents: int) -> str:
    return f"¥{Decimal(price_cents) / Decimal(100):.2f}"


def _format_time(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else ""


class OrderService:
    @staticmethod
    def create_from_cart(user: MiniappUser, data: dict) -> dict:
        item_ids = data.get("cart_item_ids") or []
        query = CartItem.query.join(Product).filter(
            CartItem.user_id == user.id,
            CartItem.deleted_at.is_(None),
            Product.status == "active",
            Product.deleted_at.is_(None),
        )
        if item_ids:
            try:
                ids = [int(item_id) for item_id in item_ids]
            except (TypeError, ValueError):
                raise OrderError("购物车参数不正确") from None
            query = query.filter(CartItem.id.in_(ids))
        cart_items = query.order_by(CartItem.created_at.asc()).all()
        if not cart_items:
            raise OrderError("购物车为空")

        remark = (data.get("remark") or "").strip()
        order = OrderService._create_order(
            user,
            [(cart_item.product, cart_item.quantity) for cart_item in cart_items],
            remark,
        )
        for cart_item in cart_items:
            cart_item.soft_delete()
        db.session.commit()
        return OrderService.serialize(order)

    @staticmethod
    def create_direct(user: MiniappUser, data: dict) -> dict:
        product = OrderService._get_active_product(data.get("product_id"))
        quantity = OrderService._positive_int(data.get("quantity"), default=1, maximum=99)
        remark = (data.get("remark") or "").strip()
        order = OrderService._create_order(user, [(product, quantity)], remark)
        db.session.commit()
        return OrderService.serialize(order)

    @staticmethod
    def list_orders(user: MiniappUser, args) -> list[dict]:
        status = (args.get("status") or "").strip()
        query = Order.query.filter(Order.user_id == user.id, Order.deleted_at.is_(None))
        if status and status != "all":
            if status not in ORDER_STATUS:
                raise OrderError("订单状态不正确")
            query = query.filter(Order.status == status)
        orders = query.order_by(Order.created_at.desc()).all()
        return [OrderService.serialize(order, brief=True) for order in orders]

    @staticmethod
    def get_order(user: MiniappUser, order_id: int) -> dict:
        order = Order.query.filter(
            Order.id == order_id,
            Order.user_id == user.id,
            Order.deleted_at.is_(None),
        ).first()
        if not order:
            raise OrderError("订单不存在", 404)
        return OrderService.serialize(order)

    @staticmethod
    def pay_order(user: MiniappUser, order_id: int) -> dict:
        order = Order.query.filter(
            Order.id == order_id,
            Order.user_id == user.id,
            Order.deleted_at.is_(None),
        ).first()
        if not order:
            raise OrderError("订单不存在", 404)
        if order.status != "pending_payment":
            return OrderService.serialize(order)
        now = datetime.utcnow()
        order.paid_amount_cents = order.total_amount_cents
        order.payment_method = "wechat"
        order.paid_at = now
        has_membership_items = OrderService._has_membership_items(order)
        all_membership_items = OrderService._all_membership_items(order)
        if has_membership_items:
            OrderService._recharge_membership(user, order, now)
        if all_membership_items:
            order.status = "completed"
            order.completed_at = now
        else:
            order.status = "in_progress"
        db.session.commit()
        return OrderService.serialize(order)

    @staticmethod
    def cancel_order(user: MiniappUser, order_id: int) -> None:
        order = Order.query.filter(
            Order.id == order_id,
            Order.user_id == user.id,
            Order.deleted_at.is_(None),
        ).first()
        if not order:
            raise OrderError("订单不存在", 404)
        if order.status != "pending_payment":
            raise OrderError("只有待支付订单可以取消")
        order.deleted_at = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def serialize(order: Order, brief: bool = False) -> dict:
        items = [OrderService.serialize_item(item) for item in order.items]
        first_item = items[0] if items else {}
        quantity = sum(item["quantity"] for item in items)
        data = {
            "id": str(order.id),
            "order_no": order.order_no,
            "orderNo": order.order_no,
            "status": order.status,
            "statusLabel": ORDER_STATUS_LABEL.get(order.status, order.status),
            "product_type": order.product_type,
            "title": OrderService._order_title(items),
            "desc": OrderService._status_desc(order),
            "image": first_item.get("image", ""),
            "quantity": quantity,
            "total_amount_cents": order.total_amount_cents,
            "displayPrice": _format_price(order.total_amount_cents),
            "payMethod": "微信支付" if order.payment_method == "wechat" else "未支付",
            "patientName": order.service_user_name or "本人",
            "time": _format_time(order.created_at),
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "paid_at": order.paid_at.isoformat() if order.paid_at else None,
            "completed_at": order.completed_at.isoformat() if order.completed_at else None,
            "items": items,
            "progress": OrderService._progress(order),
        }
        if brief:
            data.pop("items", None)
            data.pop("progress", None)
        return data

    @staticmethod
    def serialize_item(item: OrderItem) -> dict:
        return {
            "id": str(item.id),
            "product_id": str(item.product_id) if item.product_id else "",
            "title": item.product_name_snapshot,
            "desc": item.product_summary_snapshot,
            "product_type": item.product_type_snapshot,
            "price_cents": item.price_cents_snapshot,
            "price": _format_price(item.price_cents_snapshot),
            "validity_days": item.validity_days_snapshot,
            "quantity": item.quantity,
            "subtotal_cents": item.subtotal_cents,
            "subtotal": _format_price(item.subtotal_cents),
            "image": item.image_url_snapshot or "",
        }

    @staticmethod
    def _progress(order: Order) -> list[dict]:
        paid_done = order.status in {"in_progress", "completed", "refunded"}
        completed_done = order.status in {"completed", "refunded"}
        events = [
            {
                "title": "订单已创建",
                "time": _format_time(order.created_at),
                "done": True,
                "active": order.status == "pending_payment",
            },
            {
                "title": "订单支付完成" if paid_done else "等待支付",
                "time": _format_time(order.paid_at),
                "done": paid_done,
                "active": order.status == "in_progress",
            },
        ]
        if OrderService._has_membership_items(order) and paid_done:
            events.insert(
                2,
                {
                    "title": "会员权益已开通",
                    "time": _format_time(order.paid_at),
                    "done": True,
                    "active": order.status == "in_progress",
                },
            )
        if order.status in {"completed", "refunded"}:
            events.append(
                {
                    "title": "服务已完成" if order.status == "completed" else "订单已退款",
                    "time": _format_time(order.completed_at or order.refunded_at),
                    "done": completed_done,
                    "active": True,
                }
            )
        return events

    @staticmethod
    def _status_desc(order: Order) -> str:
        if order.status == "pending_payment":
            return "请完成支付，支付后服务将开始处理。"
        if order.status == "in_progress":
            if OrderService._has_membership_items(order):
                return "服务进行中，会员权益已开通，其他服务将由工作人员继续处理。"
            return "服务进行中，工作人员将持续处理您的订单。"
        if order.status == "completed":
            return "本次服务已完成，感谢您的使用。"
        if order.status == "refunded":
            return "订单已退款，服务已终止。"
        return ""

    @staticmethod
    def _recharge_membership(user: MiniappUser, order: Order, now: datetime) -> None:
        membership_items = [item for item in order.items if item.product_type_snapshot == "membership"]
        days = sum(item.validity_days_snapshot * item.quantity for item in membership_items)
        if days <= 0:
            return
        starts_at = user.membership_expires_at if user.membership_expires_at and user.membership_expires_at > now else now
        expires_at = starts_at + timedelta(days=days)
        user.membership_status = "active"
        user.membership_expires_at = expires_at
        db.session.add(
            MiniappUserMembership(
                user_id=user.id,
                product_id=membership_items[0].product_id if membership_items else None,
                level="standard",
                status="active",
                starts_at=starts_at,
                expires_at=expires_at,
                source_type="order",
                source_id=order.id,
            )
        )

    @staticmethod
    def _create_order(user: MiniappUser, product_items: list[tuple[Product, int]], remark: str) -> Order:
        product_types = {product.product_type for product, _ in product_items}
        product_type = "membership" if product_types == {"membership"} else "other"
        total_amount_cents = sum(product.price_cents * quantity for product, quantity in product_items)
        order = Order(
            order_no=OrderService._create_order_no(),
            user_id=user.id,
            status="pending_payment",
            product_type=product_type,
            total_amount_cents=total_amount_cents,
            paid_amount_cents=0,
            payment_method="",
            service_user_name=user.real_name or "本人",
            remark=remark,
        )
        db.session.add(order)
        db.session.flush()
        for product, quantity in product_items:
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name_snapshot=product.name,
                    product_type_snapshot=product.product_type,
                    product_summary_snapshot=product.summary or "",
                    price_cents_snapshot=product.price_cents,
                    validity_days_snapshot=product.validity_days,
                    quantity=quantity,
                    subtotal_cents=product.price_cents * quantity,
                    image_url_snapshot=product.image_url or "",
                )
            )
        return order

    @staticmethod
    def _get_active_product(product_id) -> Product:
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            raise OrderError("请选择商品") from None
        product = Product.query.filter(
            Product.id == product_id,
            Product.status == "active",
            Product.deleted_at.is_(None),
        ).first()
        if not product:
            raise OrderError("商品不存在或未上架", 404)
        return product

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

    @staticmethod
    def _order_title(items: list[dict]) -> str:
        if not items:
            return ""
        quantity = sum(item["quantity"] for item in items)
        if len(items) == 1 and quantity == 1:
            return items[0]["title"]
        names = [item["title"] for item in items[:2]]
        return f"{'、'.join(names)}等{quantity}件商品"

    @staticmethod
    def _has_membership_items(order: Order) -> bool:
        return any(item.product_type_snapshot == "membership" for item in order.items)

    @staticmethod
    def _all_membership_items(order: Order) -> bool:
        return bool(order.items) and all(item.product_type_snapshot == "membership" for item in order.items)

    @staticmethod
    def _create_order_no() -> str:
        now = datetime.utcnow()
        return f"{now:%Y%m%d%H%M%S%f}{randint(100, 999)}"
