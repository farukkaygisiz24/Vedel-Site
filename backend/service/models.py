import re
import uuid
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Device(models.Model):
    INTERVAL_CHOICES = [
        (3, '3 ay'),
        (6, '6 ay'),
        (9, '9 ay'),
        (12, '12 ay'),
    ]

    party = models.ForeignKey(
        'sales.Party',
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name='Cari',
    )
    name = models.CharField('Cihaz', max_length=160)
    place = models.CharField('Konum', max_length=160, blank=True)
    interval_months = models.PositiveSmallIntegerField(
        'Bakım aralığı',
        choices=INTERVAL_CHOICES,
        default=6,
    )
    last_serviced_on = models.DateField('Son bakım', null=True, blank=True)
    next_due = models.DateField('Sonraki bakım', null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='devices_created',
        verbose_name='Oluşturan',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cihaz'
        verbose_name_plural = 'Cihazlar'
        ordering = ['name', 'id']

    def __str__(self):
        return self.name


class Job(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_OPEN = 'open'
    STATUS_SUBMITTED = 'submitted'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Bekleyen'),
        (STATUS_OPEN, 'Açık'),
        (STATUS_SUBMITTED, 'Teslim'),
        (STATUS_CLOSED, 'Kapalı'),
    ]
    VAT_PLUS = 'plus'
    VAT_INCLUDED = 'included'
    VAT_NONE = 'none'
    VAT_CHOICES = [
        (VAT_PLUS, '+ KDV'),
        (VAT_INCLUDED, 'KDV dahil'),
        (VAT_NONE, 'KDV yok'),
    ]

    number = models.CharField('No', max_length=24, unique=True)
    date = models.DateField('Tarih')
    time = models.TimeField('Saat', null=True, blank=True)
    party = models.ForeignKey(
        'sales.Party',
        on_delete=models.PROTECT,
        related_name='service_jobs',
        verbose_name='Cari',
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs',
        verbose_name='Cihaz',
    )
    vat_mode = models.CharField('KDV', max_length=16, choices=VAT_CHOICES, default=VAT_PLUS)
    status = models.CharField(
        'Durum',
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    sale = models.OneToOneField(
        'sales.Sale',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='service_job',
        verbose_name='Satış fişi',
    )
    assignee = models.ForeignKey(
        'crew.CrewMember',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs',
        verbose_name='Personel',
    )
    assign_all = models.BooleanField('Tüm personel', default=False)
    notes = models.TextField('Not', blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    vat_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cost_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    list_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    list_vat = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    list_grand = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_rate = models.DecimalField('İndirim %', max_digits=8, decimal_places=4, default=Decimal('0.0000'))
    submitted_at = models.DateTimeField('Teslim', null=True, blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs_submitted',
        verbose_name='Teslim eden',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='jobs_created',
        verbose_name='Oluşturan',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='jobs_updated',
        verbose_name='Güncelleyen',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Servis işi'
        verbose_name_plural = 'Servis işleri'
        ordering = ['-date', '-id']

    def __str__(self):
        return self.number

    def get_absolute_url(self) -> str:
        from django.urls import reverse
        return reverse('portal-service-job-detail', kwargs={'number': self.number})

    def get_field_url(self) -> str:
        from django.urls import reverse
        return reverse('portal-field-job', kwargs={'number': self.number})

    @property
    def is_pending(self) -> bool:
        return self.status == self.STATUS_PENDING

    @property
    def is_open(self) -> bool:
        return self.status == self.STATUS_OPEN

    @property
    def is_submitted(self) -> bool:
        return self.status == self.STATUS_SUBMITTED

    @property
    def is_closed(self) -> bool:
        return self.status == self.STATUS_CLOSED

    @property
    def is_overdue(self) -> bool:
        from django.utils import timezone
        return self.status == self.STATUS_OPEN and self.date < timezone.localdate()

    @property
    def is_waiting(self) -> bool:
        return self.is_pending or self.is_overdue

    @property
    def is_mount(self) -> bool:
        return bool(self.sale_id)

    @property
    def kind_label(self) -> str:
        return 'Montaj' if self.is_mount else 'Servis'

    @property
    def display_number(self) -> str:
        sale = getattr(self, 'sale', None)
        if sale is not None and sale.number:
            return sale.number
        return self.number

    @property
    def assignee_label(self) -> str:
        if self.assignee_id:
            return self.assignee.display_name
        if self.assign_all:
            return 'Hepsi'
        return ''

    @property
    def device_summary(self) -> str:
        if self.is_mount:
            packs = list(self.sold_packs.all())
            if not packs:
                return '—'
            labels = [pack.label for pack in packs[:2] if pack.label]
            extra = len(packs) - 2
            text = ' · '.join(labels) if labels else '—'
            if extra > 0:
                text += f' +{extra}'
            return text
        if self.device_id:
            return self.device.name
        return '—'

    @property
    def profit(self) -> Decimal:
        return self.grand_total - self.cost_total

    @property
    def is_organic(self) -> bool:
        return self.sale_id is None

    @property
    def paid_total(self) -> Decimal:
        total = self.payment_allocations.aggregate(s=Sum('amount'))['s']
        return total or Decimal('0.00')

    @property
    def remaining(self) -> Decimal:
        return self.grand_total - self.paid_total

    @property
    def discount_amount(self) -> Decimal:
        value = (self.list_grand or Decimal('0.00')) - (self.grand_total or Decimal('0.00'))
        return value.quantize(Decimal('0.01')) if value else Decimal('0.00')


class JobLine(models.Model):
    KIND_LABOR = 'labor'
    KIND_PART = 'part'
    KIND_CHOICES = [
        (KIND_LABOR, 'İşçilik'),
        (KIND_PART, 'Parça'),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='İş',
    )
    kind = models.CharField('Tür', max_length=16, choices=KIND_CHOICES)
    product = models.ForeignKey(
        'stock.Product',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='job_lines',
        verbose_name='Ürün',
    )
    description = models.CharField('Açıklama', max_length=200, blank=True)
    qty = models.DecimalField('Adet', max_digits=12, decimal_places=2)
    unit_price = models.DecimalField('Birim fiyat', max_digits=12, decimal_places=2)
    list_unit_price = models.DecimalField('Liste birim', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cost_price = models.DecimalField('Alış', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    vat_rate = models.DecimalField('KDV %', max_digits=5, decimal_places=2)
    line_net = models.DecimalField(max_digits=12, decimal_places=2)
    line_vat = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'İş kalemi'
        verbose_name_plural = 'İş kalemleri'

    def __str__(self):
        return f'{self.job.number} · {self.display_name}'

    @property
    def display_name(self) -> str:
        if self.product_id:
            return self.product.display_name
        return self.description or 'İşçilik'

    @property
    def line_cost(self) -> Decimal:
        return (self.cost_price or Decimal('0.00')) * (self.qty or Decimal('0.00'))


def job_photo_to(instance, filename):
    ext = Path(filename or '').suffix.lower() or '.jpg'
    number = instance.job.number if getattr(instance, 'job_id', None) else 'tmp'
    return f'jobs/{number}/field/{uuid.uuid4().hex}{ext}'


def job_unit_photo_to(instance, filename):
    ext = Path(filename or '').suffix.lower() or '.jpg'
    job = getattr(instance, 'job', None)
    if job is None and getattr(instance, 'pack_id', None):
        job = instance.pack.job
    if job is None and getattr(instance, 'unit_id', None):
        job = instance.unit.job
    number = job.number if job else 'tmp'
    return f'jobs/{number}/{uuid.uuid4().hex}{ext}'


class JobSoldPack(models.Model):
    KIND_SPLIT = 'split'
    KIND_MULTI = 'multi'
    KIND_CHOICES = [
        (KIND_SPLIT, 'Split'),
        (KIND_MULTI, 'Multi'),
    ]
    CARE_INTERVALS = [
        (3, '3 ay'),
        (6, '6 ay'),
        (9, '9 ay'),
        (12, '12 ay'),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='sold_packs',
        verbose_name='İş',
    )
    kind = models.CharField('Tip', max_length=16, choices=KIND_CHOICES)
    source_key = models.CharField('Kaynak', max_length=80)
    sort = models.PositiveSmallIntegerField('Sıra', default=0)
    outdoor_sale_line = models.ForeignKey(
        'sales.SaleLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_packs',
        verbose_name='Dış ünite kalemi',
    )
    outdoor_product = models.ForeignKey(
        'stock.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_packs',
        verbose_name='Dış ünite ürün',
    )
    outdoor_name = models.CharField('Dış ünite', max_length=160, blank=True)
    outdoor_serial = models.CharField('Dış ünite seri no', max_length=80, blank=True)
    outdoor_index = models.PositiveSmallIntegerField('Dış sıra', default=0)
    interval_months = models.PositiveSmallIntegerField(
        'Bakım aralığı',
        choices=CARE_INTERVALS,
        default=6,
    )
    last_serviced_on = models.DateField('Son bakım', null=True, blank=True)
    next_due = models.DateField('Sonraki bakım', null=True, blank=True)

    class Meta:
        verbose_name = 'Cihaz paketi'
        verbose_name_plural = 'Cihaz paketleri'
        ordering = ['sort', 'id']
        unique_together = [('job', 'source_key')]

    def __str__(self):
        return f'{self.job.number} · {self.get_kind_display()}'

    @property
    def brand(self) -> str:
        indoor = self.units.order_by('id').first()
        if indoor and indoor.brand:
            return indoor.brand
        product = self.outdoor_product
        if product and product.brand:
            return product.brand
        return '—'

    @property
    def indoor_units(self):
        return list(self.units.order_by('id'))

    @property
    def care_rowspan(self) -> int:
        count = self.units.count() + (1 if self.outdoor_name else 0)
        return max(count, 1)

    @property
    def photo_items(self):
        return list(self.photos.order_by('sort', 'pk'))

    @property
    def photo_urls(self) -> list[str]:
        return [item.file_url for item in self.photo_items if item.file_url]

    @property
    def photo_count(self) -> int:
        return self.photos.count()

    @property
    def album_zip_name(self) -> str:
        party = (self.job.party.display_name if self.job.party_id else '').strip()
        stem = f'{self.job.number}-{party}' if party else self.job.number
        stem = re.sub(r'[\\/:*?"<>|]+', ' ', stem)
        stem = re.sub(r'\s+', ' ', stem).strip(' .')
        return f'{stem}.zip'

    @property
    def mount_items(self):
        return list(self.materials.select_related('product').order_by('id'))

    @property
    def label(self) -> str:
        if self.kind == self.KIND_MULTI:
            return f'{self.brand} · Multi'
        return self.brand


class JobSoldUnit(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='sold_units',
        verbose_name='İş',
    )
    sale_line = models.ForeignKey(
        'sales.SaleLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_units',
        verbose_name='Satış kalemi',
    )
    product = models.ForeignKey(
        'stock.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_units',
        verbose_name='Ürün',
    )
    pack = models.ForeignKey(
        JobSoldPack,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='units',
        verbose_name='Paket',
    )
    brand = models.CharField('Marka', max_length=120, blank=True)
    model = models.CharField('Model', max_length=160)
    outdoor_name = models.CharField('Dış ünite', max_length=160, blank=True)
    line_index = models.PositiveSmallIntegerField('Sıra', default=0)
    CARE_INTERVALS = [
        (3, '3 ay'),
        (6, '6 ay'),
        (9, '9 ay'),
        (12, '12 ay'),
    ]

    room = models.CharField('Oda', max_length=80, blank=True)
    serial = models.CharField('İç ünite seri no', max_length=80, blank=True)
    outdoor_serial = models.CharField('Dış ünite seri no', max_length=80, blank=True)
    interval_months = models.PositiveSmallIntegerField(
        'Bakım aralığı',
        choices=CARE_INTERVALS,
        default=6,
    )
    last_serviced_on = models.DateField('Son bakım', null=True, blank=True)
    next_due = models.DateField('Sonraki bakım', null=True, blank=True)

    class Meta:
        verbose_name = 'Satılan cihaz'
        verbose_name_plural = 'Satılan cihazlar'
        ordering = ['id']
        unique_together = [('job', 'sale_line', 'line_index')]

    def __str__(self):
        return f'{self.job.number} · {self.model}'

    @property
    def has_outdoor(self) -> bool:
        return bool(self.outdoor_name)

    @property
    def photo_items(self):
        return list(self.photos.order_by('sort', 'pk'))

    @property
    def photo_urls(self) -> list[str]:
        return [item.file_url for item in self.photo_items if item.file_url]

    @property
    def photo_count(self) -> int:
        return self.photos.count()

    @property
    def album_zip_name(self) -> str:
        party = (self.job.party.display_name if self.job.party_id else '').strip()
        stem = f'{self.job.number}-{party}' if party else self.job.number
        stem = re.sub(r'[\\/:*?"<>|]+', ' ', stem)
        stem = re.sub(r'\s+', ' ', stem).strip(' .')
        return f'{stem}.zip'

    @property
    def mount_items(self):
        return list(self.materials.select_related('product').order_by('id'))


class JobSoldUnitPhoto(models.Model):
    pack = models.ForeignKey(
        JobSoldPack,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='photos',
        verbose_name='Paket',
    )
    unit = models.ForeignKey(
        JobSoldUnit,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='photos',
        verbose_name='Cihaz',
    )
    image = models.FileField('Görsel', upload_to=job_unit_photo_to)
    sort = models.PositiveSmallIntegerField('Sıra', default=0)

    class Meta:
        verbose_name = 'Cihaz görseli'
        verbose_name_plural = 'Cihaz görselleri'
        ordering = ['sort', 'id']

    def __str__(self):
        return f'{self.pack_id or self.unit_id} · {self.pk}'

    @property
    def file_url(self) -> str:
        if not self.image:
            return ''
        job = self.pack.job if self.pack_id else self.unit.job
        if self.pack_id:
            return f'{job.get_absolute_url()}?group={self.pack_id}&photo={self.pk}'
        return f'{job.get_absolute_url()}?unit={self.unit_id}&photo={self.pk}'


class JobSoldUnitMaterial(models.Model):
    pack = models.ForeignKey(
        JobSoldPack,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='materials',
        verbose_name='Paket',
    )
    unit = models.ForeignKey(
        JobSoldUnit,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='materials',
        verbose_name='Cihaz',
    )
    product = models.ForeignKey(
        'stock.Product',
        on_delete=models.PROTECT,
        related_name='job_unit_materials',
        verbose_name='Ürün',
    )
    qty = models.DecimalField('Adet', max_digits=12, decimal_places=2)
    name = models.CharField('Ürün adı', max_length=200)
    unit_label = models.CharField('Birim', max_length=16, blank=True)

    class Meta:
        verbose_name = 'Montaj malzemesi'
        verbose_name_plural = 'Montaj malzemeleri'
        ordering = ['id']

    def __str__(self):
        return f'{self.name} · {self.qty}'


class JobPhoto(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='İş',
    )
    image = models.FileField('Görsel', upload_to=job_photo_to)
    sort = models.PositiveSmallIntegerField('Sıra', default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='job_photos_created',
        verbose_name='Ekleyen',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'İş görseli'
        verbose_name_plural = 'İş görselleri'
        ordering = ['sort', 'id']

    def __str__(self):
        return f'{self.job.number} · {self.pk}'

    @property
    def file_url(self) -> str:
        if not self.image:
            return ''
        return f'{self.job.get_field_url()}?photo={self.pk}'


@receiver(pre_delete, sender=JobSoldUnitPhoto)
def _purge_unit_photo_file(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


@receiver(pre_delete, sender=JobPhoto)
def _purge_job_photo_file(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
