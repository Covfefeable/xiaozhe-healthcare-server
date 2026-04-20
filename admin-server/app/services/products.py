from decimal import Decimal

from app.extensions import db
from app.models import Product, ProductStatus, ProductType


VALIDITY_DAY_OPTIONS = {30, 90, 180, 365}


class ProductError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class ProductService:
    @staticmethod
    def serialize(product: Product) -> dict:
        return {
            "id": product.id,
            "name": product.name,
            "summary": product.summary or "",
            "price_cents": product.price_cents,
            "price": f"{Decimal(product.price_cents) / Decimal(100):.2f}",
            "validity_days": product.validity_days,
            "product_type": product.product_type,
            "image_url": product.image_url or "",
            "detail_markdown": product.detail_markdown or "",
            "status": product.status,
            "sort_order": product.sort_order,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        }

    @staticmethod
    def list_products(args) -> dict:
        page = ProductService._positive_int(args.get("page"), default=1)
        page_size = ProductService._positive_int(
            args.get("page_size"),
            default=20,
            maximum=100,
        )
        keyword = (args.get("keyword") or "").strip()
        status = (args.get("status") or "").strip()
        product_type = (args.get("product_type") or "").strip()
        validity_days = args.get("validity_days")

        query = Product.query.filter(Product.deleted_at.is_(None))

        if keyword:
            query = query.filter(Product.name.ilike(f"%{keyword}%"))
        if status:
            if status not in {item.value for item in ProductStatus}:
                raise ProductError("无效的产品状态")
            query = query.filter(Product.status == status)
        if product_type:
            if product_type not in {item.value for item in ProductType}:
                raise ProductError("无效的产品类型")
            query = query.filter(Product.product_type == product_type)
        if validity_days:
            days = ProductService._parse_validity_days_filter(validity_days)
            query = query.filter(Product.validity_days == days)

        total = query.count()
        items = (
            query.order_by(Product.sort_order.asc(), Product.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": [ProductService.serialize(item) for item in items],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
            },
        }

    @staticmethod
    def get_product(product_id: int) -> Product:
        product = Product.query.filter(
            Product.id == product_id,
            Product.deleted_at.is_(None),
        ).first()
        if not product:
            raise ProductError("产品不存在", 404)
        return product

    @staticmethod
    def create_product(data: dict) -> Product:
        payload = ProductService._validate_payload(data)
        product = Product(**payload, status=ProductStatus.DRAFT.value)
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def update_product(product_id: int, data: dict) -> Product:
        product = ProductService.get_product(product_id)
        payload = ProductService._validate_payload(data)
        for key, value in payload.items():
            setattr(product, key, value)
        db.session.commit()
        return product

    @staticmethod
    def delete_product(product_id: int) -> None:
        product = ProductService.get_product(product_id)
        product.soft_delete()
        db.session.commit()

    @staticmethod
    def publish_product(product_id: int) -> Product:
        product = ProductService.get_product(product_id)
        product.status = ProductStatus.ACTIVE.value
        db.session.commit()
        return product

    @staticmethod
    def unpublish_product(product_id: int) -> Product:
        product = ProductService.get_product(product_id)
        product.status = ProductStatus.INACTIVE.value
        db.session.commit()
        return product

    @staticmethod
    def _validate_payload(data: dict) -> dict:
        name = (data.get("name") or "").strip()
        if not name:
            raise ProductError("产品名称不能为空")
        if len(name) > 100:
            raise ProductError("产品名称不能超过 100 个字符")
        summary = (data.get("summary") or "").strip()
        if len(summary) > 20:
            raise ProductError("产品简介不能超过 20 个字符")

        product_type = ProductService._parse_product_type(data.get("product_type"))

        return {
            "name": name,
            "summary": summary,
            "price_cents": ProductService._parse_price_cents(data.get("price_cents")),
            "validity_days": ProductService._parse_validity_days(data.get("validity_days"), product_type),
            "product_type": product_type,
            "image_url": data.get("image_url") or "",
            "detail_markdown": data.get("detail_markdown") or "",
            "sort_order": ProductService._int_or_default(data.get("sort_order"), 0),
        }

    @staticmethod
    def _parse_price_cents(value) -> int:
        try:
            price_cents = int(value)
        except (TypeError, ValueError):
            raise ProductError("产品价格不能为空") from None
        if price_cents < 0:
            raise ProductError("产品价格不能小于 0")
        return price_cents

    @staticmethod
    def _parse_validity_days(value, product_type: str) -> int:
        if product_type == ProductType.OTHER.value:
            return 0
        try:
            days = int(value)
        except (TypeError, ValueError):
            raise ProductError("有效期不能为空") from None
        if days not in VALIDITY_DAY_OPTIONS:
            raise ProductError("有效期只能是 30、90、180、365 天")
        return days

    @staticmethod
    def _parse_validity_days_filter(value) -> int:
        try:
            days = int(value)
        except (TypeError, ValueError):
            raise ProductError("无效的有效期") from None
        if days not in VALIDITY_DAY_OPTIONS:
            raise ProductError("有效期只能是 30、90、180、365 天")
        return days

    @staticmethod
    def _parse_product_type(value) -> str:
        product_type = (value or ProductType.OTHER.value).strip()
        if product_type not in {item.value for item in ProductType}:
            raise ProductError("产品类型不正确")
        return product_type

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
    def _int_or_default(value, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
