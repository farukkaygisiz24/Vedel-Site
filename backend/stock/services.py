import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.db import transaction
from django.db.models import F, Q

from .models import Category, Product, StockMovement

TWOPLACES = Decimal('0.01')
DEFAULT_CATEGORY_NAME = 'Merkez Depo'
DEFAULT_CATEGORY_SLUG = 'merkez-depo'
DEFAULT_SKU_PREFIX = 'STK'
MOUNT_CATEGORY_NAME = 'Klima Montaj Malzemesi'
MOUNT_CATEGORY_SLUG = 'klima-montaj-malzemesi'
MOUNT_SKU_PREFIX = 'KMM'
COPPER_CATEGORY_NAME = 'Bakır Boru'
COPPER_CATEGORY_SLUG = 'bakir-boru'
COPPER_SKU_PREFIX = 'BAK'
MAX_INCLUDED_COPPER_METERS = Decimal('1000.00')

# Products at/below their critical threshold ("Kritik eşik", only when "Hatırlat" is on).
LOW_STOCK = Q(alert_on=True) & (
    Q(alert_qty__isnull=True, stock_qty__lte=0)
    | Q(alert_qty__isnull=False, stock_qty__lte=F('alert_qty'))
)
SERVICE_LABOR_SKU = 'KS-0004'
SERVICE_CATEGORY_SLUG = 'klima-servis'
AUTO_SKU_RETRIES = 5
AUTO_SKU_RE = re.compile(r'^([A-Z]{2,6})-(\d+)$')
PREFIX_RE = re.compile(r'^[A-Z]{2,6}$')
SLUG_RE = re.compile(r'[^a-z0-9]+')
SLUG_TR = str.maketrans({
    'Ç': 'c',
    'Ğ': 'g',
    'İ': 'i',
    'I': 'i',
    'Ö': 'o',
    'Ş': 's',
    'Ü': 'u',
    'ç': 'c',
    'ğ': 'g',
    'ı': 'i',
    'i': 'i',
    'ö': 'o',
    'ş': 's',
    'ü': 'u',
})


def tr_upper(value: str) -> str:
    return str(value or '').replace('i', 'İ').replace('ı', 'I').upper()


def tr_lower(value: str) -> str:
    return str(value or '').replace('İ', 'i').replace('I', 'ı').lower()


def pretty_label(value: str) -> str:
    words = str(value or '').split()
    if not words:
        return ''
    letters = ''.join(ch for ch in ''.join(words) if ch.isalpha())
    if letters and letters == tr_upper(letters) and letters != tr_lower(letters):
        return ' '.join(words)
    titled = []
    for word in words:
        titled.append(tr_upper(word[:1]) + tr_lower(word[1:]))
    return ' '.join(titled)


def normalize_prefix(raw) -> str:
    text = str(raw or '').replace('ı', 'I').replace('i', 'I').replace('İ', 'I').upper()
    text = re.sub(r'[^A-Z]', '', text)
    if not PREFIX_RE.match(text):
        raise ValueError('Stok öneki 2–6 harf olmalı (MHI, ERF, STK).')
    return text


def prefix_for(category=None) -> str:
    if category is not None and getattr(category, 'sku_prefix', ''):
        return str(category.sku_prefix).upper()
    return DEFAULT_SKU_PREFIX


def default_category(user=None) -> Category:
    item = Category.objects.filter(name=DEFAULT_CATEGORY_NAME).first()
    if item:
        return item
    old = Category.objects.filter(name='MERKEZ DEPO').first()
    if old:
        old.name = DEFAULT_CATEGORY_NAME
        old.save(update_fields=['name'])
        return old
    stk = Category.objects.filter(sku_prefix=DEFAULT_SKU_PREFIX).first()
    if stk:
        return stk
    if user is not None:
        return create_category(
            name=DEFAULT_CATEGORY_NAME,
            prefix=DEFAULT_SKU_PREFIX,
            user=user,
        )
    first = Category.objects.order_by('pk').first()
    if first:
        return first
    raise ValueError('Kategori zorunlu.')


def mount_category(user=None) -> Category:
    item = Category.objects.filter(slug=MOUNT_CATEGORY_SLUG).first()
    if item:
        return item
    item = Category.objects.filter(name=MOUNT_CATEGORY_NAME).first()
    if item:
        if item.slug != MOUNT_CATEGORY_SLUG and not Category.objects.filter(slug=MOUNT_CATEGORY_SLUG).exists():
            item.slug = MOUNT_CATEGORY_SLUG
            item.save(update_fields=['slug'])
        return item
    item = Category.objects.filter(sku_prefix=MOUNT_SKU_PREFIX).first()
    if item:
        return item
    if user is not None:
        return create_category(
            name=MOUNT_CATEGORY_NAME,
            prefix=MOUNT_SKU_PREFIX,
            user=user,
        )
    raise ValueError('Klima Montaj Malzemesi deposu yok.')


def next_sku(prefix=None) -> str:
    if prefix:
        code = normalize_prefix(prefix)
    else:
        code = DEFAULT_SKU_PREFIX
    item_re = re.compile(rf'^{re.escape(code)}-(\d+)$')
    serial = 0
    for sku in Product.objects.filter(sku__startswith=f'{code}-').values_list('sku', flat=True):
        match = item_re.match(sku)
        if match:
            serial = max(serial, int(match.group(1)))
    return f'{code}-{serial + 1:04d}'


def is_auto_sku(sku: str) -> bool:
    return bool(AUTO_SKU_RE.match(str(sku or '')))


def category_slug(name: str) -> str:
    text = SLUG_RE.sub('-', str(name or '').translate(SLUG_TR).lower()).strip('-')
    return text or 'category'


def next_category_slug(name: str) -> str:
    base = category_slug(name)
    slug = base
    serial = 2
    while Category.objects.filter(slug=slug).exists():
        slug = f'{base}-{serial}'
        serial += 1
    return slug


def _parse_klima_flag(raw) -> bool:
    return str(raw or '').strip() in ('1', 'on', 'true', 'yes')


def _parse_copper_flag(raw) -> bool:
    return str(raw or '').strip() in ('1', 'on', 'true', 'yes')


def parse_included_copper_meters(raw) -> Decimal:
    text = str(raw or '').strip()
    if not text:
        return Decimal('0.00')
    value = parse_decimal(text, 'Split dahil bakır (mt)')
    if value < 0:
        raise ValueError('Split dahil bakır metre negatif olamaz.')
    if value > MAX_INCLUDED_COPPER_METERS:
        raise ValueError('Split dahil bakır metre en fazla 1000 olabilir.')
    return value


def mount_material_filter():
    from django.db.models import Q

    return Q(category__slug=MOUNT_CATEGORY_SLUG) | Q(category__is_copper_pipe=True)


def copper_category(user=None) -> Category:
    item = Category.objects.filter(slug=COPPER_CATEGORY_SLUG).first()
    if item:
        return item
    item = Category.objects.filter(name=COPPER_CATEGORY_NAME).first()
    if item:
        changed = []
        if item.slug != COPPER_CATEGORY_SLUG and not Category.objects.filter(slug=COPPER_CATEGORY_SLUG).exists():
            item.slug = COPPER_CATEGORY_SLUG
            changed.append('slug')
        if not item.is_copper_pipe:
            item.is_copper_pipe = True
            changed.append('is_copper_pipe')
        if changed:
            item.save(update_fields=changed)
        return item
    item = Category.objects.filter(sku_prefix=COPPER_SKU_PREFIX).first()
    if item:
        if not item.is_copper_pipe:
            item.is_copper_pipe = True
            item.save(update_fields=['is_copper_pipe'])
        return item
    if user is not None:
        return create_category(
            name=COPPER_CATEGORY_NAME,
            prefix=COPPER_SKU_PREFIX,
            user=user,
            is_copper_pipe=True,
        )
    raise ValueError('Bakır Boru deposu yok.')


def create_category(
    *,
    name: str,
    prefix: str,
    user,
    brand: str = '',
    is_klima: bool = False,
    is_copper_pipe: bool = False,
    included_copper_meters=None,
) -> Category:
    name = pretty_label(name)
    if not name:
        raise ValueError('Kategori adı zorunlu.')
    sku_prefix = normalize_prefix(prefix)
    is_klima = bool(is_klima)
    is_copper_pipe = bool(is_copper_pipe)
    if is_klima and is_copper_pipe:
        raise ValueError('Klima ve bakır boru aynı kategoride olamaz.')
    if is_klima and sku_prefix == MOUNT_SKU_PREFIX:
        raise ValueError('Montaj kategorisi klima olamaz.')
    if is_klima and sku_prefix == COPPER_SKU_PREFIX:
        raise ValueError('Bakır boru kategorisi klima olamaz.')
    if is_copper_pipe and sku_prefix == MOUNT_SKU_PREFIX:
        raise ValueError('Montaj kategorisi bakır boru olarak işaretlenemez.')
    if included_copper_meters is None:
        meters = Decimal('0.00')
    elif isinstance(included_copper_meters, Decimal):
        meters = included_copper_meters
    else:
        meters = parse_included_copper_meters(included_copper_meters)
    if not is_klima:
        meters = Decimal('0.00')
    return Category.objects.create(
        name=name,
        slug=next_category_slug(name),
        sku_prefix=sku_prefix,
        brand=pretty_label(brand),
        is_klima=is_klima,
        is_copper_pipe=is_copper_pipe,
        included_copper_meters=meters,
        created_by=user,
    )


PROTECTED_CATEGORY_SLUGS = frozenset(
    {
        DEFAULT_CATEGORY_SLUG,
        MOUNT_CATEGORY_SLUG,
        COPPER_CATEGORY_SLUG,
        SERVICE_CATEGORY_SLUG,
    }
)


def delete_category(*, item: Category) -> None:
    if item.slug in PROTECTED_CATEGORY_SLUGS:
        raise ValueError('Bu kategori silinemez.')
    count = item.products.count()
    if count:
        raise ValueError(f'Bu kategoride {count} ürün var. Önce ürünleri silin.')
    item.delete()


def update_category(
    *,
    item: Category,
    name: str,
    prefix: str,
    brand: str = '',
    is_klima: bool = False,
    is_copper_pipe: bool = False,
    included_copper_meters=None,
) -> Category:
    name = pretty_label(name)
    if not name:
        raise ValueError('Kategori adı zorunlu.')
    new_prefix = normalize_prefix(prefix)
    if new_prefix != item.sku_prefix and item.products.exists():
        raise ValueError('Bu kategoride ürün varken önek değişmez.')
    is_klima = bool(is_klima)
    is_copper_pipe = bool(is_copper_pipe)
    if item.slug == COPPER_CATEGORY_SLUG:
        # The protected copper depot always stays copper.
        is_copper_pipe = True
    if is_klima and is_copper_pipe:
        raise ValueError('Klima ve bakır boru aynı kategoride olamaz.')
    if is_klima and (new_prefix == MOUNT_SKU_PREFIX or item.slug == MOUNT_CATEGORY_SLUG):
        raise ValueError('Montaj kategorisi klima olamaz.')
    if is_klima and (new_prefix == COPPER_SKU_PREFIX or item.slug == COPPER_CATEGORY_SLUG or item.is_copper_pipe):
        raise ValueError('Bakır boru kategorisi klima olamaz.')
    if is_copper_pipe and (new_prefix == MOUNT_SKU_PREFIX or item.slug == MOUNT_CATEGORY_SLUG):
        raise ValueError('Montaj kategorisi bakır boru olarak işaretlenemez.')
    if included_copper_meters is None:
        meters = item.included_copper_meters or Decimal('0.00')
    elif isinstance(included_copper_meters, Decimal):
        meters = included_copper_meters
    else:
        meters = parse_included_copper_meters(included_copper_meters)
    if not is_klima:
        meters = Decimal('0.00')
    item.name = name
    item.sku_prefix = new_prefix
    item.brand = pretty_label(brand)
    item.is_klima = is_klima
    item.is_copper_pipe = is_copper_pipe
    item.included_copper_meters = meters
    item.save(
        update_fields=['name', 'sku_prefix', 'brand', 'is_klima', 'is_copper_pipe', 'included_copper_meters']
    )
    return item


def parse_decimal(raw, field: str) -> Decimal:
    text = str(raw or '').strip().replace('\xa0', '').replace(' ', '')
    if not text:
        raise ValueError(f'{field} boş olamaz.')
    if ',' in text:
        text = text.replace('.', '').replace(',', '.')
    else:
        parts = text.split('.')
        if len(parts) > 1 and all(len(part) == 3 for part in parts[1:]):
            text = ''.join(parts)
    try:
        return Decimal(text).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f'{field} geçersiz.') from exc


class StockError(ValueError):
    pass


@transaction.atomic
def apply_movement(
    *,
    product: Product,
    qty: Decimal,
    reason: str,
    user,
    sale_line=None,
    job=None,
    note: str = '',
    allow_negative: bool = False,
    supplier=None,
    buy_price=None,
) -> StockMovement:
    locked = Product.objects.select_for_update().get(pk=product.pk)
    next_qty = locked.stock_qty + qty
    if next_qty < 0 and reason != StockMovement.REASON_SALE and not allow_negative:
        raise StockError(f'{locked.name} için yetersiz stok (elde {locked.stock_qty}).')
    locked.stock_qty = next_qty
    updates = ['stock_qty', 'updated_at']
    snap = buy_price
    if snap is None:
        snap = Decimal('0.00')
    elif snap < 0:
        raise ValueError('Alış fiyatı negatif olamaz.')
    if reason == StockMovement.REASON_IN and buy_price is not None:
        locked.buy_price = snap
        updates.append('buy_price')
    locked.save(update_fields=updates)
    return StockMovement.objects.create(
        product=locked,
        qty=qty,
        reason=reason,
        buy_price=snap,
        supplier=supplier,
        sale_line=sale_line,
        job=job,
        note=note,
        created_by=user,
    )


def tracks_serial_from_post(post) -> bool:
    raw = str(post.get('tracks_serial', '')).strip().lower()
    if raw in {'1', 'on', 'true', 'yes'}:
        return True
    if raw in {'0', 'off', 'false', 'no'}:
        return False
    kind = str(post.get('device_kind', '')).strip()
    return kind in {
        Product.KIND_SPLIT,
        Product.KIND_MULTI_INDOOR,
        Product.KIND_MULTI_OUTDOOR,
    }


def apply_device_fields(product: Product, post, *, exclude_pk=None) -> Product:
    category = product.category
    tracks = tracks_serial_from_post(post)
    kind = str(post.get('device_kind', '')).strip()
    if kind not in {
        Product.KIND_SPLIT,
        Product.KIND_MULTI_INDOOR,
        Product.KIND_MULTI_OUTDOOR,
        Product.KIND_NONE,
    }:
        kind = Product.KIND_NONE

    product.outdoor = None
    if not tracks:
        product.is_device = False
        product.device_kind = Product.KIND_NONE
        product.outdoor_name = ''
        return product

    if category is not None and category.is_klima:
        if kind == Product.KIND_NONE:
            raise ValueError('Split veya multi seçin.')
        product.device_kind = kind
        product.is_device = True
        if kind == Product.KIND_SPLIT:
            name = tr_upper(post.get('outdoor_name', ''))
            if not name:
                raise ValueError('Split cihazda dış ünite model kodu zorunlu.')
            product.outdoor_name = name
        else:
            product.outdoor_name = ''
        return product

    product.is_device = True
    product.device_kind = Product.KIND_NONE
    product.outdoor_name = ''
    return product


def update_product(*, product: Product, post) -> Product:
    name = tr_upper(post.get('name', ''))
    if not name:
        raise ValueError('Ürün adı zorunlu.')
    product.brand = pretty_label(post.get('brand', ''))
    product.name = name
    product.unit = tr_upper(post.get('unit', '')) or 'ADET'
    vat_raw = str(post.get('vat_rate', '')).strip()
    product.vat_rate = parse_decimal(vat_raw, 'KDV') if vat_raw else Decimal('20.00')
    buy_raw = str(post.get('buy_price', '')).strip()
    sale_raw = str(post.get('sale_price', '')).strip()
    if buy_raw:
        buy_price = parse_decimal(buy_raw, 'Alış fiyatı')
        if buy_price < 0:
            raise ValueError('Alış fiyatı negatif olamaz.')
        product.buy_price = buy_price
    if sale_raw:
        sale_price = parse_decimal(sale_raw, 'Satış fiyatı')
        if sale_price < 0:
            raise ValueError('Satış fiyatı negatif olamaz.')
        product.sale_price = sale_price
    apply_device_fields(product, post)
    product.save(
        update_fields=[
            'brand',
            'name',
            'unit',
            'vat_rate',
            'buy_price',
            'sale_price',
            'is_device',
            'device_kind',
            'outdoor',
            'outdoor_name',
            'updated_at',
        ]
    )
    return product
