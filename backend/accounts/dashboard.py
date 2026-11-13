"""Office home (/dashboard/) data. Each block is computed only for roles that see it."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.utils import timezone

ZERO = Decimal('0.00')
LIST_LIMIT = 6

MONTHS_TR = (
    'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
    'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık',
)


@dataclass
class MonthTotal:
    label: str
    total: Decimal
    count: int


@dataclass
class Revenue:
    current: MonthTotal
    previous: MonthTotal
    collected: Decimal | None = None

    @property
    def delta_pct(self) -> int | None:
        if not self.previous.total:
            return None
        change = (self.current.total - self.previous.total) / self.previous.total * 100
        return int(change.quantize(Decimal('1')))

    @property
    def delta_abs(self) -> int | None:
        pct = self.delta_pct
        return None if pct is None else abs(pct)


def month_bounds(today: date) -> tuple[date, date, date]:
    """(previous month start, this month start, next month start)."""
    this_start = today.replace(day=1)
    prev_start = (this_start.replace(year=this_start.year - 1, month=12)
                  if this_start.month == 1 else this_start.replace(month=this_start.month - 1))
    next_start = (this_start.replace(year=this_start.year + 1, month=1)
                  if this_start.month == 12 else this_start.replace(month=this_start.month + 1))
    return prev_start, this_start, next_start


def _month_label(start: date) -> str:
    return f'{MONTHS_TR[start.month - 1]} {start.year}'


def _sum(qs, field: str, start: date, end: date) -> MonthTotal:
    row = qs.filter(date__gte=start, date__lt=end).aggregate(total=Sum(field), count=Count('id'))
    return MonthTotal(_month_label(start), row['total'] or ZERO, row['count'] or 0)


def sales_revenue(today: date) -> Revenue:
    """Device/maintenance sales by sale date, VAT included (grand_total)."""
    from sales.models import PaymentAllocation, Sale

    prev_start, this_start, next_start = month_bounds(today)
    collected = (
        PaymentAllocation.objects.filter(
            sale__isnull=False,
            payment__date__gte=this_start,
            payment__date__lt=next_start,
        ).aggregate(total=Sum('amount'))['total']
        or ZERO
    )
    return Revenue(
        current=_sum(Sale.objects.all(), 'grand_total', this_start, next_start),
        previous=_sum(Sale.objects.all(), 'grand_total', prev_start, this_start),
        collected=collected,
    )


def service_revenue(today: date) -> Revenue:
    """Closed service jobs not tied to a sale (mount jobs are counted in sales)."""
    from sales.models import PaymentAllocation
    from service.models import Job

    prev_start, this_start, next_start = month_bounds(today)
    qs = Job.objects.filter(status=Job.STATUS_CLOSED, sale__isnull=True)
    collected = (
        PaymentAllocation.objects.filter(
            job__isnull=False,
            job__sale__isnull=True,
            payment__date__gte=this_start,
            payment__date__lt=next_start,
        ).aggregate(total=Sum('amount'))['total']
        or ZERO
    )
    return Revenue(
        current=_sum(qs, 'grand_total', this_start, next_start),
        previous=_sum(qs, 'grand_total', prev_start, this_start),
        collected=collected,
    )


def _critical(qs):
    from stock.services import LOW_STOCK

    return qs.filter(LOW_STOCK | Q(stock_qty__lt=0), is_active=True).select_related('category')


def device_stock_alerts():
    """Devices (klima units) at/below their critical threshold, or negative."""
    from stock.models import Product

    qs = _critical(Product.objects.filter(Q(is_device=True) | Q(category__is_klima=True)))
    return qs.order_by('stock_qty', 'name')


def copper_stock():
    """All copper pipe products with remaining meters, lowest first."""
    from stock.models import Product

    return (
        Product.objects.filter(category__is_copper_pipe=True, is_active=True)
        .select_related('category')
        .order_by('stock_qty', 'name')
    )


def mount_stock_alerts():
    """Mount materials (not copper) at/below threshold, or negative."""
    from stock.models import Product
    from stock.services import MOUNT_CATEGORY_SLUG

    qs = _critical(Product.objects.filter(category__slug=MOUNT_CATEGORY_SLUG, is_device=False))
    return qs.order_by('stock_qty', 'name')


def dashboard_context(user, today: date | None = None) -> dict:
    today = today or timezone.localdate()
    ctx: dict = {'today': today}
    can_sales = getattr(user, 'can_sales', False)
    can_lead = getattr(user, 'can_service_lead', False)

    if can_sales:
        ctx['sales_revenue'] = sales_revenue(today)
        alerts = device_stock_alerts()
        ctx['device_alerts'] = list(alerts[:LIST_LIMIT])
        ctx['device_alert_count'] = alerts.count()

    if can_lead:
        from service.services import due_maintenance, missed_jobs

        ctx['service_revenue'] = service_revenue(today)

        copper = list(copper_stock())
        ctx['copper_items'] = copper
        mount = mount_stock_alerts()
        ctx['mount_alerts'] = list(mount[:LIST_LIMIT])
        ctx['mount_alert_count'] = mount.count()

        missed = missed_jobs(today).select_related('party', 'sale').order_by('date', 'time', 'id')
        ctx['missed_jobs'] = list(missed[:LIST_LIMIT])
        ctx['missed_count'] = missed.count()
        from service.models import Job

        ctx['today_open_count'] = Job.objects.filter(
            date=today, status__in=(Job.STATUS_OPEN, Job.STATUS_PENDING)
        ).count()

        due = due_maintenance(today).select_related('party').order_by('next_due', 'name')
        ctx['due_devices'] = list(due[:LIST_LIMIT])
        ctx['due_overdue_count'] = due.filter(next_due__lt=today).count()
        ctx['due_soon_count'] = due.filter(next_due__gte=today).count()

    return ctx
