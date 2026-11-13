from decimal import Decimal

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Category(models.Model):
    name = models.CharField('Kategori', max_length=80, unique=True)
    slug = models.SlugField('Kısa ad', max_length=80, unique=True)
    sku_prefix = models.CharField(
        'Stok öneki',
        max_length=6,
        unique=True,
        validators=[RegexValidator(r'^[A-Z]{2,6}$', 'Stok öneki 2–6 harf olmalı.')],
    )
    brand = models.CharField('Marka', max_length=80, blank=True)
    is_klima = models.BooleanField('Klima', default=False)
    is_copper_pipe = models.BooleanField('Bakır boru', default=False)
    included_copper_meters = models.DecimalField(
        'Split dahil bakır (mt)',
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='stock_categories_created',
        verbose_name='Oluşturan',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField('Stok kodu', max_length=40, unique=True)
    brand = models.CharField('Marka', max_length=80, blank=True)
    name = models.CharField('Ürün adı', max_length=160)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Kategori',
    )
    unit = models.CharField('Birim', max_length=16, default='adet')
    vat_rate = models.DecimalField('KDV %', max_digits=5, decimal_places=2, default=Decimal('20.00'))
    sale_price = models.DecimalField('Satış fiyatı', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    buy_price = models.DecimalField('Alış fiyatı', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    stock_qty = models.DecimalField('Stok', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    alert_qty = models.DecimalField(
        'Kritik eşik',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    alert_on = models.BooleanField('Hatırlat', default=False)
    KIND_NONE = ''
    KIND_SPLIT = 'split'
    KIND_MULTI_INDOOR = 'multi_indoor'
    KIND_MULTI_OUTDOOR = 'multi_outdoor'
    KIND_CHOICES = [
        (KIND_NONE, 'Cihaz değil'),
        (KIND_SPLIT, 'Split'),
        (KIND_MULTI_INDOOR, 'Multi iç ünite'),
        (KIND_MULTI_OUTDOOR, 'Multi dış ünite'),
    ]
    is_device = models.BooleanField('Cihaz', default=False)
    device_kind = models.CharField(
        'Cihaz tipi',
        max_length=16,
        choices=KIND_CHOICES,
        blank=True,
        default=KIND_NONE,
    )
    outdoor_name = models.CharField('Dış ünite', max_length=160, blank=True)
    outdoor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='indoor_units',
        verbose_name='Dış ünite stoku',
    )
    is_active = models.BooleanField('Aktif', default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='products_created',
        verbose_name='Oluşturan',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        ordering = ['name']

    def __str__(self):
        return f'{self.sku} · {self.display_name}'

    def get_absolute_url(self) -> str:
        from django.urls import reverse
        return reverse('portal-stock-item', kwargs={'number': self.sku})

    @property
    def display_name(self) -> str:
        brand = (self.brand or '').strip()
        if brand:
            return f'{brand} · {self.name}'
        return self.name

    @property
    def is_split(self) -> bool:
        return self.device_kind == self.KIND_SPLIT

    @property
    def is_multi_indoor(self) -> bool:
        return self.device_kind == self.KIND_MULTI_INDOOR

    @property
    def is_multi_outdoor(self) -> bool:
        return self.device_kind == self.KIND_MULTI_OUTDOOR

    @property
    def profit(self):
        return (self.sale_price or Decimal('0.00')) - (self.buy_price or Decimal('0.00'))

    @property
    def is_low(self) -> bool:
        if not self.alert_on:
            return False
        limit = self.alert_qty if self.alert_qty is not None else Decimal('0.00')
        return (self.stock_qty or Decimal('0.00')) <= limit


class StockMovement(models.Model):
    REASON_SALE = 'sale'
    REASON_IN = 'in'
    REASON_ADJUST = 'adjust'
    REASON_JOB = 'job'
    REASON_CHOICES = [
        (REASON_SALE, 'Satış'),
        (REASON_IN, 'Stok girişi'),
        (REASON_ADJUST, 'Düzeltme'),
        (REASON_JOB, 'Montaj'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='movements',
        verbose_name='Ürün',
    )
    qty = models.DecimalField('Adet', max_digits=12, decimal_places=2)
    reason = models.CharField('Neden', max_length=16, choices=REASON_CHOICES)
    buy_price = models.DecimalField('Alış', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    supplier = models.ForeignKey(
        'sales.Party',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_supplies',
        verbose_name='Tedarikçi',
    )
    sale_line = models.ForeignKey(
        'sales.SaleLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_movements',
        verbose_name='Satış kalemi',
    )
    job = models.ForeignKey(
        'service.Job',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_movements',
        verbose_name='Servis işi',
    )
    note = models.CharField('Not', max_length=200, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='stock_movements',
        verbose_name='İşleyen',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Stok hareketi'
        verbose_name_plural = 'Stok hareketleri'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.sku} {self.qty}'
