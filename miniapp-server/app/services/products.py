from decimal import Decimal

from app.models import Product
from app.services.storage import StorageService
from app.utils.time import beijing_iso


class ProductError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


def _format_price(price_cents: int) -> str:
    return f"¥{Decimal(price_cents) / Decimal(100):.2f}"


class ProductService:
    @staticmethod
    def serialize(product: Product, featured: bool = False) -> dict:
        return {
            "id": str(product.id),
            "title": product.name,
            "desc": product.summary or "",
            "price": _format_price(product.price_cents),
            "price_cents": product.price_cents,
            "validity_days": product.validity_days,
            "product_type": product.product_type,
            "badge": "今日推荐" if featured else None,
            "featured": featured,
            "image_object_key": product.image_object_key or "",
            "image": StorageService.sign_url(product.image_object_key) or None,
            "content": product.detail_markdown or "",
            "created_at": beijing_iso(product.created_at),
            "updated_at": beijing_iso(product.updated_at),
        }

    @staticmethod
    def list_products() -> list[dict]:
        products = (
            Product.query.filter(
                Product.status == "active",
                Product.deleted_at.is_(None),
            )
            .order_by(Product.sort_order.asc(), Product.created_at.desc())
            .all()
        )
        return [
            ProductService.serialize(product, featured=index == 0)
            for index, product in enumerate(products)
        ]

    @staticmethod
    def get_product(product_id: int) -> dict:
        product = Product.query.filter(
            Product.id == product_id,
            Product.status == "active",
            Product.deleted_at.is_(None),
        ).first()
        if not product:
            raise ProductError("产品不存在或未上架", 404)
        return ProductService.serialize(product)
