from datetime import datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func

from app.models import MiniappUser, Order


def _today_start_utc() -> datetime:
    beijing_now = datetime.utcnow() + timedelta(hours=8)
    beijing_start = datetime.combine(beijing_now.date(), time.min)
    return beijing_start - timedelta(hours=8)


def _format_amount(cents: int | None) -> str:
    return f"{Decimal(cents or 0) / Decimal(100):.2f}"


class DashboardService:
    @staticmethod
    def get_dashboard() -> dict:
        now = datetime.utcnow()
        today_start = _today_start_utc()
        base_orders = Order.query.filter(Order.deleted_at.is_(None))
        paid_amount_cents = (
            base_orders.filter(
                Order.paid_at >= today_start,
                Order.paid_amount_cents > 0,
            )
            .with_entities(func.coalesce(func.sum(Order.paid_amount_cents), 0))
            .scalar()
        )

        return {
            "overview": {
                "today_new_users": MiniappUser.query.filter(
                    MiniappUser.deleted_at.is_(None),
                    MiniappUser.created_at >= today_start,
                ).count(),
                "active_members": MiniappUser.query.filter(
                    MiniappUser.deleted_at.is_(None),
                    MiniappUser.membership_expires_at.isnot(None),
                    MiniappUser.membership_expires_at > now,
                ).count(),
                "today_orders": base_orders.filter(Order.created_at >= today_start).count(),
                "today_paid_amount_cents": int(paid_amount_cents or 0),
                "today_paid_amount": _format_amount(paid_amount_cents),
            },
            "todos": {
                "pending_refund_orders": base_orders.filter(Order.status == "pending_refund").count(),
                "in_progress_orders": base_orders.filter(Order.status == "in_progress").count(),
                "pending_payment_orders": base_orders.filter(Order.status == "pending_payment").count(),
            },
        }
