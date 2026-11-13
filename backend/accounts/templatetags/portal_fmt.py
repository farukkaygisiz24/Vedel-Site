from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django import template
from django.utils.html import format_html

register = template.Library()

TWOPLACES = Decimal('0.01')


def _decimal(value):
    if value is None or value == '':
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _group_int(text: str) -> str:
    sign = ''
    if text.startswith('-'):
        sign = '-'
        text = text[1:]
    grouped = ''
    while len(text) > 3:
        grouped = '.' + text[-3:] + grouped
        text = text[:-3]
    return sign + text + grouped


@register.filter
def tr_money(value):
    n = _decimal(value)
    if n is None:
        return '0,00'
    n = n.quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    sign = '-' if n < 0 else ''
    whole, frac = f'{abs(n):.2f}'.split('.')
    return f'{sign}{_group_int(whole)},{frac}'


@register.filter
def plain_money(value):
    """Dot decimal for data-* / JS (never localize)."""
    n = _decimal(value)
    if n is None:
        return '0.00'
    n = n.quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    return f'{n:.2f}'


@register.filter
def tr_qty(value):
    n = _decimal(value)
    if n is None:
        return '0'
    if n == n.to_integral_value():
        return _group_int(str(int(n)))
    n = n.quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    sign = '-' if n < 0 else ''
    whole, frac = f'{abs(n):.2f}'.split('.')
    frac = frac.rstrip('0') or '0'
    return f'{sign}{_group_int(whole)},{frac}'


@register.filter
def tel_link(value):
    text = str(value or '').strip()
    number = ''.join(ch for ch in text if ch.isdigit() or ch == '+')
    if not number:
        return text
    return format_html('<a class="tel-link" href="tel:{}">{}</a>', number, text)
