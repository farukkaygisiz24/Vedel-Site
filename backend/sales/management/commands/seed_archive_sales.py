import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sales.models import Party, Payment, PaymentAllocation, Sale, SaleLine
from sales.services import line_amounts, next_sale_number
from stock.models import Product

MARKER = 'Sahte arşiv kaydı'


class Command(BaseCommand):
    help = 'Geçmiş yıllara stoka dokunmadan sahte satış fişleri ekler.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50)

    def handle(self, *args, **options):
        count = max(0, int(options['count']))
        existing = Sale.objects.filter(notes=MARKER).count()
        needed = max(0, count - existing)
        if needed == 0:
            self.stdout.write(f'Zaten {existing} sahte arşiv fişi var.')
            return

        user = get_user_model().objects.order_by('id').first()
        parties = list(Party.objects.all())
        products = list(Product.objects.filter(is_active=True))
        if not user:
            raise CommandError('Kullanıcı yok.')
        if not parties:
            raise CommandError('Cari yok.')
        if not products:
            raise CommandError('Ürün yok.')

        year_bag = [2025] * 30 + [2024] * 12 + [2023] * 8
        random.shuffle(year_bag)
        while len(year_bag) < needed:
            year_bag.append(random.choice([2023, 2024, 2025]))

        created = 0
        for year in year_bag[:needed]:
            self._make_sale(user, parties, products, year)
            created += 1
        self.stdout.write(self.style.SUCCESS(f'{created} sahte arşiv fişi eklendi.'))

    @transaction.atomic
    def _make_sale(self, user, parties, products, year):
        start = date(year, 1, 1)
        span = (date(year, 12, 31) - start).days
        sale_date = start + timedelta(days=random.randint(0, span))
        party = random.choice(parties)
        vat_mode = random.choice([Sale.VAT_PLUS, Sale.VAT_INCLUDED])
        work_type = random.choice([Sale.WORK_DEVICE, Sale.WORK_SERVICE])
        issued = random.random() < 0.35
        line_count = random.randint(1, 3)
        parsed = []
        for product in random.sample(products, k=min(line_count, len(products))):
            qty = Decimal(str(random.randint(1, 3)))
            price = product.sale_price or Decimal('12500.00')
            net, vat, total = line_amounts(qty, price, product.vat_rate, vat_mode)
            parsed.append(
                {
                    'product': product,
                    'qty': qty,
                    'unit_price': price,
                    'vat_rate': product.vat_rate,
                    'net': net,
                    'vat': vat,
                    'total': total,
                }
            )
        subtotal = sum((item['net'] for item in parsed), Decimal('0.00'))
        vat_total = sum((item['vat'] for item in parsed), Decimal('0.00'))
        grand_total = sum((item['total'] for item in parsed), Decimal('0.00'))
        serial = next_sale_number(sale_date)
        sale = Sale.objects.create(
            number=serial,
            date=sale_date,
            party=party,
            work_type=work_type,
            vat_mode=vat_mode,
            invoice_status=Sale.INVOICE_YES if issued else Sale.INVOICE_NO,
            invoice_no=f'VDL{year}{random.randint(100, 999)}' if issued else '',
            notes=MARKER,
            subtotal=subtotal,
            vat_total=vat_total,
            grand_total=grand_total,
            created_by=user,
            updated_by=user,
        )
        for item in parsed:
            SaleLine.objects.create(
                sale=sale,
                product=item['product'],
                qty=item['qty'],
                unit_price=item['unit_price'],
                vat_rate=item['vat_rate'],
                line_net=item['net'],
                line_vat=item['vat'],
                line_total=item['total'],
            )
        roll = random.random()
        if roll < 0.25 or grand_total <= 0:
            return
        if roll < 0.7:
            amount = (grand_total * Decimal(str(random.choice([25, 40, 50, 75]))) / Decimal('100')).quantize(Decimal('0.01'))
        else:
            amount = grand_total
        if amount <= 0:
            return
        payment = Payment.objects.create(
            party=sale.party,
            method=random.choice([Payment.METHOD_CASH, Payment.METHOD_CARD, Payment.METHOD_TRANSFER]),
            amount=amount,
            date=sale_date,
            created_by=user,
        )
        PaymentAllocation.objects.create(payment=payment, sale=sale, amount=amount)
