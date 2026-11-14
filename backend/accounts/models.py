import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models


class Customer(AbstractUser):
    ROLE_SALES = 'sales'
    ROLE_SERVICE_LEAD = 'service_lead'
    ROLE_SERVICE = 'service'
    ROLE_CHOICES = [
        (ROLE_SALES, 'Satış'),
        (ROLE_SERVICE_LEAD, 'Servis yetkilisi'),
        (ROLE_SERVICE, 'Servis'),
    ]

    phone = models.CharField('Telefon', max_length=20, blank=True)
    role = models.CharField('Rol', max_length=20, blank=True, choices=ROLE_CHOICES)
    stock_categories = models.ManyToManyField(
        'stock.Category',
        blank=True,
        related_name='portal_users',
        verbose_name='Depo kategorileri',
    )

    class Meta:
        verbose_name = 'Müşteri'
        verbose_name_plural = 'Müşteriler'

    def __str__(self):
        return self.username

    def get_absolute_url(self) -> str:
        from django.urls import reverse
        return reverse('portal-users-item', kwargs={'username': self.username})

    @property
    def display_name(self) -> str:
        name = f'{self.first_name} {self.last_name}'.strip()
        return name or self.username

    @property
    def role_label(self) -> str:
        if self.is_superuser:
            return 'Yönetici'
        return dict(self.ROLE_CHOICES).get(self.role, 'Sınırlı')

    @property
    def can_sales(self) -> bool:
        return self.is_superuser or (self.is_staff and self.role in {self.ROLE_SALES, self.ROLE_SERVICE_LEAD})

    @property
    def can_service_lead(self) -> bool:
        return self.is_superuser or (self.is_staff and self.role == self.ROLE_SERVICE_LEAD)

    @property
    def can_service_field(self) -> bool:
        return self.is_staff and self.role == self.ROLE_SERVICE

    @property
    def can_service(self) -> bool:
        return self.can_service_lead or self.can_service_field

    @property
    def can_stock(self) -> bool:
        return self.can_sales or self.can_service_field

    @property
    def can_stock_manage(self) -> bool:
        return self.can_sales

    @property
    def can_users(self) -> bool:
        return self.can_service_lead

    @property
    def can_crew(self) -> bool:
        return self.can_service_lead


class AuthToken(models.Model):
    key = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='tokens',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Oturum anahtarı'
        verbose_name_plural = 'Oturum anahtarları'

    def __str__(self):
        return f'{self.user.username} · {self.key[:8]}'

    @classmethod
    def issue(cls, user: Customer) -> 'AuthToken':
        return cls.objects.create(user=user, key=secrets.token_hex(32))


class Notification(models.Model):
    KIND_SALE_NEW = 'sale_new'
    KIND_JOB_NEW = 'job_new'
    KIND_JOB_SCHEDULED = 'job_scheduled'
    KIND_JOB_SUBMITTED = 'job_submitted'
    KIND_JOB_ASSIGNED = 'job_assigned'
    KIND_JOB_RESCHEDULED = 'job_rescheduled'
    KIND_JOB_UNASSIGNED = 'job_unassigned'
    KIND_JOB_CANCELLED = 'job_cancelled'
    KIND_MAINTENANCE = 'maintenance'
    KIND_DIGEST = 'digest'
    KIND_CHOICES = [
        (KIND_SALE_NEW, 'Yeni satış'),
        (KIND_JOB_NEW, 'Yeni servis işi'),
        (KIND_JOB_SCHEDULED, 'Montaj tarihi'),
        (KIND_JOB_SUBMITTED, 'İş teslim edildi'),
        (KIND_JOB_ASSIGNED, 'İş atandı'),
        (KIND_JOB_RESCHEDULED, 'Tarih değişti'),
        (KIND_JOB_UNASSIGNED, 'İş alındı'),
        (KIND_JOB_CANCELLED, 'İş iptal'),
        (KIND_MAINTENANCE, 'Bakım'),
        (KIND_DIGEST, 'Günlük özet'),
    ]

    recipient = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    kind = models.CharField(max_length=24, choices=KIND_CHOICES)
    title = models.CharField(max_length=160)
    body = models.CharField(max_length=300, blank=True)
    url = models.CharField(max_length=300, blank=True)
    actor = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    dedupe_key = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at', '-id']
        indexes = [models.Index(fields=['recipient', 'read_at'], name='notif_recipient_read')]
        verbose_name = 'Bildirim'
        verbose_name_plural = 'Bildirimler'

    def __str__(self):
        return f'{self.recipient_id} · {self.title}'

    @property
    def is_read(self) -> bool:
        return self.read_at is not None


class PushSubscription(models.Model):
    user = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
    )
    endpoint = models.URLField(max_length=600, unique=True)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=100)
    user_agent = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_ok_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Push aboneliği'
        verbose_name_plural = 'Push abonelikleri'

    def __str__(self):
        return f'{self.user_id} · {self.endpoint[:40]}'
