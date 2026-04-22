from decimal import Decimal

from app.extensions import db
from app.models import CartItem, MiniappUser, Product
from app.services.storage import StorageService
from app.utils.time import beijing_iso


class CartError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


def _format_price(price_cents: int) -> str:
    return f"¥{Decimal(price_cents) / Decimal(100):.2f}"


class CartService:
    @staticmethod
    def list_items(user: MiniappUser) -> dict:
        items = (
            CartItem.query.join(Product)
            .filter(
                CartItem.user_id == user.id,
                CartItem.deleted_at.is_(None),
                Product.status == "active",
                Product.deleted_at.is_(None),
            )
            .order_by(CartItem.created_at.desc())
            .all()
        )
        return {
            "items": [CartService.serialize(item) for item in items],
            "summary": CartService.summary(items),
        }

    @staticmethod
    def add_item(user: MiniappUser, data: dict) -> dict:
        product = CartService._get_active_product(data.get("product_id"))
        quantity = CartService._positive_int(data.get("quantity"), default=1, maximum=99)
        item = CartItem.query.filter(
            CartItem.user_id == user.id,
            CartItem.product_id == product.id,
            CartItem.deleted_at.is_(None),
        ).first()
        if item:
            item.quantity = min(item.quantity + quantity, 99)
        else:
            item = CartItem(user_id=user.id, product_id=product.id, quantity=quantity)
            db.session.add(item)
        db.session.commit()
        return CartService.serialize(item)

    @staticmethod
    def update_item(user: MiniappUser, item_id: int, data: dict) -> dict:
        item = CartService.get_item(user, item_id)
        quantity = CartService._positive_int(data.get("quantity"), default=item.quantity, maximum=99)
        item.quantity = quantity
        db.session.commit()
        return CartService.serialize(item)

    @staticmethod
    def delete_item(user: MiniappUser, item_id: int) -> None:
        item = CartService.get_item(user, item_id)
        item.soft_delete()
        db.session.commit()

    @staticmethod
    def get_item(user: MiniappUser, item_id: int) -> CartItem:
        item = CartItem.query.filter(
            CartItem.id == item_id,
            CartItem.user_id == user.id,
            CartItem.deleted_at.is_(None),
        ).first()
        if not item:
            raise CartError("购物车商品不存在", 404)
        return item

    @staticmethod
    def serialize(item: CartItem) -> dict:
        product = item.product
        price_cents = product.price_cents if product else 0
        return {
            "id": str(item.id),
            "product_id": str(item.product_id),
            "title": product.name if product else "",
            "desc": product.summary if product else "",
            "image_object_key": product.image_object_key or "" if product else "",
            "image": StorageService.sign_url(product.image_object_key) if product else "",
            "price": _format_price(price_cents),
            "price_cents": price_cents,
            "validity_days": product.validity_days if product else None,
            "quantity": item.quantity,
            "subtotal_cents": price_cents * item.quantity,
            "subtotal": _format_price(price_cents * item.quantity),
            "created_at": beijing_iso(item.created_at),
            "updated_at": beijing_iso(item.updated_at),
        }

    @staticmethod
    def summary(items: list[CartItem]) -> dict:
        total_count = sum(item.quantity for item in items)
        total_cents = sum((item.product.price_cents if item.product else 0) * item.quantity for item in items)
        return {
            "total_count": total_count,
            "total_cents": total_cents,
            "total_price": _format_price(total_cents),
        }

    @staticmethod
    def _get_active_product(product_id) -> Product:
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            raise CartError("请选择商品") from None
        product = Product.query.filter(
            Product.id == product_id,
            Product.status == "active",
            Product.deleted_at.is_(None),
        ).first()
        if not product:
            raise CartError("商品不存在或未上架", 404)
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
