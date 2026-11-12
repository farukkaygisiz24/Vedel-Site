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
