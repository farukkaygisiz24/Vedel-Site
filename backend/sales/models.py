from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import models
from django.db.models import Sum


class Party(models.Model):
    KIND_REAL = 'real'
    KIND_LEGAL = 'legal'
    KIND_CHOICES = [
        (KIND_REAL, 'Gerçek kişi'),
        (KIND_LEGAL, 'Tüzel kişi'),
    ]

    kind = models.CharField('Tür', max_length=16, choices=KIND_CHOICES)
    number = models.CharField('No', max_length=24, unique=True)
    first_name = models.CharField('Ad', max_length=80, blank=True)
    last_name = models.CharField('Soyad', max_length=80, blank=True)
    national_id = models.CharField('T.C. kimlik no', max_length=11, blank=True)
    company_name = models.CharField('Unvan', max_length=160, blank=True)
    tax_office = models.CharField('Vergi dairesi', max_length=80, blank=True)
    tax_no = models.CharField('Vergi no', max_length=20, blank=True)
    email = models.EmailField('E-posta', blank=True)
    phone = models.CharField('Telefon', max_length=20)
    contact2_name = models.CharField('2. ulaşım adı soyadı', max_length=160, blank=True)
    phone2 = models.CharField('2. ulaşım telefon', max_length=20, blank=True)
    address = models.TextField('Adres')
    city = models.CharField('İl', max_length=80, blank=True)
    district = models.CharField('İlçe', max_length=80, blank=True)
    notes = models.TextField('Not', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='parties_created',
        verbose_name='Oluşturan',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cari'
        verbose_name_plural = 'Cariler'
        ordering = ['-created_at']

    def __str__(self):
        return self.display_name

    def get_absolute_url(self) -> str:
        from django.urls import reverse
        return reverse('portal-sales-customers-edit', kwargs={'number': self.number})

    @property
    def display_name(self) -> str:
        if self.kind == self.KIND_LEGAL:
            return self.company_name.strip() or 'Tüzel kişi'
        name = f'{self.first_name} {self.last_name}'.strip()
        return name or 'Gerçek kişi'

    @property
    def contact2_parts(self) -> list[str]:
        parts = []
        name = (self.contact2_name or '').strip()
        phone = (self.phone2 or '').strip()
        if name:
            parts.append(name)
        if phone:
            parts.append(phone)
        return parts


class Sale(models.Model):
    WORK_DEVICE = 'device_sale'
    WORK_SERVICE = 'maintenance'
    WORK_CHOICES = [
        (WORK_DEVICE, 'Cihaz satışı'),
        (WORK_SERVICE, 'Bakım / Servis'),
    ]
    VAT_PLUS = 'plus'
    VAT_INCLUDED = 'included'
    VAT_NONE = 'none'
    VAT_CHOICES = [
        (VAT_PLUS, '+ KDV'),
        (VAT_INCLUDED, 'KDV dahil'),
        (VAT_NONE, 'KDV yok'),
    ]
    INVOICE_NO = 'not_issued'
    INVOICE_YES = 'issued'
    INVOICE_CHOICES = [
        (INVOICE_NO, 'Kesilmedi'),
        (INVOICE_YES, 'Kesildi'),
    ]

    number = models.CharField('No', max_length=24, unique=True)
    date = models.DateField('Tarih')
    party = models.ForeignKey(
        Party,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name='Cari',
    )
    work_type = models.CharField('İş tipi', max_length=20, choices=WORK_CHOICES)
    vat_mode = models.CharField('KDV', max_length=16, choices=VAT_CHOICES)
    invoice_status = models.CharField(
        'Fatura',
        max_length=16,
        choices=INVOICE_CHOICES,
        default=INVOICE_NO,
    )
    invoice_no = models.CharField('Fatura no', max_length=40, blank=True)
    notes = models.TextField('Not', blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    vat_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sales_created',
        verbose_name='Oluşturan',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sales_updated',
        verbose_name='Güncelleyen',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Satış'
        verbose_name_plural = 'Satışlar'
        ordering = ['-date', '-id']

    def __str__(self):
        return self.number

    def get_absolute_url(self) -> str:
        from django.urls import reverse
        if self.is_archived:
            return reverse('portal-sales-archive-detail', kwargs={'number': self.number})
        return reverse('portal-sales-detail', kwargs={'number': self.number})

    def get_list_url(self) -> str:
        from urllib.parse import urlencode
        from django.urls import reverse
        if self.is_archived:
            return f"{reverse('portal-sales-archive')}?{urlencode({'year': self.date.year})}"
        return reverse('portal-sales')

    @property
    def is_archived(self) -> bool:
        from django.utils import timezone
        return self.date.year < timezone.localdate().year

    @property
    def paid_total(self) -> Decimal:
        total = self.payment_allocations.aggregate(s=Sum('amount'))['s']
        return total or Decimal('0.00')

    @property
    def remaining(self) -> Decimal:
        return self.grand_total - self.paid_total


class SaleLine(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Satış',
    )
    product = models.ForeignKey(
        'stock.Product',
        on_delete=models.PROTECT,
        related_name='sale_lines',
        verbose_name='Ürün',
        null=True,
        blank=True,
    )
    description = models.CharField('Açıklama', max_length=200, blank=True)
    qty = models.DecimalField('Adet', max_digits=12, decimal_places=2)
    unit_price = models.DecimalField('Birim fiyat', max_digits=12, decimal_places=2)
    cost_price = models.DecimalField('Alış', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    vat_rate = models.DecimalField('KDV %', max_digits=5, decimal_places=2)
    line_net = models.DecimalField(max_digits=12, decimal_places=2)
    line_vat = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Satış kalemi'
        verbose_name_plural = 'Satış kalemleri'

    def __str__(self):
        return f'{self.sale.number} · {self.display_name}'

    @property
    def display_name(self) -> str:
        if self.product_id:
            return self.product.display_name
        return self.description or 'İşçilik'


class Payment(models.Model):
    METHOD_CASH = 'cash'
    METHOD_CARD = 'card'
    METHOD_TRANSFER = 'transfer'
    METHOD_CHOICES = [
        (METHOD_CARD, 'Kart'),
        (METHOD_CASH, 'Nakit'),
        (METHOD_TRANSFER, 'Havale'),
    ]
    INSTALLMENT_CHOICES = [(1, 'Peşin')] + [(n, f'{n} taksit') for n in range(2, 13)]

    party = models.ForeignKey(
        Party,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Cari',
    )
    method = models.CharField('Yöntem', max_length=16, choices=METHOD_CHOICES)
    amount = models.DecimalField('Tutar', max_digits=12, decimal_places=2)
    date = models.DateField('Tarih')
    card_holder = models.CharField('Kart sahibi', max_length=120, blank=True)
    card_installments = models.PositiveSmallIntegerField(
        'Taksit',
        choices=INSTALLMENT_CHOICES,
        null=True,
        blank=True,
    )
    transfer_sender = models.CharField('Havale eden', max_length=120, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='payments_created',
        verbose_name='İşleyen',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ödeme'
        verbose_name_plural = 'Ödemeler'
        ordering = ['-date', '-id']

    def __str__(self):
        return f'{self.party.number} · {self.amount}'

    @property
    def installment_label(self) -> str:
        if not self.card_installments:
            return ''
        if self.card_installments == 1:
            return 'Peşin'
        return f'{self.card_installments} taksit'

    @property
    def monthly_installment(self) -> Decimal | None:
        if self.method != self.METHOD_CARD or not self.card_installments or self.card_installments < 2:
            return None
        return (self.amount / Decimal(self.card_installments)).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP,
        )

    @property
    def pay_name(self) -> str:
        if self.method == self.METHOD_CARD:
            return self.card_holder
        if self.method == self.METHOD_TRANSFER:
            return self.transfer_sender
        return ''

    @property
    def card_detail(self) -> str:
        parts = [part for part in (self.card_holder, self.installment_label) if part]
        return ' · '.join(parts)

    @property
    def pay_detail(self) -> str:
        if self.method == self.METHOD_CARD:
            return self.card_detail
        if self.method == self.METHOD_TRANSFER:
            return self.transfer_sender
        return ''


class PaymentAllocation(models.Model):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='allocations',
        verbose_name='Tahsilat',
    )
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='payment_allocations',
        verbose_name='Satış',
        null=True,
        blank=True,
    )
    job = models.ForeignKey(
        'service.Job',
        on_delete=models.CASCADE,
        related_name='payment_allocations',
        verbose_name='Servis işi',
        null=True,
        blank=True,
    )
    amount = models.DecimalField('Tutar', max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Tahsilat tahsisi'
        verbose_name_plural = 'Tahsilat tahsisleri'
        constraints = [
            models.CheckConstraint(
                name='payment_allocation_sale_xor_job',
                condition=(
                    models.Q(sale__isnull=False, job__isnull=True)
                    | models.Q(sale__isnull=True, job__isnull=False)
                ),
            ),
        ]

    def __str__(self):
        target = self.sale.number if self.sale_id else (self.job.number if self.job_id else '?')
        return f'{target} · {self.amount}'

    @property
    def slip_number(self) -> str:
        if self.sale_id:
            return self.sale.number
        if self.job_id:
            return self.job.number
        return ''

    @property
    def slip_url(self) -> str:
        if self.sale_id:
            return self.sale.get_absolute_url()
        if self.job_id:
            return self.job.get_absolute_url()
        return ''
