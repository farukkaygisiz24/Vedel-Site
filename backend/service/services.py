import io
import re
import zipfile
from calendar import monthrange
from datetime import date, time, timedelta
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal
from itertools import groupby
from pathlib import Path

from django.db import IntegrityError, transaction
from django.db.models import Q, prefetch_related_objects
from django.http import FileResponse, Http404
from django.utils import timezone

from sales.models import Sale, SaleLine
from sales.services import line_amounts, money, parse_decimal, tr_upper
from stock.models import Product, StockMovement
from stock.services import MOUNT_CATEGORY_SLUG, SERVICE_CATEGORY_SLUG, StockError, apply_movement

from .models import Device, Job, JobLine, JobPhoto, JobSoldPack, JobSoldUnit, JobSoldUnitMaterial, JobSoldUnitPhoto

TWOPLACES = Decimal('0.01')
DAY_CAP = 4
SERVICE_HOURS = [time(hour, 0) for hour in range(8, 19)]
SERVICE_HOUR_LABELS = [item.strftime('%H:%M') for item in SERVICE_HOURS]
UNIT_PHOTO_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.heic'}
UNIT_PHOTO_MAX = 8 * 1024 * 1024
MAX_MULTI_INDOOR = 7
MOUNT_PHOTO_MIN = 4


def parse_year_month(raw, fallback: date | None = None) -> tuple[int, int]:
    when = fallback or timezone.localdate()
    text = str(raw or '').strip()
    if text:
        try:
            parts = text.split('-')
            year, month = int(parts[0]), int(parts[1])
            if 1 <= month <= 12 and 2000 <= year <= 2100:
                return year, month
        except (TypeError, ValueError, IndexError):
            pass
    return when.year, when.month


def _job_slot(job: Job) -> dict:
    return {
        'time': job.time.strftime('%H:%M') if job.time else '',
        'party': job.party.display_name,
        'number': job.display_number,
        'kind': job.kind_label,
        'pending': job.status == Job.STATUS_PENDING,
    }


def month_jobs(year: int, month: int, qs=None) -> dict[str, list[dict]]:
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    source = qs if qs is not None else Job.objects.all()
    rows = (
        source.filter(
            date__gte=start,
            date__lte=end,
            status__in=[Job.STATUS_OPEN, Job.STATUS_PENDING],
        )
        .select_related('party', 'sale')
        .order_by('date', 'time', 'id')
    )
    days: dict[str, list[dict]] = {}
    for job in rows:
        days.setdefault(job.date.isoformat(), []).append(_job_slot(job))
    return days


def month_load(year: int, month: int) -> dict[str, int]:
    return {key: len(items) for key, items in month_jobs(year, month).items()}


def parse_service_time(raw) -> time:
    text = str(raw or '').strip()
    if not text:
        raise ValueError('Servis saati seçin.')
    try:
        parts = text.split(':')
        hour, minute = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
        clock = time(hour, minute)
    except (TypeError, ValueError) as exc:
        raise ValueError('Servis saati geçersiz.') from exc
    if clock not in SERVICE_HOURS:
        raise ValueError('Servis saati 08:00–18:00 arası tam saat olmalı.')
    return clock


def month_load_payload(year: int, month: int, qs=None) -> dict:
    jobs = month_jobs(year, month, qs=qs)
    return {
        'ok': True,
        'month': f'{year:04d}-{month:02d}',
        'cap': DAY_CAP,
        'days': {key: len(items) for key, items in jobs.items()},
        'jobs': jobs,
    }


def compact_job_number(number: str) -> str:
    return re.sub(r'[^A-Za-z0-9]', '', str(number or '')).upper()


def next_job_number(when: date) -> str:
    prefix = f'SRV{when.year}'
    serial = 0
    for number in Job.objects.filter(number__startswith=prefix).values_list('number', flat=True):
        compact = compact_job_number(number)
        if compact.startswith(prefix) and compact[len(prefix):].isdigit():
            serial = max(serial, int(compact[len(prefix):]))
    return f'{prefix}{serial + 1:04d}'


def week_start(when: date) -> date:
    return when - timedelta(days=when.weekday())


def add_months(when: date, months: int) -> date:
    month = when.month - 1 + int(months)
    year = when.year + month // 12
    month = month % 12 + 1
    day = min(when.day, monthrange(year, month)[1])
    return date(year, month, day)


DEFAULT_CARE_INTERVAL = 12


def parse_interval(raw) -> int:
    try:
        months = int(str(raw or '').strip() or str(DEFAULT_CARE_INTERVAL))
    except (TypeError, ValueError) as exc:
        raise ValueError('Bakım aralığı seçin.') from exc
    if months not in {3, 6, 9, 12}:
        raise ValueError('Bakım aralığı 3, 6, 9 veya 12 ay olmalıdır.')
    return months


def _parse_job_date(post) -> date:
    raw = str(post.get('date', '')).strip()
    try:
        return date.fromisoformat(raw) if raw else timezone.localdate()
    except ValueError as exc:
        raise ValueError('Tarih geçersiz.') from exc


def _parse_job_lines(post, vat_mode: str) -> list[dict]:
    kinds = post.getlist('kind')
    product_ids = post.getlist('product_id')
    descriptions = post.getlist('description')
    qtys = post.getlist('qty')
    prices = post.getlist('unit_price')
    costs = post.getlist('cost_price')
    vat_rates = post.getlist('vat_rate')
    parsed = []
    count = max(len(kinds), len(product_ids), len(descriptions), len(qtys), len(prices))
    for index in range(count):
        kind = str(kinds[index] if index < len(kinds) else '').strip() or JobLine.KIND_LABOR
        if kind not in {JobLine.KIND_LABOR, JobLine.KIND_PART}:
            raise ValueError('Kalem türü seçin.')
        qty_raw = qtys[index] if index < len(qtys) else ''
        price_raw = prices[index] if index < len(prices) else ''
        desc = tr_upper(descriptions[index] if index < len(descriptions) else '')
        product_id = str(product_ids[index] if index < len(product_ids) else '').strip()
        if kind == JobLine.KIND_LABOR:
            if not desc and not str(price_raw).strip():
                continue
            if not desc:
                raise ValueError('İşçilik açıklaması zorunlu.')
            product = None
            if product_id:
                product = (
                    Product.objects.select_related('category')
                    .filter(pk=product_id, is_active=True)
                    .first()
                )
            cost_price = Decimal('0.00')
        else:
            if not product_id and not str(qty_raw).strip() and not str(price_raw).strip():
                continue
            if not product_id:
                raise ValueError('Parça için stok seçin.')
            product = Product.objects.select_for_update().select_related('category').get(
                pk=product_id,
                is_active=True,
            )
            if not desc:
                desc = product.display_name
            cost_raw = costs[index] if index < len(costs) else ''
            if str(cost_raw).strip():
                cost_price = parse_decimal(cost_raw, 'Alış fiyatı')
            else:
                cost_price = product.buy_price or Decimal('0.00')
            if cost_price < 0:
                raise ValueError('Alış fiyatı negatif olamaz.')
        qty = parse_decimal(qty_raw or '1', 'Adet')
        if str(price_raw).strip():
            price = parse_decimal(price_raw, 'Birim fiyat')
        elif product is not None:
            price = product.sale_price or Decimal('0.00')
        else:
            price = Decimal('0.00')
        if qty <= 0:
            raise ValueError('Adet sıfırdan büyük olmalı.')
        if price < 0:
            raise ValueError('Birim fiyat negatif olamaz.')
        if product:
            vat_rate = (
                parse_decimal(vat_rates[index], 'KDV')
                if index < len(vat_rates) and str(vat_rates[index]).strip()
                else product.vat_rate
            )
        else:
            vat_rate = (
                parse_decimal(vat_rates[index], 'KDV')
                if index < len(vat_rates) and str(vat_rates[index]).strip()
                else Decimal('20.00')
            )
        if vat_mode == Job.VAT_NONE:
            vat_rate = Decimal('0.00')
        elif vat_rate <= 0:
            vat_rate = Decimal('20.00')
        net, vat, total = line_amounts(qty, price, vat_rate, vat_mode)
        parsed.append(
            {
                'kind': kind,
                'product': product,
                'description': desc,
                'qty': qty,
                'unit_price': price,
                'cost_price': money(cost_price),
                'vat_rate': vat_rate,
                'net': net,
                'vat': vat,
                'total': total,
            }
        )
    if not parsed:
        raise ValueError('En az bir kalem ekleyin.')
    return parsed


def _reject_klima_parts(parsed_lines: list[dict]) -> None:
    for item in parsed_lines:
        if item['kind'] != JobLine.KIND_PART:
            continue
        product = item.get('product')
        category = getattr(product, 'category', None) if product else None
        if product is None or product.is_device or (category is not None and category.is_klima):
            raise ValueError('Servis malzemesi bulunamadı.')


def _replace_lines(job: Job, parsed_lines: list[dict]) -> None:
    job.lines.all().delete()
    for item in parsed_lines:
        _create_job_line(job, item)
    _recompute_job_totals(job)


def _create_job_line(job: Job, item: dict) -> JobLine:
    return JobLine.objects.create(
        job=job,
        kind=item['kind'],
        product=item['product'],
        description=item['description'],
        qty=item['qty'],
        unit_price=item['unit_price'],
        cost_price=item['cost_price'],
        vat_rate=item['vat_rate'],
        line_net=item['net'],
        line_vat=item['vat'],
        line_total=item['total'],
    )


def _replace_field_service_parts(job: Job, parsed_lines: list[dict]) -> None:
    parts = [item for item in parsed_lines if item['kind'] == JobLine.KIND_PART]
    job.lines.filter(kind=JobLine.KIND_PART).delete()
    for item in parts:
        _create_job_line(job, item)
    _recompute_job_totals(job)


def _seed_service_labor(job: Job, work_id) -> None:
    if job.sale_id:
        return
    raw = str(work_id or '').strip()
    if not raw:
        return
    if not raw.isdigit():
        raise ValueError('İş seçimi geçersiz.')
    product = (
        Product.objects.filter(
            pk=int(raw),
            is_active=True,
            category__slug=SERVICE_CATEGORY_SLUG,
        )
        .select_related('category')
        .first()
    )
    if not product:
        raise ValueError('İş kartı bulunamadı.')
    existing = job.lines.filter(kind=JobLine.KIND_LABOR, product=product).first()
    if existing:
        return
    job.lines.filter(kind=JobLine.KIND_LABOR, product__category__slug=SERVICE_CATEGORY_SLUG).delete()
    qty = Decimal('1.00')
    price = product.sale_price or Decimal('0.00')
    vat_rate = Decimal('0.00') if job.vat_mode == Job.VAT_NONE else product.vat_rate
    net, vat, total = line_amounts(qty, price, vat_rate, job.vat_mode)
    _create_job_line(
        job,
        {
            'kind': JobLine.KIND_LABOR,
            'product': product,
            'description': product.display_name,
            'qty': qty,
            'unit_price': price,
            'cost_price': money(product.buy_price or Decimal('0.00')),
            'vat_rate': vat_rate,
            'net': net,
            'vat': vat,
            'total': total,
        },
    )
    _recompute_job_totals(job)


def _recompute_job_totals(job: Job) -> None:
    lines = list(job.lines.all())
    job.subtotal = money(sum((item.line_net for item in lines), Decimal('0')))
    job.vat_total = money(sum((item.line_vat for item in lines), Decimal('0')))
    job.grand_total = money(sum((item.line_total for item in lines), Decimal('0')))
    job.cost_total = money(sum((item.cost_price * item.qty for item in lines), Decimal('0')))


def _clean_pk(raw) -> str:
    text = str(raw or '').strip()
    if not text or text in {'None', 'null', 'undefined'}:
        return ''
    return text


def _sold_device_name(unit: JobSoldUnit) -> str:
    brand = tr_upper(unit.brand or '')
    model = tr_upper(unit.model or '')
    if brand in {'', '—'}:
        brand = ''
    if model in {'', '—'}:
        model = ''
    if brand and model:
        return f'{brand} {model}'
    return model or brand or 'CİHAZ'


def _sold_interval(unit: JobSoldUnit) -> int:
    try:
        months = int(unit.interval_months or DEFAULT_CARE_INTERVAL)
    except (TypeError, ValueError):
        months = 6
    return months if months in {3, 6, 9, 12} else 6


def _device_choice_payload(device: Device) -> dict:
    return {
        'id': str(device.pk),
        'name': device.name,
        'place': device.place,
        'serial': '',
        'source': '',
        'interval': device.interval_months,
        'interval_label': device.get_interval_months_display(),
        'last_serviced_on': device.last_serviced_on.isoformat() if device.last_serviced_on else '',
        'next_due': device.next_due.isoformat() if device.next_due else '',
    }


def _sold_choice_payload(unit: JobSoldUnit) -> dict:
    job_no = unit.job.number if getattr(unit, 'job', None) else ''
    return {
        'id': f'sold-{unit.pk}',
        'name': _sold_device_name(unit),
        'place': tr_upper(unit.room or ''),
        'serial': tr_upper(unit.serial or ''),
        'source': job_no,
        'interval': _sold_interval(unit),
        'interval_label': unit.get_interval_months_display(),
        'last_serviced_on': unit.last_serviced_on.isoformat() if unit.last_serviced_on else '',
        'next_due': unit.next_due.isoformat() if unit.next_due else '',
    }


def party_device_choices(party) -> list[dict]:
    units = list(
        JobSoldUnit.objects.filter(job__party=party)
        .select_related('product', 'job')
        .order_by('id')
    )
    rows = [_sold_choice_payload(unit) for unit in units]
    taken = {(item['name'].casefold(), (item['place'] or '').casefold()) for item in rows}
    for item in Device.objects.filter(party=party):
        key = (item.name.casefold(), (item.place or '').casefold())
        if key in taken:
            continue
        rows.append(_device_choice_payload(item))
    return rows


def _mount_place_from_job(job: Job | None) -> str:
    sale = getattr(job, 'sale', None) if job is not None else None
    if sale is None:
        return ''
    summary = (getattr(sale, 'mount_place_summary', None) or '').strip()
    if not summary:
        return ''
    return tr_upper(summary)[:160]


def device_from_sold_unit(*, party, unit: JobSoldUnit, user, job: Job | None = None) -> Device:
    name = _sold_device_name(unit)
    place = _mount_place_from_job(job) or tr_upper(unit.room or '')
    found = Device.objects.filter(party=party, name=name, place=place).first()
    if found:
        return found
    return Device.objects.create(
        party=party,
        name=name,
        place=place,
        interval_months=_sold_interval(unit),
        last_serviced_on=unit.last_serviced_on,
        next_due=unit.next_due,
        created_by=user,
    )


def _pack_interval(pack: JobSoldPack) -> int:
    try:
        months = int(pack.interval_months or DEFAULT_CARE_INTERVAL)
    except (TypeError, ValueError):
        months = 6
    return months if months in {3, 6, 9, 12} else 6


def device_from_sold_pack(*, party, pack: JobSoldPack, user, serviced_on=None, job: Job | None = None) -> Device:
    name = tr_upper((pack.label or '').strip() or 'CİHAZ')
    serial = tr_upper(pack.outdoor_serial or '')
    if serial and serial not in name:
        name = f'{name} · {serial}'
    name = name[:160]
    indoor = pack.units.order_by('id').first()
    place = _mount_place_from_job(job) or tr_upper((indoor.room if indoor else '') or '')
    interval = _pack_interval(pack)
    next_due = add_months(serviced_on, interval) if serviced_on else None
    found = Device.objects.filter(party=party, name=name, place=place).first()
    if found:
        found.last_serviced_on = serviced_on
        found.interval_months = interval
        found.next_due = next_due
        found.save(update_fields=['last_serviced_on', 'interval_months', 'next_due', 'updated_at'])
        return found
    return Device.objects.create(
        party=party,
        name=name,
        place=place,
        interval_months=interval,
        last_serviced_on=serviced_on,
        next_due=next_due,
        created_by=user,
    )


def devices_from_sold_packs(*, job: Job, user) -> list[Device]:
    created = []
    packs = job.sold_packs.prefetch_related('units').order_by('sort', 'id')
    for pack in packs:
        created.append(
            device_from_sold_pack(
                party=job.party,
                pack=pack,
                user=user,
                serviced_on=job.date,
                job=job,
            )
        )
    return created


def _resolve_device(*, party, post, user, current: Device | None = None) -> Device | None:
    mode = str(post.get('device_mode', '')).strip()
    if mode == 'none':
        return None
    if mode == 'new':
        raise ValueError('Yeni cihaz ofiste açılmaz.')
    raw = _clean_pk(post.get('device_id', ''))
    if raw:
        if raw.startswith('sold-'):
            unit_id = raw[5:]
            if not unit_id.isdigit():
                raise ValueError('Cihaz bulunamadı.')
            unit = JobSoldUnit.objects.filter(pk=int(unit_id), job__party=party).first()
            if not unit:
                raise ValueError('Cihaz bulunamadı.')
            return device_from_sold_unit(party=party, unit=unit, user=user, job=unit.job)
        if not raw.isdigit():
            raise ValueError('Cihaz bulunamadı.')
        device = Device.objects.filter(pk=int(raw), party=party).first()
        if not device:
            raise ValueError('Cihaz bulunamadı.')
        return device
    if current and current.party_id == party.pk:
        return current
    if mode == 'existing':
        raise ValueError('Kayıtlı cihaz seçin.')
    return None


ASSIGN_ALL = 'all'


def _resolve_assignee(post):
    from crew.models import CrewMember

    raw = _clean_pk(post.get('assignee_id', ''))
    if not raw or raw == ASSIGN_ALL:
        return None
    if not raw.isdigit():
        raise ValueError('Personel bulunamadı.')
    member = CrewMember.objects.filter(pk=int(raw), is_active=True).first()
    if not member:
        raise ValueError('Personel bulunamadı.')
    return member


def _resolve_assignment(post):
    raw = str(post.get('assignee_id', '')).strip()
    if raw == ASSIGN_ALL:
        return None, True
    return _resolve_assignee(post), False


def assignment_form_values(job: Job | None = None) -> tuple:
    if job and job.assignee_id:
        return job.assignee_id, job.assignee.display_name
    return ASSIGN_ALL, 'Hepsi'


def field_visible_q(member):
    return Q(assignee=member) | Q(assign_all=True, status=Job.STATUS_OPEN)


def _resolve_party(post, user):
    from sales.models import Party
    from sales.services import party_from_post

    party_id = _clean_pk(post.get('party_id', ''))
    party_mode = str(post.get('party_mode', 'existing' if party_id else 'new')).strip()
    if party_id or party_mode == 'existing':
        if not party_id:
            raise ValueError('Müşteri seçin.')
        return Party.objects.get(pk=party_id)
    return party_from_post(post, user)


def unit_count(qty) -> int:
    amount = Decimal(qty or 0)
    if amount <= 0:
        return 0
    return int(amount.to_integral_value(rounding=ROUND_CEILING))


def _product_outdoor_name(product) -> str:
    if not product:
        return ''
    if product.outdoor_id:
        name = (product.outdoor.name or '').strip()
        if name:
            return name
    return (product.outdoor_name or '').strip()


def _product_kind(product) -> str:
    if not product:
        return ''
    kind = str(getattr(product, 'device_kind', '') or '').strip()
    if kind in {
        Product.KIND_SPLIT,
        Product.KIND_MULTI_INDOOR,
        Product.KIND_MULTI_OUTDOOR,
    }:
        return kind
    return ''


def sale_line_is_device(line: SaleLine, sale: Sale | None = None) -> bool:
    product = line.product
    if not product:
        return False
    if _product_kind(product) or getattr(product, 'is_device', False):
        return True
    category = getattr(product, 'category', None)
    if category and category.slug == MOUNT_CATEGORY_SLUG:
        return False
    # Legacy klima kartları: bayrak yoksa cihaz satışında seri ister.
    if category and getattr(category, 'is_klima', False):
        sale = sale or getattr(line, 'sale', None)
        return bool(sale and sale.work_type == Sale.WORK_DEVICE)
    return False


def _line_role(line: SaleLine, sale: Sale | None = None) -> str:
    kind = _product_kind(line.product)
    if kind:
        return kind
    if sale_line_is_device(line, sale):
        return Product.KIND_MULTI_INDOOR
    return ''


def _line_device_fields(line: SaleLine) -> tuple[str, str, str]:
    product = line.product
    if product:
        brand = (product.brand or '').strip() or '—'
        model = (product.name or '').strip() or '—'
    else:
        brand = '—'
        model = (line.description or '').strip() or 'Kalem'
    return brand, model, _product_outdoor_name(product)


def ensure_sold_packs(job: Job) -> list[JobSoldPack]:
    if not job.sale_id:
        return []
    sale = job.sale
    lines = list(sale.lines.select_related('product', 'product__outdoor', 'product__category'))
    wanted_packs: list[JobSoldPack] = []
    wanted_units: list[JobSoldUnit] = []
    sort = 0
    for line in lines:
        role = _line_role(line, sale)
        if not role:
            continue
        count = unit_count(line.qty)
        brand, model, outdoor = _line_device_fields(line)
        if role == Product.KIND_SPLIT:
            for index in range(count):
                key = f's:{line.pk}:{index}'
                pack, created = JobSoldPack.objects.get_or_create(
                    job=job,
                    source_key=key,
                    defaults={
                        'kind': JobSoldPack.KIND_SPLIT,
                        'sort': sort,
                        'outdoor_name': outdoor,
                    },
                )
                if not created and (
                    pack.kind != JobSoldPack.KIND_SPLIT
                    or pack.outdoor_name != outdoor
                    or pack.sort != sort
                ):
                    pack.kind = JobSoldPack.KIND_SPLIT
                    pack.outdoor_name = outdoor
                    pack.sort = sort
                    pack.save(update_fields=['kind', 'outdoor_name', 'sort'])
                unit, _created = JobSoldUnit.objects.get_or_create(
                    job=job,
                    sale_line=line,
                    line_index=index,
                    defaults={
                        'product': line.product,
                        'brand': brand,
                        'model': model,
                        'outdoor_name': outdoor,
                        'pack': pack,
                    },
                )
                updates = []
                if unit.pack_id != pack.pk:
                    unit.pack = pack
                    updates.append('pack')
                if unit.brand != brand or unit.model != model or unit.outdoor_name != outdoor:
                    unit.brand = brand
                    unit.model = model
                    unit.outdoor_name = outdoor
                    unit.product = line.product
                    updates.extend(['brand', 'model', 'outdoor_name', 'product'])
                if updates:
                    unit.save(update_fields=list(dict.fromkeys(updates)))
                wanted_packs.append(pack)
                wanted_units.append(unit)
                sort += 1
        elif role == Product.KIND_MULTI_OUTDOOR:
            for index in range(count):
                key = f'o:{line.pk}:{index}'
                pack, created = JobSoldPack.objects.get_or_create(
                    job=job,
                    source_key=key,
                    defaults={
                        'kind': JobSoldPack.KIND_MULTI,
                        'sort': sort,
                        'outdoor_sale_line': line,
                        'outdoor_product': line.product,
                        'outdoor_name': model,
                        'outdoor_index': index,
                    },
                )
                if not created:
                    fields = []
                    if pack.outdoor_name != model:
                        pack.outdoor_name = model
                        fields.append('outdoor_name')
                    if pack.outdoor_product_id != line.product_id:
                        pack.outdoor_product = line.product
                        fields.append('outdoor_product')
                    if pack.sort != sort:
                        pack.sort = sort
                        fields.append('sort')
                    if fields:
                        pack.save(update_fields=fields)
                wanted_packs.append(pack)
                sort += 1
        else:
            for index in range(count):
                unit, _created = JobSoldUnit.objects.get_or_create(
                    job=job,
                    sale_line=line,
                    line_index=index,
                    defaults={
                        'product': line.product,
                        'brand': brand,
                        'model': model,
                        'outdoor_name': '',
                    },
                )
                updates = []
                if unit.brand != brand or unit.model != model:
                    unit.brand = brand
                    unit.model = model
                    unit.product = line.product
                    unit.outdoor_name = ''
                    updates.extend(['brand', 'model', 'product', 'outdoor_name'])
                if updates:
                    unit.save(update_fields=updates)
                wanted_units.append(unit)
    extras_packs = JobSoldPack.objects.filter(job=job)
    if wanted_packs:
        extras_packs = extras_packs.exclude(pk__in=[item.pk for item in wanted_packs])
    for extra in extras_packs:
        extra.delete()
    extras_units = JobSoldUnit.objects.filter(job=job)
    if wanted_units:
        extras_units = extras_units.exclude(pk__in=[item.pk for item in wanted_units])
    for extra in extras_units:
        extra.delete()
    return list(JobSoldPack.objects.filter(job=job).order_by('sort', 'id'))


def ensure_sold_units(job: Job) -> list[JobSoldUnit]:
    ensure_sold_packs(job)
    return list(JobSoldUnit.objects.filter(job=job).order_by('id'))


def sold_unit_groups(job: Job) -> list[dict]:
    packs = ensure_sold_packs(job)
    if packs:
        prefetch_related_objects(packs, 'units', 'photos', 'materials__product', 'outdoor_product')
    groups = []
    for pack in packs:
        units = list(pack.units.order_by('id'))
        groups.append(
            {
                'pack': pack,
                'brand': pack.label,
                'kind': pack.kind,
                'units': units,
            }
        )
    return groups


def unassigned_sold_units(job: Job) -> list[JobSoldUnit]:
    return list(
        JobSoldUnit.objects.filter(job=job, pack__isnull=True).select_related('product').order_by('id')
    )


def party_sold_unit_groups(party) -> list[dict]:
    packs = list(
        JobSoldPack.objects.filter(job__party=party)
        .select_related('job', 'job__party', 'job__sale', 'outdoor_product')
        .prefetch_related('units', 'photos', 'materials__product')
        .order_by('job_id', 'sort', 'id')
    )
    groups = []
    for pack in packs:
        units = list(pack.units.all())
        if pack.kind == JobSoldPack.KIND_MULTI and not units:
            continue
        groups.append(
            {
                'pack': pack,
                'brand': pack.label,
                'kind': pack.kind,
                'units': units,
            }
        )
    return groups


CARE_MONTHS = {3, 6, 9, 12}


def _parse_unit_care(post, pk, prefix: str) -> dict:
    raw_interval = str(post.get(f'unit_{prefix}interval_{pk}', '')).strip()
    try:
        interval = int(raw_interval or str(DEFAULT_CARE_INTERVAL))
    except (TypeError, ValueError):
        interval = DEFAULT_CARE_INTERVAL
    if interval not in CARE_MONTHS:
        interval = DEFAULT_CARE_INTERVAL
    raw_last = str(post.get(f'unit_{prefix}last_{pk}', '')).strip()
    last = None
    if raw_last:
        try:
            last = date.fromisoformat(raw_last)
        except ValueError as exc:
            raise ValueError('Bakım tarihi geçersiz.') from exc
    nxt = add_months(last, interval) if last else None
    return {'interval': interval, 'last': last, 'next': nxt}


def _parse_unit_photo(upload):
    if not upload or not getattr(upload, 'size', 0):
        return None
    if upload.size > UNIT_PHOTO_MAX:
        raise ValueError('Cihaz görseli en fazla 8 MB olabilir.')
    name = Path(str(upload.name or '')).name
    ext = Path(name).suffix.lower()
    if ext not in UNIT_PHOTO_EXTS:
        raise ValueError('Cihaz görseli JPG, PNG, WEBP veya HEIC olmalı.')
    return upload


def _parse_pack_care(post, pk) -> dict:
    raw_interval = str(post.get(f'pack_interval_{pk}', '')).strip()
    try:
        interval = int(raw_interval or str(DEFAULT_CARE_INTERVAL))
    except (TypeError, ValueError):
        interval = DEFAULT_CARE_INTERVAL
    if interval not in CARE_MONTHS:
        interval = DEFAULT_CARE_INTERVAL
    raw_last = str(post.get(f'pack_last_{pk}', '')).strip()
    last = None
    if raw_last:
        try:
            last = date.fromisoformat(raw_last)
        except ValueError as exc:
            raise ValueError('Bakım tarihi geçersiz.') from exc
    nxt = add_months(last, interval) if last else None
    return {'interval': interval, 'last': last, 'next': nxt}


def _validate_pack_assignment(job: Job) -> None:
    packs = list(job.sold_packs.prefetch_related('units'))
    multi_packs = [item for item in packs if item.kind == JobSoldPack.KIND_MULTI]
    if not multi_packs:
        return
    loose = JobSoldUnit.objects.filter(job=job, pack__isnull=True)
    if loose.exists():
        raise ValueError('Her iç üniteyi bir dış ünite grubuna bağlayın.')
    for pack in multi_packs:
        count = pack.units.count()
        if count < 1:
            raise ValueError('Her dış ünite grubuna en az bir iç ünite bağlayın.')
        if count > MAX_MULTI_INDOOR:
            raise ValueError(f'Bir dış üniteye en fazla {MAX_MULTI_INDOOR} iç ünite bağlanır.')


def apply_sale_pack_groups(job: Job, indoor_groups: list[str]) -> None:
    ensure_sold_packs(job)
    packs = list(
        JobSoldPack.objects.filter(job=job, kind=JobSoldPack.KIND_MULTI).order_by('sort', 'id')
    )
    units = list(JobSoldUnit.objects.filter(job=job, pack__isnull=True).order_by('id'))
    cleaned = [str(item or '').strip() for item in indoor_groups]
    if not packs or not any(cleaned):
        return
    if len(cleaned) != len(units):
        raise ValueError('Her iç üniteyi bir dış ünite grubuna bağlayın.')
    for unit, text in zip(units, cleaned):
        if not text.isdigit():
            raise ValueError('Her iç üniteyi bir dış ünite grubuna bağlayın.')
        index = int(text)
        if index < 0 or index >= len(packs):
            raise ValueError('Her iç üniteyi bir dış ünite grubuna bağlayın.')
        unit.pack = packs[index]
        unit.save(update_fields=['pack'])
    _validate_pack_assignment(job)


def apply_sold_units(*, job: Job, post, files=None, user=None, allow_negative=None):
    if allow_negative is None:
        allow_negative = bool(
            user is not None
            and getattr(user, 'can_service_field', False)
            and not getattr(user, 'can_service_lead', False)
        )
    packs = ensure_sold_packs(job)
    units = list(JobSoldUnit.objects.filter(job=job).order_by('id'))
    files = files or {}
    pack_map = {item.pk: item for item in packs}
    assignable = [unit for unit in units if f'indoor_pack_{unit.pk}' in post]
    if assignable:
        for unit in assignable:
            raw = str(post.get(f'indoor_pack_{unit.pk}', '')).strip()
            chosen = pack_map.get(int(raw)) if raw.isdigit() else None
            if chosen and chosen.kind != JobSoldPack.KIND_MULTI:
                chosen = None
            if unit.pack_id != (chosen.pk if chosen else None):
                unit.pack = chosen
                unit.save(update_fields=['pack'])
        _validate_pack_assignment(job)
    for unit in units:
        updates = []
        if f'unit_room_{unit.pk}' in post:
            room = tr_upper(post.get(f'unit_room_{unit.pk}', ''))
            if room != unit.room:
                unit.room = room
                updates.append('room')
        if f'unit_serial_{unit.pk}' in post:
            serial = tr_upper(post.get(f'unit_serial_{unit.pk}', ''))
            if serial != unit.serial:
                unit.serial = serial
                updates.append('serial')
        if updates:
            unit.save(update_fields=updates)
    for pack in packs:
        updates = []
        outdoor_key = f'pack_outdoor_serial_{pack.pk}'
        outdoor_alt = f'unit_outdoor_serial_{pack.pk}'
        if outdoor_key in post or outdoor_alt in post:
            outdoor_serial = tr_upper(post.get(outdoor_key, post.get(outdoor_alt, '')))
            if outdoor_serial != pack.outdoor_serial:
                pack.outdoor_serial = outdoor_serial
                updates.append('outdoor_serial')
        posted_care = f'pack_interval_{pack.pk}' in post or f'pack_last_{pack.pk}' in post
        if posted_care or allow_negative:
            care = _parse_pack_care(post, pack.pk)
            if care['last'] is None and allow_negative:
                care['last'] = job.date
                care['next'] = add_months(job.date, care['interval'])
            mapped = {
                'interval_months': care['interval'],
                'last_serviced_on': care['last'],
                'next_due': care['next'],
            }
            for field, value in mapped.items():
                if getattr(pack, field) != value:
                    setattr(pack, field, value)
                    updates.append(field)
        if updates:
            pack.save(update_fields=updates)
        if str(post.get('field_mat_present', '')).strip() != '1':
            _replace_pack_materials(pack, post, user=user)
        raw = []
        key = f'unit_photos_{pack.pk}'
        if hasattr(files, 'getlist'):
            raw = list(files.getlist(key))
        elif files.get(key):
            raw = [files.get(key)]
        sort = pack.photos.count()
        for item in raw:
            upload = _parse_unit_photo(item)
            if not upload:
                continue
            JobSoldUnitPhoto.objects.create(pack=pack, image=upload, sort=sort)
            sort += 1
    if str(post.get('field_mat_present', '')).strip() == '1':
        _apply_field_mount(job, packs, post, user=user)
    if user is not None:
        _sync_mount_stock(job=job, user=user, allow_negative=bool(allow_negative))


def _mount_posted(post, pk) -> bool:
    raw = post.get(f'unit_mat_present_{pk}') if post is not None else ''
    return str(raw or '').strip() == '1'


def _parse_unit_materials(post, pk) -> dict[int, Decimal]:
    ids = post.getlist(f'unit_mat_product_{pk}') if hasattr(post, 'getlist') else []
    qtys = post.getlist(f'unit_mat_qty_{pk}') if hasattr(post, 'getlist') else []
    merged: dict[int, Decimal] = {}
    for index, raw_id in enumerate(ids):
        if not str(raw_id).isdigit():
            continue
        raw_qty = qtys[index] if index < len(qtys) else '1'
        qty = parse_decimal(raw_qty or '1', 'Adet')
        if qty <= 0:
            raise ValueError('Montaj adedi pozitif olmalı.')
        product_id = int(raw_id)
        merged[product_id] = merged.get(product_id, Decimal('0.00')) + qty
    return merged


def _replace_pack_materials(pack: JobSoldPack, post, user=None) -> None:
    if not _mount_posted(post, pack.pk):
        return
    _set_pack_materials(pack, _parse_unit_materials(post, pack.pk), user=user)


def _parse_field_materials(post) -> dict[int, Decimal]:
    ids = post.getlist('field_mat_product') if hasattr(post, 'getlist') else []
    qtys = post.getlist('field_mat_qty') if hasattr(post, 'getlist') else []
    if not ids:
        raw = str(post.get('field_mat_product', '')).strip() if post is not None else ''
        if raw:
            ids = [raw]
            qtys = [str(post.get('field_mat_qty', '1'))]
    merged: dict[int, Decimal] = {}
    for index, raw_id in enumerate(ids):
        if not str(raw_id).isdigit():
            continue
        raw_qty = qtys[index] if index < len(qtys) else '1'
        qty = parse_decimal(raw_qty or '1', 'Adet')
        if qty <= 0:
            raise ValueError('Montaj adedi pozitif olmalı.')
        product_id = int(raw_id)
        merged[product_id] = merged.get(product_id, Decimal('0.00')) + qty
    return merged


def _apply_field_mount(job: Job, packs: list[JobSoldPack], post, user=None) -> None:
    wanted = _parse_field_materials(post)
    if not packs:
        if wanted:
            raise ValueError('Montaj için cihaz paketi yok.')
        return
    _set_pack_materials(packs[0], wanted, user=user)
    for pack in packs[1:]:
        _set_pack_materials(pack, {}, user=user)


def field_mount_payload(job: Job) -> list[dict]:
    merged: dict[int, dict] = {}
    order: list[int] = []
    rows = (
        JobSoldUnitMaterial.objects.filter(pack__job=job)
        .select_related('product')
        .order_by('id')
    )
    for item in rows:
        pid = item.product_id
        if pid not in merged:
            merged[pid] = {
                'product_id': pid,
                'name': item.name,
                'sku': item.product.sku if item.product_id else '',
                'unit': item.unit_label,
                'qty': Decimal('0.00'),
            }
            order.append(pid)
        merged[pid]['qty'] += item.qty
        if item.name:
            merged[pid]['name'] = item.name
    payload = []
    for pid in order:
        row = merged[pid]
        payload.append(
            {
                'product_id': row['product_id'],
                'name': row['name'],
                'sku': row['sku'],
                'unit': row['unit'],
                'qty': str(row['qty']).replace('.', ','),
            }
        )
    return payload


def _set_pack_materials(pack: JobSoldPack, wanted: dict[int, Decimal], user=None) -> None:
    products = {
        item.pk: item
        for item in Product.objects.filter(
            pk__in=wanted.keys(),
            is_active=True,
            is_device=False,
            category__slug=MOUNT_CATEGORY_SLUG,
        )
    }
    if user is not None and getattr(user, 'can_service_field', False) and not getattr(user, 'can_service_lead', False):
        allowed = set(user.stock_categories.values_list('pk', flat=True))
        products = {pk: item for pk, item in products.items() if item.category_id in allowed}
    missing = set(wanted) - set(products)
    if missing:
        raise ValueError('Montaj malzemesi bulunamadı.')
    existing = {item.product_id: item for item in pack.materials.all()}
    keep = set()
    for product_id, qty in wanted.items():
        product = products[product_id]
        name = product.display_name
        unit_label = product.unit or ''
        keep.add(product_id)
        row = existing.get(product_id)
        if row is None:
            JobSoldUnitMaterial.objects.create(
                pack=pack,
                product=product,
                qty=qty,
                name=name,
                unit_label=unit_label,
            )
            continue
        if row.qty != qty or row.name != name or row.unit_label != unit_label:
            row.qty = qty
            row.name = name
            row.unit_label = unit_label
            row.save(update_fields=['qty', 'name', 'unit_label'])
    for product_id, row in existing.items():
        if product_id not in keep:
            row.delete()


def _mount_note(job: Job) -> str:
    return f'{job.number} montaj'


def _mount_wanted_qty(job: Job) -> dict[int, Decimal]:
    wanted: dict[int, Decimal] = {}
    rows = JobSoldUnitMaterial.objects.filter(Q(pack__job=job) | Q(unit__job=job))
    for item in rows:
        wanted[item.product_id] = wanted.get(item.product_id, Decimal('0.00')) + item.qty
    return wanted


def _service_stock_note(job: Job) -> str:
    return f'{job.number} servis'


def _mount_movements(job: Job):
    return (
        StockMovement.objects.select_for_update()
        .filter(job=job, reason=StockMovement.REASON_JOB, note=_mount_note(job))
        .order_by('pk')
    )


@transaction.atomic
def _sync_mount_stock(*, job: Job, user, wanted: dict[int, Decimal] | None = None, allow_negative: bool = False) -> None:
    if wanted is None:
        wanted = _mount_wanted_qty(job)
    by_product: dict[int, list[StockMovement]] = {}
    for item in _mount_movements(job):
        by_product.setdefault(item.product_id, []).append(item)
    ids = set(wanted) | set(by_product)
    if not ids:
        return
    products = {
        item.pk: item
        for item in Product.objects.select_for_update().filter(pk__in=ids)
    }
    note = _mount_note(job)
    try:
        for product_id in ids:
            product = products.get(product_id)
            if product is None:
                raise ValueError('Montaj malzemesi bulunamadı.')
            want = wanted.get(product_id, Decimal('0.00'))
            existing = by_product.get(product_id, [])
            taken = Decimal('0.00')
            for item in existing:
                taken -= item.qty
            delta = want - taken
            if delta:
                next_qty = product.stock_qty - delta
                if next_qty < 0 and not allow_negative:
                    raise StockError(f'{product.name} için yetersiz stok (elde {product.stock_qty}).')
                product.stock_qty = next_qty
                product.save(update_fields=['stock_qty', 'updated_at'])
            if want == 0:
                for item in existing:
                    item.delete()
                continue
            keep = existing[0] if existing else None
            if keep is None:
                StockMovement.objects.create(
                    product=product,
                    qty=-want,
                    reason=StockMovement.REASON_JOB,
                    job=job,
                    note=note,
                    created_by=user,
                )
                continue
            if keep.qty != -want or keep.job_id != job.pk or keep.note != note:
                keep.qty = -want
                keep.job = job
                keep.note = note
                keep.save(update_fields=['qty', 'job', 'note'])
            for item in existing[1:]:
                item.delete()
    except StockError as exc:
        raise ValueError(str(exc)) from exc


def unit_photo_response(*, job: Job, raw_id: str, photo_id: str = '', pack: bool = False, group_id: str = ''):
    if str(group_id).isdigit():
        group = JobSoldPack.objects.filter(pk=int(group_id), job=job).first()
        if not group:
            raise Http404()
        if pack:
            return pack_album_zip(group)
        if not str(photo_id).isdigit():
            raise Http404()
        photo = JobSoldUnitPhoto.objects.filter(pk=int(photo_id), pack=group).first()
        if not photo or not photo.image:
            raise Http404()
        try:
            handle = photo.image.open('rb')
        except FileNotFoundError as exc:
            raise Http404() from exc
        return FileResponse(handle, as_attachment=False, filename=Path(photo.image.name).name)
    if not str(raw_id).isdigit():
        raise Http404()
    unit = JobSoldUnit.objects.filter(pk=int(raw_id), job=job).first()
    if not unit:
        raise Http404()
    if pack:
        if unit.pack_id:
            return pack_album_zip(unit.pack)
        return unit_album_zip(unit)
    if not str(photo_id).isdigit():
        raise Http404()
    photo = JobSoldUnitPhoto.objects.filter(pk=int(photo_id), unit=unit).first()
    if not photo or not photo.image:
        raise Http404()
    try:
        handle = photo.image.open('rb')
    except FileNotFoundError as exc:
        raise Http404() from exc
    return FileResponse(handle, as_attachment=False, filename=Path(photo.image.name).name)


def pack_album_zip(pack: JobSoldPack):
    photos = [item for item in pack.photo_items if item.image]
    if not photos:
        raise Http404()
    buf = io.BytesIO()
    written = 0
    with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for index, photo in enumerate(photos, start=1):
            ext = Path(photo.image.name).suffix.lower() or '.jpg'
            try:
                handle = photo.image.open('rb')
            except FileNotFoundError:
                continue
            with handle:
                archive.writestr(f'{index:02d}{ext}', handle.read())
            written += 1
    if not written:
        raise Http404()
    buf.seek(0)
    return FileResponse(
        buf,
        as_attachment=True,
        filename=pack.album_zip_name,
        content_type='application/zip',
    )


def unit_album_zip(unit: JobSoldUnit):
    photos = [item for item in unit.photo_items if item.image]
    if not photos:
        raise Http404()
    buf = io.BytesIO()
    written = 0
    with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for index, photo in enumerate(photos, start=1):
            ext = Path(photo.image.name).suffix.lower() or '.jpg'
            try:
                handle = photo.image.open('rb')
            except FileNotFoundError:
                continue
            with handle:
                archive.writestr(f'{index:02d}{ext}', handle.read())
            written += 1
    if not written:
        raise Http404()
    buf.seek(0)
    return FileResponse(
        buf,
        as_attachment=True,
        filename=unit.album_zip_name,
        content_type='application/zip',
    )


@transaction.atomic
def save_job(*, user, post, job: Job | None = None, files=None) -> Job:
    job_date = _parse_job_date(post)
    raw_clock = str(post.get('service_time', '')).strip()
    if raw_clock:
        clock = parse_service_time(raw_clock)
    elif job is not None:
        clock = job.time
    else:
        clock = None
    from_sale = bool(job is not None and job.sale_id)
    closing = str(post.get('action', '')).strip() == 'close'
    if from_sale:
        vat_mode = job.vat_mode
        party = job.party
        parsed_lines = None
        device = job.device
    else:
        posted_vat = str(post.get('vat_mode', '')).strip()
        if posted_vat:
            if posted_vat not in {Job.VAT_PLUS, Job.VAT_INCLUDED, Job.VAT_NONE}:
                raise ValueError('KDV tipi seçin.')
            vat_mode = posted_vat
        elif job is not None:
            vat_mode = job.vat_mode
        else:
            vat_mode = Job.VAT_NONE
        party = _resolve_party(post, user)
        kinds = post.getlist('kind') if hasattr(post, 'getlist') else []
        has_lines = any(str(item).strip() for item in kinds)
        if closing or has_lines:
            parsed_lines = _parse_job_lines(post, vat_mode)
            if closing and any(item['unit_price'] <= 0 for item in parsed_lines):
                raise ValueError('Her kaleme satış fiyatı girin.')
        else:
            parsed_lines = None
        device = _resolve_device(
            party=party,
            post=post,
            user=user,
            current=job.device if job else None,
        )
    notes = str(post.get('notes', '')).strip()
    assignee, assign_all = _resolve_assignment(post)
    if not assignee and not assign_all:
        raise ValueError('Personel seçin.')
    if assign_all and job is not None and not job.is_open:
        raise ValueError('Teslim edilen işe tüm personel ataması yapılamaz.')
    if job is None:
        job = Job(
            number=next_job_number(job_date),
            created_by=user,
            updated_by=user,
            status=Job.STATUS_OPEN,
        )
    elif job.is_pending:
        raise ValueError('Bekleyen iş önce güne alınır.')
    elif job.is_closed:
        raise ValueError('Kapalı iş düzenlenemez.')
    job.date = job_date
    job.time = clock
    job.party = party
    job.device = device
    job.assignee = None if assign_all else assignee
    job.assign_all = assign_all
    job.vat_mode = vat_mode
    job.notes = notes
    job.updated_by = user
    job.save()
    if parsed_lines is not None:
        _replace_lines(job, parsed_lines)
        job.save(update_fields=['subtotal', 'vat_total', 'grand_total', 'cost_total', 'updated_at'])
    elif not job.sale_id:
        _seed_service_labor(job, post.get('work_id'))
        job.save(update_fields=['subtotal', 'vat_total', 'grand_total', 'cost_total', 'updated_at'])
    if job.sale_id:
        apply_sold_units(job=job, post=post, files=files, user=user)
    if str(post.get('action', '')).strip() == 'close':
        if getattr(user, 'can_service_field', False) and not getattr(user, 'can_service_lead', False):
            raise ValueError('İş kapatılamaz.')
        close_job(job=job, user=user)
    return job


def relabel_mount_job(job: Job) -> Job:
    sale = getattr(job, 'sale', None)
    if not job.sale_id or sale is None or not sale.number:
        return job
    if job.number == sale.number:
        return job
    clash = Job.objects.filter(number=sale.number).exclude(pk=job.pk).exists()
    if clash:
        return job
    job.number = sale.number
    job.save(update_fields=['number'])
    return job


def schedule_sale_job(*, sale: Sale, when: date, user, clock: time | None = None) -> Job:
    today = timezone.localdate()
    if when < today:
        raise ValueError('Servis günü geçmiş olamaz.')
    job = Job.objects.filter(sale=sale).first()
    if job:
        job.date = when
        job.time = clock
        job.party = sale.party
        job.vat_mode = sale.vat_mode
        job.notes = sale.notes
        job.updated_by = user
        job.save(update_fields=['date', 'time', 'party', 'vat_mode', 'notes', 'updated_by', 'updated_at'])
        relabel_mount_job(job)
        ensure_sold_units(job)
        return job
    job = Job(
        number=sale.number,
        date=when,
        time=clock,
        party=sale.party,
        sale=sale,
        vat_mode=sale.vat_mode,
        status=Job.STATUS_PENDING,
        notes=sale.notes,
        created_by=user,
        updated_by=user,
    )
    try:
        job.save()
    except IntegrityError as exc:
        raise ValueError('Bu satış numarası zaten bir işte kayıtlı.') from exc
    ensure_sold_units(job)
    return job


def sale_mount_preview_rows(sale: Sale) -> list[dict]:
    """Device rows for the temporary mount-activation panel (no job required)."""
    rows: list[dict] = []
    lines = list(sale.lines.select_related('product', 'product__outdoor', 'product__category'))
    for line in lines:
        role = _line_role(line, sale)
        if not role:
            continue
        count = unit_count(line.qty)
        brand, model, outdoor = _line_device_fields(line)
        if role == Product.KIND_SPLIT:
            for index in range(count):
                key = f's:{line.pk}:{index}'
                rows.append(
                    {
                        'source_key': key,
                        'kind': 'split',
                        'label': f'{brand} · {model}',
                        'outdoor_name': outdoor,
                        'needs_indoor_serial': True,
                        'needs_outdoor_serial': bool(outdoor),
                        'serial_name': f'serial_{key}',
                        'outdoor_name_key': f'outdoor_{key}',
                    }
                )
        elif role == Product.KIND_MULTI_OUTDOOR:
            for index in range(count):
                key = f'o:{line.pk}:{index}'
                rows.append(
                    {
                        'source_key': key,
                        'kind': 'multi_outdoor',
                        'label': f'Dış ünite · {model}',
                        'outdoor_name': model,
                        'needs_indoor_serial': False,
                        'needs_outdoor_serial': True,
                        'serial_name': '',
                        'outdoor_name_key': f'outdoor_{key}',
                    }
                )
        else:
            for index in range(count):
                key = f'i:{line.pk}:{index}'
                rows.append(
                    {
                        'source_key': key,
                        'kind': 'multi_indoor',
                        'label': f'İç ünite · {brand} · {model}',
                        'outdoor_name': '',
                        'needs_indoor_serial': True,
                        'needs_outdoor_serial': False,
                        'serial_name': f'serial_{key}',
                        'outdoor_name_key': '',
                    }
                )
    return rows


def _auto_assign_multi_indoors(job: Job) -> None:
    packs = list(
        JobSoldPack.objects.filter(job=job, kind=JobSoldPack.KIND_MULTI).order_by('sort', 'id')
    )
    units = list(JobSoldUnit.objects.filter(job=job, pack__isnull=True).order_by('id'))
    if not packs or not units:
        return
    for index, unit in enumerate(units):
        pack = packs[index % len(packs)]
        unit.pack = pack
        unit.save(update_fields=['pack'])


@transaction.atomic
def activate_sale_mount(*, sale: Sale, user, post) -> Job:
    """Temporary backfill: create/close mount job on sale.date with serials + care interval."""
    existing = Job.objects.filter(sale=sale).first()
    if existing and existing.status == Job.STATUS_CLOSED:
        raise ValueError('Bu satış zaten aktif edilmiş.')

    when = sale.date
    if existing:
        job = existing
        job.date = when
        job.party = sale.party
        job.vat_mode = sale.vat_mode
        job.updated_by = user
        job.save(update_fields=['date', 'party', 'vat_mode', 'updated_by', 'updated_at'])
        relabel_mount_job(job)
    else:
        job = Job(
            number=sale.number,
            date=when,
            party=sale.party,
            sale=sale,
            vat_mode=sale.vat_mode,
            status=Job.STATUS_PENDING,
            notes=sale.notes,
            created_by=user,
            updated_by=user,
        )
        try:
            job.save()
        except IntegrityError as exc:
            raise ValueError('Bu satış numarası zaten bir işte kayıtlı.') from exc

    packs = ensure_sold_packs(job)
    _auto_assign_multi_indoors(job)
    packs = list(JobSoldPack.objects.filter(job=job).prefetch_related('units').order_by('sort', 'id'))
    if not packs:
        if JobSoldUnit.objects.filter(job=job).exists():
            raise ValueError('Multi iç üniteler için satışta dış ünite kalemi de olmalı.')
        raise ValueError('Bu satışta aktive edilecek cihaz kalemi yok.')

    try:
        interval = int(
            str(post.get('interval_months', str(DEFAULT_CARE_INTERVAL))).strip()
            or str(DEFAULT_CARE_INTERVAL)
        )
    except (TypeError, ValueError) as exc:
        raise ValueError('Bakım aralığı geçersiz.') from exc
    if interval not in {3, 6, 9, 12}:
        raise ValueError('Bakım aralığı 3, 6, 9 veya 12 ay olmalı.')

    for pack in packs:
        outdoor_key = f'outdoor_{pack.source_key}'
        outdoor_serial = tr_upper(post.get(outdoor_key, ''))
        if pack.outdoor_name and not outdoor_serial:
            raise ValueError(f'Dış ünite seri no zorunlu ({pack.outdoor_name}).')
        pack.outdoor_serial = outdoor_serial
        pack.interval_months = interval
        pack.last_serviced_on = when
        pack.next_due = add_months(when, interval)
        pack.save(
            update_fields=[
                'outdoor_serial',
                'interval_months',
                'last_serviced_on',
                'next_due',
            ]
        )
        units = list(pack.units.order_by('id'))
        if not units and pack.kind == JobSoldPack.KIND_SPLIT:
            raise ValueError('İç ünite bulunamadı.')
        for unit in units:
            if pack.kind == JobSoldPack.KIND_SPLIT:
                serial = tr_upper(post.get(f'serial_{pack.source_key}', ''))
            else:
                serial = tr_upper(
                    post.get(f'serial_i:{unit.sale_line_id}:{unit.line_index}', '')
                )
            if not serial:
                raise ValueError(f'Seri no zorunlu ({unit.brand} · {unit.model}).')
            unit.serial = serial
            unit.save(update_fields=['serial'])

    job.status = Job.STATUS_SUBMITTED
    job.submitted_at = timezone.now()
    job.submitted_by = user
    job.updated_by = user
    job.save(
        update_fields=['status', 'submitted_at', 'submitted_by', 'updated_by', 'updated_at']
    )
    return close_job(job=job, user=user)


@transaction.atomic
def confirm_job(
    *,
    job: Job,
    user,
    when: date | None = None,
    clock: time | None = None,
    assignee=None,
    assign_all: bool = False,
    device: Device | None = None,
) -> Job:
    today = timezone.localdate()
    if not job.is_waiting:
        raise ValueError('Bu iş bekleyen değil.')
    if assignee is None and not assign_all:
        raise ValueError('Personel seçin.')
    if when is not None:
        if when < today:
            raise ValueError('Servis günü geçmiş olamaz.')
        job.date = when
        if clock is not None:
            job.time = clock
    elif job.date < today:
        raise ValueError('Takvimden yeni gün seçin.')
    job.assignee = None if assign_all else assignee
    job.assign_all = bool(assign_all)
    if job.sale_id:
        job.device = None
    elif device is not None:
        job.device = device
    job.status = Job.STATUS_OPEN
    job.updated_by = user
    job.save(update_fields=['date', 'time', 'assignee', 'assign_all', 'device', 'status', 'updated_by', 'updated_at'])
    return job


@transaction.atomic
def close_job(*, job: Job, user) -> Job:
    if getattr(user, 'can_service_field', False) and not getattr(user, 'can_service_lead', False):
        raise ValueError('Kapatma ofiste yapılır.')
    if job.status != Job.STATUS_SUBMITTED:
        raise ValueError('Saha teslim etmeden iş kapatılamaz.')
    lines = list(job.lines.select_related('product'))
    if job.sale_id:
        devices = devices_from_sold_packs(job=job, user=user)
        if devices:
            job.device = devices[0]
        elif job.device_id:
            device = job.device
            device.last_serviced_on = job.date
            device.next_due = add_months(job.date, device.interval_months)
            device.save(update_fields=['last_serviced_on', 'next_due', 'updated_at'])
        snapshot_closed_pricing(job, overwrite=True)
        job.status = Job.STATUS_CLOSED
        job.updated_by = user
        job.save(
            update_fields=[
                'status',
                'device',
                'updated_by',
                'updated_at',
                'list_subtotal',
                'list_vat',
                'list_grand',
                'discount_rate',
            ]
        )
        return job
    if not lines:
        raise ValueError('En az bir kalem ekleyin.')
    if any(item.unit_price <= 0 for item in lines):
        raise ValueError('Her kaleme satış fiyatı girin.')
    for item in lines:
        if item.product_id and item.kind == JobLine.KIND_PART:
            apply_movement(
                product=item.product,
                qty=-item.qty,
                reason=StockMovement.REASON_JOB,
                user=user,
                job=job,
                note=_service_stock_note(job),
                allow_negative=True,
            )
    if job.device_id:
        device = job.device
        device.last_serviced_on = job.date
        device.next_due = add_months(job.date, device.interval_months)
        device.save(update_fields=['last_serviced_on', 'next_due', 'updated_at'])
    snapshot_closed_pricing(job, overwrite=True)
    job.status = Job.STATUS_CLOSED
    job.updated_by = user
    job.save(
        update_fields=[
            'status',
            'updated_by',
            'updated_at',
            'list_subtotal',
            'list_vat',
            'list_grand',
            'discount_rate',
        ]
    )
    return job


def snapshot_closed_pricing(job: Job, *, overwrite: bool = False) -> None:
    lines = list(job.lines.all())
    for line in lines:
        if overwrite or not line.list_unit_price:
            line.list_unit_price = line.unit_price
            line.save(update_fields=['list_unit_price'])
    if overwrite or not job.list_grand:
        job.list_subtotal = job.subtotal
        job.list_vat = job.vat_total
        job.list_grand = job.grand_total
        job.discount_rate = Decimal('0.0000')


def _closed_vat_rate(line: JobLine, vat_mode: str) -> Decimal:
    if vat_mode == Job.VAT_NONE:
        return Decimal('0.00')
    if line.vat_rate and line.vat_rate > 0:
        return line.vat_rate
    return Decimal('20.00')


def _apply_closed_line_total(line: JobLine, *, vat_mode: str, vat_rate: Decimal, new_total: Decimal) -> None:
    qty = line.qty or Decimal('0.00')
    new_total = money(new_total)
    if new_total < 0:
        new_total = Decimal('0.00')
    if vat_mode == Job.VAT_NONE:
        net = new_total
        vat = Decimal('0.00')
        total = new_total
        unit_price = money(new_total / qty) if qty else Decimal('0.00')
    elif vat_mode == Job.VAT_INCLUDED:
        total = new_total
        if vat_rate:
            net = money(total / (1 + vat_rate / Decimal('100')))
        else:
            net = total
        vat = money(total - net)
        unit_price = money(total / qty) if qty else Decimal('0.00')
    else:
        if vat_rate:
            net = money(new_total / (1 + vat_rate / Decimal('100')))
        else:
            net = new_total
        vat = money(new_total - net)
        total = new_total
        unit_price = money(net / qty) if qty else Decimal('0.00')
    line.unit_price = unit_price
    line.vat_rate = vat_rate
    line.line_net = net
    line.line_vat = vat
    line.line_total = total
    line.save(update_fields=['unit_price', 'vat_rate', 'line_net', 'line_vat', 'line_total'])


def apply_closed_pricing(job: Job, *, vat_mode: str, target_grand: Decimal | None) -> Job:
    if vat_mode not in {Job.VAT_PLUS, Job.VAT_INCLUDED, Job.VAT_NONE}:
        raise ValueError('KDV tipi seçin.')
    snapshot_closed_pricing(job, overwrite=False)
    lines = list(job.lines.order_by('id'))
    if not lines:
        raise ValueError('En az bir kalem ekleyin.')
    list_rows = []
    for line in lines:
        rate = _closed_vat_rate(line, vat_mode)
        net, vat, total = line_amounts(line.qty, line.list_unit_price, rate, vat_mode)
        list_rows.append({'line': line, 'rate': rate, 'net': net, 'vat': vat, 'total': total})
    list_subtotal = money(sum((row['net'] for row in list_rows), Decimal('0.00')))
    list_vat = money(sum((row['vat'] for row in list_rows), Decimal('0.00')))
    list_grand = money(sum((row['total'] for row in list_rows), Decimal('0.00')))
    job.vat_mode = vat_mode
    job.list_subtotal = list_subtotal
    job.list_vat = list_vat
    job.list_grand = list_grand
    if target_grand is None:
        rate = job.discount_rate or Decimal('0.0000')
        target_grand = money(list_grand * (1 - rate / Decimal('100')))
    else:
        target_grand = money(target_grand)
    if target_grand < 0:
        raise ValueError('Genel toplam negatif olamaz.')
    paid = job.paid_total
    if target_grand < paid:
        raise ValueError(f'Genel toplam tahsilattan ({paid} TL) küçük olamaz.')
    if list_grand > 0:
        job.discount_rate = ((list_grand - target_grand) / list_grand * Decimal('100')).quantize(
            Decimal('0.0001'),
            rounding=ROUND_HALF_UP,
        )
    else:
        job.discount_rate = Decimal('0.0000')
        target_grand = Decimal('0.00')
    assigned = Decimal('0.00')
    count = len(list_rows)
    for index, row in enumerate(list_rows):
        if index == count - 1:
            new_total = money(target_grand - assigned)
        elif list_grand:
            new_total = money(target_grand * row['total'] / list_grand)
            assigned += new_total
        else:
            new_total = Decimal('0.00')
        _apply_closed_line_total(row['line'], vat_mode=vat_mode, vat_rate=row['rate'], new_total=new_total)
    _recompute_job_totals(job)
    return job


@transaction.atomic
def adjust_closed_job(*, job: Job, user, post) -> Job:
    if getattr(user, 'can_service_field', False) and not getattr(user, 'can_service_lead', False):
        raise ValueError('Bu işlem ofiste yapılır.')
    if not job.is_closed:
        raise ValueError('Yalnız kapalı işte ödeme detayı değişir.')
    if job.sale_id:
        raise ValueError('Satışa bağlı işte tutar satış fişinden gelir.')
    vat_mode = str(post.get('vat_mode', '')).strip() or job.vat_mode
    raw_grand = str(post.get('grand_total', '')).strip()
    target = parse_decimal(raw_grand, 'Genel toplam') if raw_grand else None
    apply_closed_pricing(job, vat_mode=vat_mode, target_grand=target)
    job.updated_by = user
    job.save(
        update_fields=[
            'vat_mode',
            'subtotal',
            'vat_total',
            'grand_total',
            'cost_total',
            'list_subtotal',
            'list_vat',
            'list_grand',
            'discount_rate',
            'updated_by',
            'updated_at',
        ]
    )
    return job


@transaction.atomic
def field_member_for(user):
    from accounts.http import crew_member_for
    return crew_member_for(user)


def field_can_edit(*, job: Job, user) -> bool:
    member = field_member_for(user)
    if not member or not job.is_open:
        return False
    if job.assign_all:
        return True
    return job.assignee_id == member.pk


def field_can_view(*, job: Job, user) -> bool:
    if getattr(user, 'can_service_lead', False) or getattr(user, 'is_superuser', False):
        return True
    member = field_member_for(user)
    if not member:
        return False
    if job.assignee_id == member.pk:
        return True
    return bool(job.assign_all and job.is_open)


def pack_photo_url(job: Job, photo: JobSoldUnitPhoto) -> str:
    return f'{job.get_field_url()}?group={photo.pack_id}&photo={photo.pk}'


def add_pack_photos(*, job: Job, pack: JobSoldPack, files) -> list[dict]:
    if pack.job_id != job.pk:
        raise ValueError('Görsel bu işe ait değil.')
    files = files or {}
    key = f'unit_photos_{pack.pk}'
    raw = list(files.getlist(key)) if hasattr(files, 'getlist') else ([files.get(key)] if files.get(key) else [])
    created = []
    sort = pack.photos.count()
    for item in raw:
        upload = _parse_unit_photo(item)
        if not upload:
            continue
        photo = JobSoldUnitPhoto.objects.create(pack=pack, image=upload, sort=sort)
        created.append({'id': photo.pk, 'url': pack_photo_url(job, photo)})
        sort += 1
    if not created:
        raise ValueError('Görsel seçin.')
    return created


def delete_pack_photo(*, job: Job, post) -> None:
    raw = str(post.get('photo_id', '')).strip()
    if not raw.isdigit():
        raise ValueError('Görsel seçin.')
    photo = JobSoldUnitPhoto.objects.filter(pk=int(raw), pack__job=job).first()
    if not photo:
        raise ValueError('Görsel bulunamadı.')
    photo.delete()


def save_job_photos(*, job: Job, files, user) -> None:
    files = files or {}
    raw = list(files.getlist('job_photos')) if hasattr(files, 'getlist') else ([files.get('job_photos')] if files.get('job_photos') else [])
    sort = job.photos.count()
    for item in raw:
        upload = _parse_unit_photo(item)
        if not upload:
            continue
        JobPhoto.objects.create(job=job, image=upload, sort=sort, created_by=user)
        sort += 1


def delete_job_photo(*, job: Job, post) -> None:
    raw = str(post.get('photo_id', '')).strip()
    if not raw.isdigit():
        raise ValueError('Görsel seçin.')
    photo = JobPhoto.objects.filter(pk=int(raw), job=job).first()
    if not photo:
        raise ValueError('Görsel bulunamadı.')
    photo.delete()


def job_photo_response(*, job: Job, photo_id: str):
    if not str(photo_id).isdigit():
        raise Http404()
    photo = JobPhoto.objects.filter(pk=int(photo_id), job=job).first()
    if not photo or not photo.image:
        raise Http404()
    try:
        handle = photo.image.open('rb')
    except FileNotFoundError as exc:
        raise Http404() from exc
    return FileResponse(handle, as_attachment=False, filename=Path(photo.image.name).name)


def mount_handover_gaps(job: Job) -> list[str]:
    if not job.sale_id:
        return []
    gaps: list[str] = []
    seen: set[str] = set()

    def add(message: str) -> None:
        if message not in seen:
            seen.add(message)
            gaps.append(message)

    packs = list(job.sold_packs.prefetch_related('units', 'photos'))
    if not packs:
        add('Satılan cihaz bulunamadı.')
        return gaps
    for pack in packs:
        if pack.photos.count() < MOUNT_PHOTO_MIN:
            add('Her cihaz için en az 4 görsel ekleyin.')
            break
    for unit in JobSoldUnit.objects.filter(job=job).order_by('id'):
        if not str(unit.room or '').strip():
            add('Oda yazın.')
        if not str(unit.serial or '').strip():
            add('İç ünite seri numarasını yazın.')
    for pack in packs:
        if pack.outdoor_name and not str(pack.outdoor_serial or '').strip():
            add('Dış ünite seri numarasını yazın.')
        if not pack.last_serviced_on:
            add('Bakım tarihini yazın.')
    if not JobSoldUnitMaterial.objects.filter(pack__job=job).exists():
        add('En az bir montaj malzemesi ekleyin.')
    return gaps


@transaction.atomic
def save_field_job(*, user, job: Job, post, files=None) -> Job:
    if not field_can_edit(job=job, user=user):
        raise ValueError('Bu iş size atanmadı veya teslim edildi.')
    job.notes = str(post.get('notes', '')).strip()
    job.updated_by = user
    posted_lines = str(post.get('field_lines_present', '')).strip() == '1'
    kinds = post.getlist('kind') if hasattr(post, 'getlist') else []
    if posted_lines or any(str(item).strip() for item in kinds):
        try:
            parsed = _parse_job_lines(post, job.vat_mode)
        except ValueError as exc:
            if 'En az bir kalem' not in str(exc):
                raise
            parsed = [] if posted_lines else None
        if parsed is not None:
            if posted_lines:
                _reject_klima_parts(parsed)
                _replace_field_service_parts(job, parsed)
            else:
                _replace_lines(job, parsed)
    job.save()
    save_job_photos(job=job, files=files, user=user)
    if job.sale_id:
        apply_sold_units(job=job, post=post, files=files, user=user, allow_negative=True)
    if str(post.get('action', '')).strip() == 'submit':
        submit_field_job(job=job, user=user)
    return job


@transaction.atomic
def submit_field_job(*, job: Job, user) -> Job:
    if not field_can_edit(job=job, user=user):
        raise ValueError('Bu iş teslim edilemez.')
    member = field_member_for(user)
    job.status = Job.STATUS_SUBMITTED
    job.submitted_at = timezone.now()
    job.submitted_by = user
    job.updated_by = user
    fields = ['status', 'submitted_at', 'submitted_by', 'updated_by', 'updated_at']
    if job.assign_all and member:
        job.assignee = member
        fields.append('assignee')
    job.save(update_fields=fields)
    return job


def delete_job(*, job: Job, user, allow_closed: bool = False) -> None:
    if job.status == Job.STATUS_CLOSED and not allow_closed:
        raise ValueError('Kapalı iş silinemez.')
    _sync_mount_stock(job=job, user=user, wanted={})
    job.delete()
