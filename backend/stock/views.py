from decimal import Decimal
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from accounts.http import can_access_category, role_required, stock_scope
from accounts.models import Customer
from accounts.portal import _wants_json
from accounts.search import q_search
from accounts.toasts import queue_toast
from accounts.weather import get_weather
from sales.models import Party
from stock.models import Category, Product, StockMovement
from stock.services import (
    LOW_STOCK,
    AUTO_SKU_RETRIES,
    StockError,
    apply_device_fields,
    apply_movement,
    DEFAULT_CATEGORY_SLUG,
    _parse_copper_flag,
    _parse_klima_flag,
    create_category,
    default_category,
    delete_category,
    mount_category,
    mount_material_filter,
    update_category,
    is_auto_sku,
    next_sku,
    parse_decimal,
    prefix_for,
    pretty_label,
    update_product,
)

PRODUCT_PAGE_SIZE = 6
STOCK_LIST_PAGE_SIZE = 20
QTY_FIELD = DecimalField(max_digits=12, decimal_places=2)
MONEY_FIELD = DecimalField(max_digits=14, decimal_places=2)
QTY_ZERO = Value(Decimal('0.00'), output_field=QTY_FIELD)
MONEY_ZERO = Value(Decimal('0.00'), output_field=MONEY_FIELD)


def _ctx(**extra):
    extra.setdefault('weather', get_weather())
    return extra


def tr_upper(value: str) -> str:
    return str(value or '').replace('i', 'İ').replace('ı', 'I').upper().strip()


def parse_alert_qty(raw):
    text = str(raw or '').strip()
    if not text:
        return None
    qty = parse_decimal(text, 'Kritik eşik')
    if qty < 0:
        raise ValueError('Kritik eşik negatif olamaz.')
    return qty


def _product_payload(item: Product) -> dict:
    return {
        'ok': True,
        'id': item.pk,
        'name': item.name,
        'brand': item.brand,
        'label': item.display_name,
        'sku': item.sku,
        'url': item.get_absolute_url(),
        'price': str(item.sale_price),
        'buy': str(item.buy_price),
        'vat': str(item.vat_rate),
        'stock': str(item.stock_qty),
        'unit': item.unit,
        'device_kind': item.device_kind,
        'is_klima': bool(item.category_id and item.category.is_klima),
        'outdoor_name': item.outdoor_name,
        'is_device': item.is_device,
    }


def product_search_json(request: HttpRequest) -> JsonResponse:
    query = str(request.GET.get('q', '')).strip()
    try:
        page = max(1, int(request.GET.get('page', '1')))
    except (TypeError, ValueError):
        page = 1
    qs = Product.objects.filter(is_active=True).select_related('category')
    if str(request.GET.get('mount', '')).strip() in ('1', 'true', 'on'):
        qs = qs.filter(mount_material_filter(), is_device=False)
    copper_only = str(request.GET.get('copper', '')).strip() in ('1', 'true', 'on')
    if copper_only:
        qs = qs.filter(category__is_copper_pipe=True, is_device=False)
    elif str(request.GET.get('sale', '')).strip() in ('1', 'true', 'on'):
        # Normal sale lines: copper goes through the "Anlaşma kalemi" panel only.
        qs = qs.exclude(category__is_copper_pipe=True)
    family = str(request.GET.get('device_family', '')).strip()
    scope = stock_scope(request.user)
    if scope is not None:
        qs = qs.filter(category__in=scope)
    cat_raw = str(request.GET.get('category_id', '')).strip()
    cat = Category.objects.filter(pk=int(cat_raw)).first() if cat_raw.isdigit() else None
    if cat and not can_access_category(request.user, cat):
        cat = None
    merkez = Category.objects.filter(slug=DEFAULT_CATEGORY_SLUG).first()
    if merkez and not can_access_category(request.user, merkez):
        merkez = None

    if copper_only:
        cat = None
        family = ''
    if cat and cat.is_klima:
        # Klima markası + Split/Multi cihazlar; Merkez Depo her markada global.
        if family == Product.KIND_SPLIT:
            brand_q = (
                Q(category=cat)
                & (Q(device_kind=Product.KIND_SPLIT) | Q(outdoor_name__gt=''))
                & ~Q(device_kind__in=[Product.KIND_MULTI_INDOOR, Product.KIND_MULTI_OUTDOOR])
            )
        elif family == 'multi':
            brand_q = (
                Q(category=cat)
                & (
                    Q(device_kind__in=[Product.KIND_MULTI_INDOOR, Product.KIND_MULTI_OUTDOOR])
                    | Q(is_device=True, outdoor_name='', device_kind='')
                )
                & ~Q(device_kind=Product.KIND_SPLIT)
            )
        else:
            brand_q = Q(category=cat)
        if merkez:
            qs = qs.filter(brand_q | Q(category=merkez))
        else:
            qs = qs.filter(brand_q)
    else:
        if family == Product.KIND_SPLIT:
            qs = qs.filter(Q(device_kind=Product.KIND_SPLIT) | Q(outdoor_name__gt='')).exclude(
                device_kind__in=[Product.KIND_MULTI_INDOOR, Product.KIND_MULTI_OUTDOOR]
            )
        elif family == 'multi':
            qs = qs.filter(
                Q(device_kind__in=[Product.KIND_MULTI_INDOOR, Product.KIND_MULTI_OUTDOOR])
                | Q(is_device=True, outdoor_name='', device_kind='')
            ).exclude(device_kind=Product.KIND_SPLIT)
        if cat:
            qs = qs.filter(category=cat)
    tokens = [token for token in query.split() if token]
    for token in tokens:
        qs = qs.filter(q_search(token, 'name', 'sku', 'brand'))
    paginator = Paginator(qs.order_by('name'), PRODUCT_PAGE_SIZE)
    page_obj = paginator.get_page(page)
    prefix = None
    if cat:
        prefix = prefix_for(cat)
    elif getattr(request.user, 'can_stock_manage', False):
        prefix = prefix_for(default_category(request.user))
    else:
        prefix = prefix_for(None)
    return JsonResponse(
        {
            'ok': True,
            'results': [_product_payload(item) for item in page_obj.object_list],
            'page': page_obj.number,
            'pages': paginator.num_pages,
            'count': paginator.count,
            'has_next': page_obj.has_next(),
            'next_sku': next_sku(prefix),
        }
    )


def _create_product(request: HttpRequest) -> Product:
    name = tr_upper(request.POST.get('name', ''))
    if not name:
        raise ValueError('Ürün adı zorunlu.')
    brand = pretty_label(request.POST.get('brand', ''))
    vat_raw = str(request.POST.get('vat_rate', '')).strip()
    price_raw = str(request.POST.get('sale_price', '')).strip()
    vat_rate = parse_decimal(vat_raw or '20', 'KDV')
    sale_price = parse_decimal(price_raw or '0', 'Satış fiyatı')
    buy_raw = str(request.POST.get('buy_price', '')).strip()
    buy_price = parse_decimal(buy_raw, 'Alış fiyatı') if buy_raw else None
    if buy_price is not None and buy_price < 0:
        raise ValueError('Alış fiyatı negatif olamaz.')
    alert_qty = parse_alert_qty(request.POST.get('alert_qty', ''))
    alert_on = str(request.POST.get('alert_on', '')).strip() in ('1', 'on', 'true')
    unit = tr_upper(request.POST.get('unit', '')) or 'ADET'
    category_raw = str(request.POST.get('category_id', '')).strip()
    if category_raw:
        category = Category.objects.get(pk=category_raw)
    else:
        category = default_category(request.user)
    prefix = prefix_for(category)
    product = None
    last_integrity = None
    for _attempt in range(AUTO_SKU_RETRIES):
        current_sku = next_sku(prefix)
        try:
            with transaction.atomic():
                product = Product.objects.create(
                    sku=current_sku,
                    brand=brand,
                    name=name,
                    category=category,
                    unit=unit,
                    vat_rate=vat_rate,
                    sale_price=sale_price,
                    buy_price=buy_price or Decimal('0.00'),
                    alert_qty=alert_qty,
                    alert_on=alert_on,
                    created_by=request.user,
                )
            break
        except IntegrityError as exc:
            last_integrity = exc
            if not is_auto_sku(current_sku):
                raise
    if product is None:
        raise last_integrity or IntegrityError('Bu stok kodu zaten var.')
    qty_raw = str(request.POST.get('qty', '')).strip()
    if qty_raw:
        qty = parse_decimal(qty_raw, 'Adet')
        if qty > 0:
            apply_movement(
                product=product,
                qty=qty,
                reason=StockMovement.REASON_IN,
                user=request.user,
                note=str(request.POST.get('note', '')).strip(),
                buy_price=buy_price,
            )
            product.refresh_from_db()
    elif buy_price is not None:
        product.buy_price = buy_price
        product.save(update_fields=['buy_price', 'updated_at'])
        product.refresh_from_db()
    apply_device_fields(product, request.POST)
    product.save(update_fields=['is_device', 'device_kind', 'outdoor', 'outdoor_name', 'updated_at'])
    return product


def _stock_in(request: HttpRequest, product: Product) -> Product:
    qty = parse_decimal(request.POST.get('qty'), 'Adet')
    if qty <= 0:
        raise ValueError('Giriş adedi sıfırdan büyük olmalı.')
    buy_raw = str(request.POST.get('buy_price', '')).strip()
    buy_price = parse_decimal(buy_raw, 'Alış fiyatı') if buy_raw else None
    if buy_price is not None and buy_price < 0:
        raise ValueError('Alış fiyatı negatif olamaz.')
    supplier = None
    supplier_raw = str(request.POST.get('supplier_id', '')).strip()
    if supplier_raw:
        supplier = Party.objects.get(pk=supplier_raw)
    apply_movement(
        product=product,
        qty=qty,
        reason=StockMovement.REASON_IN,
        user=request.user,
        note=str(request.POST.get('note', '')).strip(),
        supplier=supplier,
        buy_price=buy_price,
    )
    product.refresh_from_db()
    return product


def _sku_map():
    data = {'': next_sku()}
    for item in Category.objects.all():
        data[str(item.pk)] = next_sku(item.sku_prefix)
    return data


def _category_payload(item: Category, toast='') -> dict:
    return {
        'ok': True,
        'id': item.pk,
        'name': item.name,
        'slug': item.slug,
        'prefix': item.sku_prefix,
        'brand': item.brand,
        'is_klima': bool(item.is_klima),
        'is_copper_pipe': bool(item.is_copper_pipe),
        'included_copper_meters': str(item.included_copper_meters or Decimal('0.00')),
        'locked': item.products.exists(),
        'next_sku': next_sku(item.sku_prefix),
        'url': f'/stock/?category={item.slug}',
        'toast': toast,
    }


def _category_choices():
    cats = list(Category.objects.annotate(product_n=Count('products')))
    cats.sort(key=lambda item: (item.slug != DEFAULT_CATEGORY_SLUG, item.name))
    return [
        {
            'id': str(item.pk),
            'name': item.name,
            'prefix': item.sku_prefix,
            'brand': item.brand,
            'is_klima': bool(item.is_klima),
            'is_copper_pipe': bool(item.is_copper_pipe),
            'included_copper_meters': str(item.included_copper_meters or Decimal('0.00')),
            'slug': item.slug,
            'locked': item.product_n > 0,
        }
        for item in cats
    ]


def _stock_querystring(values, page=None):
    data = {}
    for key in ('q', 'stock', 'device', 'category'):
        val = str(values.get(key) or '').strip()
        if val:
            data[key] = val
    if page:
        try:
            page_no = int(page)
        except (TypeError, ValueError):
            page_no = 1
        if page_no > 1:
            data['page'] = str(page_no)
    encoded = urlencode(data)
    return f'?{encoded}' if encoded else '?'


def _stock_list_context(request: HttpRequest, error='', stock_modal=''):
    query = str(request.GET.get('q', '')).strip()
    stock = str(request.GET.get('stock', '')).strip()
    device = str(request.GET.get('device', '')).strip()
    category_slug = str(request.GET.get('category', '')).strip()
    category = None
    qs = Product.objects.select_related('category')
    scope = stock_scope(request.user)
    if scope is not None:
        qs = qs.filter(category__in=scope)
    tokens = [token for token in query.split() if token]
    for token in tokens:
        qs = qs.filter(q_search(token, 'name', 'sku', 'brand'))
    if category_slug == 'other':
        qs = qs.filter(category__isnull=True)
    elif category_slug:
        category = Category.objects.filter(slug=category_slug).first()
        if category:
            qs = qs.filter(category=category)
        else:
            qs = qs.none()
    else:
        category_slug = ''
    if stock == 'in':
        qs = qs.exclude(LOW_STOCK).filter(stock_qty__gt=0)
    elif stock == 'out':
        qs = qs.filter(LOW_STOCK)
    else:
        stock = ''
    if device in {Product.KIND_SPLIT, Product.KIND_MULTI_INDOOR, Product.KIND_MULTI_OUTDOOR}:
        qs = qs.filter(device_kind=device)
    else:
        device = ''
    qs = qs.annotate(
        stock_value=ExpressionWrapper(F('stock_qty') * F('buy_price'), output_field=MONEY_FIELD)
    ).order_by('sku')

    try:
        page = max(1, int(request.GET.get('page', '1')))
    except (TypeError, ValueError):
        page = 1
    paginator = Paginator(qs, STOCK_LIST_PAGE_SIZE)
    page_obj = paginator.get_page(page)

    filters = {'q': query, 'stock': stock, 'device': device, 'category': category_slug}
    page_links = []
    for num in paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1):
        if num == paginator.ELLIPSIS:
            page_links.append({'label': '…', 'href': '', 'on': False, 'gap': True})
        else:
            page_links.append({
                'label': str(num),
                'href': _stock_querystring(filters, page=num),
                'on': num == page_obj.number,
                'gap': False,
            })

    totals = qs.aggregate(
        product_count=Count('id'),
        qty_total=Coalesce(Sum('stock_qty'), QTY_ZERO),
        value_total=Coalesce(Sum('stock_value'), MONEY_ZERO),
        empty_count=Count('id', filter=LOW_STOCK),
    )
    has_filters = bool(query or stock or device or category_slug)
    if not page_obj.object_list:
        if category_slug and not category and category_slug != 'other':
            empty_copy = 'Bu kategori yok.'
        elif has_filters:
            empty_copy = 'Bu süzgeçte ürün yok.'
        else:
            empty_copy = 'Henüz ürün yok. Yeni ürün ile ilk kartı açın.'
    else:
        empty_copy = ''
    if category:
        category_name = category.name
    elif category_slug == 'other':
        category_name = 'Diğer'
    else:
        category_name = ''

    return {
        'products': page_obj.object_list,
        'catalog': qs.order_by('sku'),
        'page_obj': page_obj,
        'paginator': paginator,
        'page_links': page_links,
        'prev_href': _stock_querystring(filters, page=page_obj.previous_page_number()) if page_obj.has_previous() else '',
        'next_href': _stock_querystring(filters, page=page_obj.next_page_number()) if page_obj.has_next() else '',
        'query': query,
        'stock': stock,
        'device': device,
        'category': category_slug,
        'category_is_klima': bool(category and category.is_klima),
        'category_id': category.pk if category else '',
        'category_name': category_name,
        'product_count': totals['product_count'] or 0,
        'qty_total': totals['qty_total'] or Decimal('0.00'),
        'value_total': totals['value_total'] or Decimal('0.00'),
        'empty_count': totals['empty_count'] or 0,
        'empty_copy': empty_copy,
        'error': error,
        'stock_modal': stock_modal,
        'show_list': bool(category_slug),
        'next_sku': next_sku(prefix_for(category)),
        'setting_cat': (
            {
                'id': str(category.pk),
                'name': category.name,
                'prefix': category.sku_prefix,
                'brand': category.brand,
                'is_klima': bool(category.is_klima),
                'is_copper_pipe': bool(category.is_copper_pipe),
                'included_copper_meters': (
                    ''
                    if not category.included_copper_meters
                    else format(category.included_copper_meters.normalize(), 'f').rstrip('0').rstrip('.')
                ),
                'slug': category.slug,
                'locked': category.products.exists(),
            }
            if category and getattr(request.user, 'can_stock_manage', False)
            else None
        ),
        'can_stock_manage': getattr(request.user, 'can_stock_manage', False),
    }


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD, Customer.ROLE_SERVICE)
@require_http_methods(['GET', 'POST'])
def stock_home(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET' and _wants_json(request):
        return product_search_json(request)
    slug = str(request.GET.get('category', '')).strip()
    if slug and slug != 'other':
        category = Category.objects.filter(slug=slug).first()
        if not can_access_category(request.user, category):
            return redirect('portal-stock')
    error = ''
    stock_modal = ''
    if request.method == 'POST':
        action = str(request.POST.get('action', '')).strip()
        try:
            if not getattr(request.user, 'can_stock_manage', False):
                raise ValueError('Bu işlem için yetkiniz yok.')
            if action == 'product':
                product = _create_product(request)
                text = queue_toast(request, 'Ürün eklendi.')
                if _wants_json(request):
                    payload = _product_payload(product)
                    payload['next_sku'] = next_sku(prefix_for(product.category))
                    payload['toast'] = text
                    return JsonResponse(payload)
            elif action == 'category':
                cat_id = str(request.POST.get('id', '')).strip()
                if cat_id:
                    item = update_category(
                        item=Category.objects.get(pk=cat_id),
                        name=str(request.POST.get('name', '')).strip(),
                        prefix=request.POST.get('sku_prefix', ''),
                        brand=request.POST.get('brand', ''),
                        is_klima=_parse_klima_flag(request.POST.get('is_klima')),
                        is_copper_pipe=_parse_copper_flag(request.POST.get('is_copper_pipe')),
                        included_copper_meters=request.POST.get('included_copper_meters', ''),
                    )
                    text = queue_toast(request, 'Kategori güncellendi.')
                else:
                    item = create_category(
                        name=str(request.POST.get('name', '')).strip(),
                        prefix=request.POST.get('sku_prefix', ''),
                        brand=request.POST.get('brand', ''),
                        is_klima=_parse_klima_flag(request.POST.get('is_klima')),
                        is_copper_pipe=_parse_copper_flag(request.POST.get('is_copper_pipe')),
                        included_copper_meters=request.POST.get('included_copper_meters', ''),
                        user=request.user,
                    )
                    text = queue_toast(request, 'Kategori eklendi.')
                if _wants_json(request):
                    return JsonResponse(_category_payload(item, toast=text))
            elif action == 'delete_category':
                cat_id = str(request.POST.get('id', '')).strip()
                if not cat_id:
                    raise ValueError('Kategori seçin.')
                item = Category.objects.get(pk=cat_id)
                delete_category(item=item)
                text = queue_toast(request, 'Kategori silindi.')
                if _wants_json(request):
                    return JsonResponse({'ok': True, 'toast': text, 'deleted': True, 'url': reverse('portal-stock')})
            elif action == 'in':
                product = Product.objects.get(pk=request.POST.get('product_id'))
                _stock_in(request, product)
                text = queue_toast(request, 'Stok girişi kaydedildi.')
                if _wants_json(request):
                    payload = _product_payload(product)
                    payload['toast'] = text
                    return JsonResponse(payload)
            else:
                error = 'Bilinmeyen işlem.'
        except IntegrityError:
            error = 'Bu kategori veya önek zaten var.' if action == 'category' else 'Bu stok kodu zaten var.'
        except (ValueError, StockError, Product.DoesNotExist, Category.DoesNotExist, Party.DoesNotExist) as exc:
            error = str(exc)
        if error:
            if action == 'in':
                stock_modal = 'in'
            elif action in {'category', 'delete_category'}:
                stock_modal = 'category'
            else:
                stock_modal = 'product'
            if _wants_json(request):
                return JsonResponse({'ok': False, 'error': error}, status=400)
        elif not _wants_json(request):
            if action == 'category':
                return redirect(f"{reverse('portal-stock')}?category={item.slug}")
            return redirect('portal-stock')
    return render(
        request,
        'portal/stock.html',
        _ctx(**_stock_list_context(request, error=error, stock_modal=stock_modal)),
    )


def _stock_back_href(category=None, slug=''):
    slug = str(slug or (category.slug if category else '')).strip()
    if slug:
        return f"{reverse('portal-stock')}?category={slug}"
    return reverse('portal-stock')


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD)
@require_http_methods(['GET', 'POST'])
def product_new(request: HttpRequest) -> HttpResponse:
    error = ''
    posted = request.POST if request.method == 'POST' else None
    category = None
    if posted:
        raw = str(posted.get('category_id', '')).strip()
        if raw:
            category = Category.objects.filter(pk=raw).first()
    if category is None:
        slug = str(request.GET.get('category', '')).strip()
        if slug and slug != 'other':
            category = Category.objects.filter(slug=slug).first()
    if request.method == 'POST':
        try:
            product = _create_product(request)
            queue_toast(request, 'Ürün eklendi.')
            return redirect(product.get_absolute_url())
        except IntegrityError:
            error = 'Bu stok kodu zaten var.'
        except (ValueError, StockError, Category.DoesNotExist) as exc:
            error = str(exc)
    if category is None:
        category = default_category(request.user)
    sku_map = _sku_map()
    next_code = sku_map.get(str(category.pk), next_sku(prefix_for(category)))
    cat_choices = _category_choices()
    return render(
        request,
        'portal/stock_new.html',
        _ctx(
            error=error,
            next_sku=next_code,
            sku_map=sku_map,
            cat_choices=cat_choices,
            form_brand=pretty_label(posted.get('brand', '')) if posted else '',
            form_name=posted.get('name', '') if posted else '',
            form_unit=tr_upper(posted.get('unit', '')) or 'ADET' if posted else 'ADET',
            form_buy=posted.get('buy_price', '') if posted else '',
            form_sale=posted.get('sale_price', '') if posted else '',
            form_vat=posted.get('vat_rate', '') if posted else '20',
            form_qty=posted.get('qty', '') if posted else '',
            form_alert=posted.get('alert_qty', '') if posted else '',
            form_alert_on=bool(posted and str(posted.get('alert_on', '')).strip() in ('1', 'on', 'true')),
            form_device_kind=str(posted.get('device_kind', '')).strip() if posted else '',
            form_outdoor_name=tr_upper(posted.get('outdoor_name', '')) if posted else '',
            form_tracks_serial=(
                str(posted.get('tracks_serial', '')).strip() in ('1', 'on', 'true', 'yes')
                if posted
                else bool(category.is_klima)
            ),
            category_is_klima=bool(category.is_klima),
            form_note=posted.get('note', '') if posted else '',
            category_id=category.pk,
            category_label=f'{category.name} · {category.sku_prefix}',
            back_href=_stock_back_href(category, str(request.GET.get('category', '')).strip()),
        ),
    )


@role_required(Customer.ROLE_SALES, Customer.ROLE_SERVICE_LEAD, Customer.ROLE_SERVICE)
@require_http_methods(['GET', 'POST'])
def product_item(request: HttpRequest, number: str) -> HttpResponse:
    product = get_object_or_404(Product.objects.select_related('category', 'outdoor'), sku=number)
    if not can_access_category(request.user, product.category):
        return redirect('portal-stock')
    error = ''
    stock_modal = ''
    if request.method == 'POST':
        action = str(request.POST.get('action', '')).strip()
        try:
            if not getattr(request.user, 'can_stock_manage', False):
                raise ValueError('Bu işlem için yetkiniz yok.')
            if action == 'in':
                _stock_in(request, product)
                text = queue_toast(request, 'Stok girişi kaydedildi.')
                if _wants_json(request):
                    payload = _product_payload(product)
                    payload['toast'] = text
                    return JsonResponse(payload)
                return redirect(product.get_absolute_url())
            if action == 'alert':
                product.alert_qty = parse_alert_qty(request.POST.get('alert_qty', ''))
                product.alert_on = str(request.POST.get('alert_on', '')).strip() in ('1', 'on', 'true')
                product.save(update_fields=['alert_qty', 'alert_on', 'updated_at'])
                queue_toast(request, 'Kritik eşik kaydedildi.')
                return redirect(product.get_absolute_url())
            if action == 'device':
                apply_device_fields(product, request.POST)
                product.save(update_fields=['is_device', 'device_kind', 'outdoor', 'outdoor_name', 'updated_at'])
                queue_toast(request, 'Cihaz kaydedildi.')
                return redirect(product.get_absolute_url())
            if action == 'save':
                update_product(product=product, post=request.POST)
                text = queue_toast(request, 'Ürün kartı güncellendi.')
                if _wants_json(request):
                    payload = _product_payload(product)
                    payload['toast'] = text
                    return JsonResponse(payload)
                return redirect(product.get_absolute_url())
            error = 'Bilinmeyen işlem.'
        except (ValueError, StockError, Party.DoesNotExist) as exc:
            error = str(exc)
        if error:
            if action == 'alert':
                stock_modal = 'alert'
            elif action == 'in':
                stock_modal = 'in'
            elif action in {'save', 'device'}:
                stock_modal = 'edit'
            if _wants_json(request):
                return JsonResponse({'ok': False, 'error': error}, status=400)
    last_buy = (
        product.movements.filter(reason=StockMovement.REASON_IN)
        .select_related('supplier')
        .first()
    )
    return render(
        request,
        'portal/stock_item.html',
        _ctx(
            product=product,
            movements=product.movements.select_related(
                'supplier', 'created_by', 'sale_line', 'sale_line__sale', 'job'
            ),
            last_buy=last_buy,
            error=error,
            stock_modal=stock_modal,
            back_href=_stock_back_href(product.category),
            can_stock_manage=getattr(request.user, 'can_stock_manage', False),
        ),
    )
