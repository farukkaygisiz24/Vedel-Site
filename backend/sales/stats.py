"""Sales page summaries: systems sold per year and period labels."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from django.db.models import Count, Sum

ZERO = Decimal('0.00')
TOP_LIMIT = 3

MONTHS_SHORT_TR = ('Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara')


@dataclass
class TopProduct:
    name: str
    qty: int
    total: Decimal


@dataclass
class YearSummary:
    year: int
    sale_count: int = 0
    revenue: Decimal = ZERO
    systems: int = 0
    split_systems: int = 0
    multi_systems: int = 0
    top: list[TopProduct] = field(default_factory=list)

    @property
    def average(self) -> Decimal:
        if not self.sale_count:
            return ZERO
        return (self.revenue / self.sale_count).quantize(Decimal('0.01'))


def _qty(value) -> int:
    try:
        return max(0, int(Decimal(value or 0)))
    except (ArithmeticError, TypeError, ValueError):
        return 0


def year_summary(year: int) -> YearSummary:
    """A system is one split or one multi outdoor unit; multi indoors belong to their outdoor.

    Legacy klima lines without a device kind count as splits unless the sale has a multi outdoor.
    The top list ranks systems only, so multi indoors stay out of it.
    """
    from service.services import _product_kind, sale_line_is_device
    from stock.models import Product

    from .models import Sale, SaleLine

    sales = Sale.objects.filter(date__year=year)
    totals = sales.aggregate(revenue=Sum('grand_total'), count=Count('id'))
    summary = YearSummary(year=year, sale_count=totals['count'] or 0, revenue=totals['revenue'] or ZERO)

    lines = (
        SaleLine.objects.filter(sale__date__year=year, product__isnull=False, is_copper=False)
        .select_related('product', 'product__category', 'sale')
        .order_by('sale_id', 'id')
    )
    by_sale: dict[int, list] = defaultdict(list)
    for line in lines:
        if sale_line_is_device(line, line.sale):
            by_sale[line.sale_id].append(line)

    top: dict[int, TopProduct] = {}
    for sale_lines in by_sale.values():
        kinds = [_product_kind(line.product) for line in sale_lines]
        has_outdoor = Product.KIND_MULTI_OUTDOOR in kinds
        for line, kind in zip(sale_lines, kinds):
            qty = _qty(line.qty)
            if kind == Product.KIND_SPLIT or (not kind and not has_outdoor):
                summary.split_systems += qty
            elif kind == Product.KIND_MULTI_OUTDOOR:
                summary.multi_systems += qty
            else:
                continue
            item = top.get(line.product_id)
            if item is None:
                item = top[line.product_id] = TopProduct(line.product.display_name, 0, ZERO)
            item.qty += qty
            item.total += line.line_total or ZERO
    summary.systems = summary.split_systems + summary.multi_systems
    summary.top = sorted(top.values(), key=lambda item: (-item.qty, -item.total, item.name))[:TOP_LIMIT]
    return summary


def _day(value: date, with_year: bool) -> str:
    text = f'{value.day} {MONTHS_SHORT_TR[value.month - 1]}'
    return f'{text} {value.year}' if with_year else text


def period_label(date_from: date | None, date_to: date | None, today: date) -> str:
    if not date_from and not date_to:
        return 'Tüm zamanlar'
    years = {item.year for item in (date_from, date_to) if item}
    with_year = years != {today.year}
    if date_from and date_to:
        return f'{_day(date_from, with_year)} – {_day(date_to, with_year)}'
    if date_from:
        return f'{_day(date_from, with_year)} – bugün'
    return f'– {_day(date_to, with_year)}'
