import re
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from stock.models import Product, StockMovement
from stock.services import apply_movement

from .models import Party, Payment, PaymentAllocation, Sale, SaleLine
from .tr_locations import is_known_city, is_known_district

TWOPLACES = Decimal('0.01')


def money(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


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
        return money(Decimal(text))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f'{field} geçersiz.') from exc


def line_amounts(qty: Decimal, unit_price: Decimal, vat_rate: Decimal, vat_mode: str):
    base = money(qty * unit_price)
    if vat_mode == Sale.VAT_NONE:
        return base, Decimal('0.00'), base
    if vat_mode == Sale.VAT_INCLUDED:
        total = base
        net = money(total / (1 + vat_rate / Decimal('100')))
        vat = money(total - net)
        return net, vat, total
    net = base
    vat = money(net * vat_rate / Decimal('100'))
    return net, vat, money(net + vat)


def compact_sale_number(number: str) -> str:
    return re.sub(r'[^A-Za-z0-9]', '', str(number or '')).upper()


PARTY_CODE_PREFIX = 'CUSTC'
PARTY_CODE_RE = re.compile(r'^(CUSTC)(\d+)(?:-(\d+))?$', re.I)
ANON_PARTY_WIDTH = 4


def compact_party_number(number: str) -> str:
    text = re.sub(r'[^A-Za-z0-9-]', '', str(number or '')).upper()
    match = PARTY_CODE_RE.match(text)
    if not match:
        return text
    prefix, digits, suffix = match.group(1).upper(), match.group(2), match.group(3)
    if suffix:
        return f'{prefix}{digits}-{int(suffix)}'
    return f'{prefix}{digits}'


def _taken_party_numbers(exclude_pk=None) -> set[str]:
    qs = Party.objects.all()
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    return {compact_party_number(item) for item in qs.values_list('number', flat=True)}


def _unique_party_number(base: str, *, exclude_pk=None) -> str:
    taken = _taken_party_numbers(exclude_pk)
    if base not in taken:
        return base
    serial = 1
    while True:
        candidate = f'{base}-{serial}'
        if candidate not in taken:
            return candidate
        serial += 1


def _next_anon_party_number(*, exclude_pk=None) -> str:
    taken = _taken_party_numbers(exclude_pk)
    serial = 0
    for number in taken:
        match = PARTY_CODE_RE.match(number)
        if not match or match.group(3):
            continue
        digits = match.group(2)
        if len(digits) in (10, 11):
            continue
        serial = max(serial, int(digits))
    while True:
        serial += 1
        candidate = f'{PARTY_CODE_PREFIX}{serial:0{ANON_PARTY_WIDTH}d}'
        if candidate not in taken:
            return candidate


def next_party_number(*, kind: str, tax_no='', national_id='', exclude_pk=None) -> str:
    if kind == Party.KIND_LEGAL:
        digits = only_digits(tax_no)
        if len(digits) not in (10, 11):
            raise ValueError('Vergi kimlik no 10 veya 11 haneli olmalıdır.')
        return _unique_party_number(f'{PARTY_CODE_PREFIX}{digits}', exclude_pk=exclude_pk)
    digits = only_digits(national_id)
    if not digits:
        return _next_anon_party_number(exclude_pk=exclude_pk)
    if len(digits) != 11:
        raise ValueError('T.C. kimlik no 11 haneli olmalıdır.')
    return _unique_party_number(f'{PARTY_CODE_PREFIX}{digits}', exclude_pk=exclude_pk)


def next_sale_number(when: date) -> str:
    prefix = f'SAL{when.year}'
    serial = 0
    numbers = list(Sale.objects.filter(number__startswith=prefix).values_list('number', flat=True))
    numbers.extend(Sale.objects.filter(number__startswith=f'SAL-{when.year}-').values_list('number', flat=True))
    from service.models import Job
    numbers.extend(Job.objects.filter(number__startswith=prefix).values_list('number', flat=True))
    for number in numbers:
        compact = compact_sale_number(number)
        if compact.startswith(prefix) and compact[len(prefix):].isdigit():
            serial = max(serial, int(compact[len(prefix):]))
    return f'{prefix}{serial + 1:04d}'


def party_from_post(post, user) -> Party:
    party = Party(created_by=user, phone='-', address='-')
    return apply_party_fields(party, post)


def only_digits(value: str) -> str:
    return re.sub(r'\D', '', str(value or ''))


def tr_upper(value: str) -> str:
    return str(value or '').replace('i', 'İ').replace('ı', 'I').upper().strip()


def parse_card_meta(post, *, method: str) -> tuple[str, int | None]:
    if method != Payment.METHOD_CARD:
        return '', None
    holder = tr_upper(post.get('card_holder', ''))
    if not holder:
        raise ValueError('Kart üzerindeki ad soyad zorunlu.')
    raw = str(post.get('card_installments', '')).strip()
    if not raw:
        raise ValueError('Kart ödemesinde taksit seçin.')
    try:
        count = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError('Taksit geçersiz.') from exc
    allowed = {value for value, _label in Payment.INSTALLMENT_CHOICES}
    if count not in allowed:
        raise ValueError('Taksit peşin, 2, 3, 4, 6, 9 veya 12 olabilir.')
    return holder, count


def parse_transfer_sender(post, *, method: str) -> str:
    if method != Payment.METHOD_TRANSFER:
        return ''
    sender = tr_upper(post.get('transfer_sender', ''))
    if not sender:
        raise ValueError('Havale eden ad soyad zorunlu.')
    return sender


def format_tr_phone(value: str, *, required: bool) -> str:
    digits = only_digits(value)
    if not digits:
        if required:
            raise ValueError('Telefon zorunlu.')
        return ''
    if not digits.startswith('0'):
        digits = '0' + digits
    if len(digits) != 11:
        raise ValueError('Telefon 0 (5XX) XXX XX XX formatında 11 hane olmalıdır.')
    return f'{digits[0]} ({digits[1:4]}) {digits[4:7]} {digits[7:9]} {digits[9:11]}'


def _optional_city_district(city: str, district: str) -> tuple[str, str]:
    city = tr_upper(city)
    district = tr_upper(district)
    if city and not is_known_city(city):
        raise ValueError('İl geçersiz.')
    if district and not city:
        raise ValueError('İlçe için il seçin.')
    if city and district and not is_known_district(city, district):
        raise ValueError('İlçe geçersiz.')
    return city, district


def mount_fields_from_party(party: Party) -> dict:
    name = f'{party.first_name} {party.last_name}'.strip()
    if not name and party.kind == Party.KIND_LEGAL:
        name = (party.company_name or '').strip()
    return {
        'mount_contact_name': tr_upper(name),
        'mount_phone': party.phone or '',
        'mount_city': tr_upper(party.city or ''),
        'mount_district': tr_upper(party.district or ''),
        'mount_address': tr_upper(party.address or ''),
        'mount_notes': '',
    }


def mount_fields_from_post(post) -> dict:
    city, district = _optional_city_district(post.get('mount_city', ''), post.get('mount_district', ''))
    return {
        'mount_contact_name': tr_upper(post.get('mount_contact_name', '')),
        'mount_phone': format_tr_phone(post.get('mount_phone', ''), required=False),
        'mount_city': city,
        'mount_district': district,
        'mount_address': tr_upper(post.get('mount_address', '')),
        'mount_notes': str(post.get('mount_notes', '') or '').strip(),
    }


def resolve_sale_mount(*, party: Party, post) -> dict:
    if party.kind == Party.KIND_LEGAL:
        return mount_fields_from_post(post)
    return mount_fields_from_party(party)


def apply_party_fields(party: Party, post) -> Party:
    kind = str(post.get('kind', party.kind)).strip()
    if kind not in {Party.KIND_REAL, Party.KIND_LEGAL}:
        raise ValueError('Müşteri türü seçin.')
    address = tr_upper(post.get('address', ''))
    if not address:
        raise ValueError('Adres zorunlu.')
    party.kind = kind
    party.first_name = tr_upper(post.get('first_name', ''))
    party.last_name = tr_upper(post.get('last_name', ''))
    party.company_name = tr_upper(post.get('company_name', ''))
    party.tax_office = tr_upper(post.get('tax_office', ''))
    party.email = tr_upper(post.get('email', ''))
    party.phone = format_tr_phone(post.get('phone', ''), required=True)
    party.contact2_name = tr_upper(post.get('contact2_name', ''))
    party.phone2 = format_tr_phone(post.get('phone2', ''), required=False)
    party.address = address
    city = tr_upper(post.get('city', ''))
    district = tr_upper(post.get('district', ''))
    if not city:
        raise ValueError('İl zorunlu.')
    if not district:
        raise ValueError('İlçe zorunlu.')
    party.city = city
    party.district = district
    party.notes = tr_upper(post.get('party_notes', post.get('notes', '')))
    if kind == Party.KIND_LEGAL:
        if not party.company_name:
            raise ValueError('Unvan zorunlu.')
        if not party.first_name or not party.last_name:
            raise ValueError('Yetkili ad ve soyad zorunlu.')
        tax_no = only_digits(post.get('tax_no', ''))
        if len(tax_no) not in (10, 11):
            raise ValueError('Vergi kimlik no 10 veya 11 haneli olmalıdır.')
        clash = (
            Party.objects.filter(kind=Party.KIND_LEGAL, tax_no=tax_no)
            .exclude(pk=party.pk or None)
            .first()
        )
        if clash:
            raise ValueError(
                f'Bu vergi no ile kayıtlı müşteri var: {clash.display_name} ({clash.number}).'
            )
        party.tax_no = tax_no
        party.national_id = ''
    else:
        if not party.first_name or not party.last_name:
            raise ValueError('Ad ve soyad zorunlu.')
        national_id = only_digits(post.get('national_id', ''))
        if national_id and len(national_id) != 11:
            raise ValueError('T.C. kimlik no 11 haneli olmalıdır.')
        party.national_id = national_id
        party.tax_no = ''
        party.tax_office = ''
        party.company_name = ''
    if not party.number:
        party.number = next_party_number(
            kind=party.kind,
            tax_no=party.tax_no,
            national_id=party.national_id,
            exclude_pk=party.pk,
        )
    party.save()
    return party


@transaction.atomic
def create_sale(*, user, post) -> Sale:
    work_type = Sale.WORK_DEVICE
    vat_mode = str(post.get('vat_mode', '')).strip()
    if str(post.get('invoice_issued', '')).strip() in {'1', 'on', 'true', 'yes'}:
        invoice_status = Sale.INVOICE_YES
    else:
        invoice_status = str(post.get('invoice_status', Sale.INVOICE_NO)).strip()
    if vat_mode not in {Sale.VAT_PLUS, Sale.VAT_INCLUDED, Sale.VAT_NONE}:
        raise ValueError('KDV tipi seçin.')
    if invoice_status not in {Sale.INVOICE_NO, Sale.INVOICE_YES}:
        raise ValueError('Fatura durumu seçin.')

    raw_date = str(post.get('date', '')).strip()
    try:
        sale_date = date.fromisoformat(raw_date) if raw_date else timezone.localdate()
    except ValueError as exc:
        raise ValueError('Tarih geçersiz.') from exc
    raw_service = str(post.get('service_date', '')).strip()
    service_date = None
    if raw_service:
        try:
            service_date = date.fromisoformat(raw_service)
        except ValueError as exc:
            raise ValueError('Servis günü geçersiz.') from exc
        if service_date < timezone.localdate():
            raise ValueError('Servis günü geçmiş olamaz.')
    service_time = None
    if service_date:
        from service.services import parse_service_time
        service_time = parse_service_time(post.get('service_time'))

    party_id = str(post.get('party_id', '')).strip()
    party_mode = str(post.get('party_mode', 'existing' if party_id else 'new')).strip()
    if party_id or party_mode == 'existing':
        if not party_id:
            raise ValueError('Müşteri seçin.')
        party = Party.objects.get(pk=party_id)
    else:
        party = party_from_post(post, user)

    product_ids = post.getlist('product_id')
    qtys = post.getlist('qty')
    prices = post.getlist('unit_price')
    descriptions = post.getlist('description')
    vat_rates = post.getlist('vat_rate')

    parsed_lines = []
    for index, product_id in enumerate(product_ids):
        product_id = str(product_id).strip()
        if not product_id:
            continue
        qty = parse_decimal(qtys[index] if index < len(qtys) else '', 'Adet')
        price = parse_decimal(prices[index] if index < len(prices) else '', 'Birim fiyat')
        if qty <= 0:
            raise ValueError('Adet sıfırdan büyük olmalı.')
        if price < 0:
            raise ValueError('Birim fiyat negatif olamaz.')
        product = Product.objects.select_for_update().get(pk=product_id, is_active=True)
        vat_rate = (
            parse_decimal(vat_rates[index], 'KDV')
            if index < len(vat_rates) and str(vat_rates[index]).strip()
            else product.vat_rate
        )
        if vat_mode == Sale.VAT_NONE:
            vat_rate = Decimal('0.00')
        net, vat, total = line_amounts(qty, price, vat_rate, vat_mode)
        parsed_lines.append(
            {
                'product': product,
                'qty': qty,
                'unit_price': price,
                'vat_rate': vat_rate,
                'description': descriptions[index].strip() if index < len(descriptions) else '',
                'net': net,
                'vat': vat,
                'total': total,
            }
        )

    if not parsed_lines:
        raise ValueError('En az bir ürün kalemi ekleyin.')

    subtotal = money(sum((item['net'] for item in parsed_lines), Decimal('0')))
    vat_total = money(sum((item['vat'] for item in parsed_lines), Decimal('0')))
    grand_total = money(sum((item['total'] for item in parsed_lines), Decimal('0')))

    mount = resolve_sale_mount(party=party, post=post)
    sale = Sale.objects.create(
        number=next_sale_number(sale_date),
        date=sale_date,
        party=party,
        work_type=work_type,
        vat_mode=vat_mode,
        invoice_status=invoice_status,
        invoice_no=tr_upper(post.get('invoice_no', '')),
        notes=str(post.get('notes', '')).strip(),
        mount_contact_name=mount['mount_contact_name'],
        mount_phone=mount['mount_phone'],
        mount_city=mount['mount_city'],
        mount_district=mount['mount_district'],
        mount_address=mount['mount_address'],
        mount_notes=mount['mount_notes'],
        subtotal=subtotal,
        vat_total=vat_total,
        grand_total=grand_total,
        created_by=user,
        updated_by=user,
    )

    for item in parsed_lines:
        line = SaleLine.objects.create(
            sale=sale,
            product=item['product'],
            description=item['description'],
            qty=item['qty'],
            unit_price=item['unit_price'],
            vat_rate=item['vat_rate'],
            line_net=item['net'],
            line_vat=item['vat'],
            line_total=item['total'],
        )
        if item['product']:
            apply_movement(
                product=item['product'],
                qty=-item['qty'],
                reason=StockMovement.REASON_SALE,
                user=user,
                sale_line=line,
            )

    methods = post.getlist('pay_method')
    amounts = post.getlist('pay_amount')
    paid = Decimal('0.00')
    parsed_pays = []
    for index, method in enumerate(methods):
        method = str(method).strip()
        raw = amounts[index] if index < len(amounts) else ''
        if not str(raw).strip():
            continue
        if method not in {
            Payment.METHOD_CASH,
            Payment.METHOD_CARD,
            Payment.METHOD_TRANSFER,
        }:
            raise ValueError('Ödeme yöntemi seçin.')
        amount = parse_decimal(raw, 'Ödeme tutarı')
        if amount <= 0:
            raise ValueError('Ödeme tutarı sıfırdan büyük olmalı.')
        paid += amount
        holder, installments = parse_card_meta(post, method=method)
        sender = parse_transfer_sender(post, method=method)
        parsed_pays.append((method, amount, holder, installments, sender))
    if paid > grand_total:
        raise ValueError('Tahsilat genel toplamı aşamaz.')
    for method, amount, holder, installments, sender in parsed_pays:
        _create_receipt(
            party=party,
            user=user,
            method=method,
            amount=amount,
            pay_date=sale_date,
            holder=holder,
            installments=installments,
            sender=sender,
            sale=sale,
        )

    if service_date:
        from service.services import apply_sale_pack_groups, schedule_sale_job

        job = schedule_sale_job(sale=sale, when=service_date, user=user, clock=service_time)
        apply_sale_pack_groups(job, post.getlist('indoor_group'))

    return sale


def _parse_payment_post(post) -> dict:
    method = str(post.get('pay_method', '')).strip()
    if method not in {Payment.METHOD_CASH, Payment.METHOD_CARD, Payment.METHOD_TRANSFER}:
        raise ValueError('Ödeme yöntemi seçin.')
    amount = parse_decimal(post.get('pay_amount'), 'Ödeme tutarı')
    if amount <= 0:
        raise ValueError('Ödeme tutarı sıfırdan büyük olmalı.')
    raw_date = str(post.get('pay_date', '')).strip()
    try:
        pay_date = date.fromisoformat(raw_date) if raw_date else timezone.localdate()
    except ValueError as exc:
        raise ValueError('Ödeme tarihi geçersiz.') from exc
    holder, installments = parse_card_meta(post, method=method)
    sender = parse_transfer_sender(post, method=method)
    return {
        'method': method,
        'amount': amount,
        'pay_date': pay_date,
        'holder': holder,
        'installments': installments,
        'sender': sender,
    }


def _create_receipt(
    *,
    party: Party,
    user,
    method: str,
    amount: Decimal,
    pay_date: date,
    holder: str,
    installments: int | None,
    sender: str,
    sale: Sale | None = None,
    job=None,
    splits: list[dict] | None = None,
) -> Payment:
    payment = Payment.objects.create(
        party=party,
        method=method,
        amount=amount,
        date=pay_date,
        created_by=user,
        card_holder=holder,
        card_installments=installments,
        transfer_sender=sender,
    )
    rows = splits or []
    if not rows:
        if sale is not None:
            rows = [{'sale': sale, 'job': None, 'amount': amount}]
        elif job is not None:
            rows = [{'sale': None, 'job': job, 'amount': amount}]
        else:
            raise ValueError('Tahsilat fişi seçin.')
    for row in rows:
        PaymentAllocation.objects.create(
            payment=payment,
            sale=row.get('sale'),
            job=row.get('job'),
            amount=row['amount'],
        )
    return payment


def party_open_slips(party: Party) -> list[dict]:
    from service.models import Job

    slips = []
    for sale in Sale.objects.filter(party=party).order_by('date', 'id'):
        remaining = sale.remaining
        if remaining > 0:
            slips.append(
                {
                    'kind': 'sale',
                    'sale': sale,
                    'job': None,
                    'date': sale.date,
                    'id': sale.id,
                    'remaining': remaining,
                }
            )
    for job in Job.objects.filter(
        party=party,
        status=Job.STATUS_CLOSED,
        sale_id__isnull=True,
    ).order_by('date', 'id'):
        remaining = job.remaining
        if remaining > 0:
            slips.append(
                {
                    'kind': 'job',
                    'sale': None,
                    'job': job,
                    'date': job.date,
                    'id': job.id,
                    'remaining': remaining,
                }
            )
    slips.sort(key=lambda item: (item['date'], item['id']))
    return slips


def party_open_remaining(party: Party) -> Decimal:
    return money(sum((item['remaining'] for item in party_open_slips(party)), Decimal('0.00')))


@transaction.atomic
def add_payment(*, sale: Sale, user, post) -> Payment:
    fields = _parse_payment_post(post)
    remaining = sale.remaining
    if fields['amount'] > remaining:
        raise ValueError(f'Kalan borç {remaining} TL. Daha fazla tahsil edilemez.')
    payment = _create_receipt(party=sale.party, user=user, sale=sale, **fields)
    sale.updated_by = user
    sale.save(update_fields=['updated_by', 'updated_at'])
    return payment


@transaction.atomic
def add_job_payment(*, job, user, post) -> Payment:
    if not job.is_closed or job.sale_id:
        raise ValueError('Yalnız kapalı servis fişine tahsilat yazılır.')
    fields = _parse_payment_post(post)
    remaining = job.remaining
    if fields['amount'] > remaining:
        raise ValueError(f'Kalan borç {remaining} TL. Daha fazla tahsil edilemez.')
    payment = _create_receipt(party=job.party, user=user, job=job, **fields)
    job.updated_by = user
    job.save(update_fields=['updated_by', 'updated_at'])
    return payment


@transaction.atomic
def add_party_payment(*, party: Party, user, post) -> Payment:
    fields = _parse_payment_post(post)
    slips = party_open_slips(party)
    total_remain = money(sum((item['remaining'] for item in slips), Decimal('0.00')))
    if fields['amount'] > total_remain:
        raise ValueError(f'Kalan borç {total_remain} TL. Daha fazla tahsil edilemez.')
    left = fields['amount']
    splits = []
    for slip in slips:
        if left <= 0:
            break
        take = left if left <= slip['remaining'] else slip['remaining']
        take = money(take)
        if take <= 0:
            continue
        splits.append({'sale': slip['sale'], 'job': slip['job'], 'amount': take})
        left = money(left - take)
    if not splits:
        raise ValueError(f'Kalan borç {total_remain} TL. Daha fazla tahsil edilemez.')
    return _create_receipt(party=party, user=user, splits=splits, **fields)


def _payment_for_delete(*, post, sale: Sale | None = None, job=None, party: Party | None = None) -> Payment:
    raw = str(post.get('payment_id', '')).strip()
    if not raw.isdigit():
        raise ValueError('Tahsilat seçin.')
    qs = Payment.objects.filter(pk=int(raw))
    if sale is not None:
        qs = qs.filter(allocations__sale=sale)
    elif job is not None:
        qs = qs.filter(allocations__job=job)
    elif party is not None:
        qs = qs.filter(party=party)
    payment = qs.first()
    if not payment:
        raise ValueError('Tahsilat bulunamadı.')
    return payment


@transaction.atomic
def delete_payment(*, user, post, sale: Sale | None = None, job=None, party: Party | None = None) -> Payment:
    payment = _payment_for_delete(post=post, sale=sale, job=job, party=party)
    if sale is not None:
        sale.updated_by = user
        sale.save(update_fields=['updated_by', 'updated_at'])
    if job is not None:
        job.updated_by = user
        job.save(update_fields=['updated_by', 'updated_at'])
    payment.delete()
    return payment


def reconcile_receipts(payment_ids: list[int]) -> None:
    for pid in payment_ids:
        payment = Payment.objects.filter(pk=pid).first()
        if not payment:
            continue
        leftover = payment.allocations.aggregate(s=Sum('amount'))['s'] or Decimal('0.00')
        if leftover <= 0:
            payment.delete()
        elif leftover != payment.amount:
            payment.amount = leftover
            payment.save(update_fields=['amount'])


@transaction.atomic
def delete_sale(*, sale: Sale, user) -> None:
    from service.models import Job
    from service.services import delete_job

    job = Job.objects.filter(sale=sale).first()
    if job:
        delete_job(job=job, user=user, allow_closed=True)
    lines = list(sale.lines.select_related('product'))
    for line in lines:
        if not line.product_id:
            continue
        if not line.stock_movements.filter(reason=StockMovement.REASON_SALE).exists():
            continue
        apply_movement(
            product=line.product,
            qty=line.qty,
            reason=StockMovement.REASON_ADJUST,
            user=user,
            sale_line=line,
            note=f'{sale.number} silindi.',
            allow_negative=True,
        )
    pay_ids = list(sale.payment_allocations.values_list('payment_id', flat=True))
    sale.delete()
    reconcile_receipts(pay_ids)


@transaction.atomic
def update_invoice(*, sale: Sale, user, post) -> Sale:
    status = str(post.get('invoice_status', '')).strip()
    if status not in {Sale.INVOICE_NO, Sale.INVOICE_YES}:
        raise ValueError('Fatura durumu seçin.')
    sale.invoice_status = status
    sale.invoice_no = tr_upper(post.get('invoice_no', ''))
    sale.updated_by = user
    sale.save(update_fields=['invoice_status', 'invoice_no', 'updated_by', 'updated_at'])
    return sale
