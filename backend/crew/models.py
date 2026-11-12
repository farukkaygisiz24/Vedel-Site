import uuid
from pathlib import Path

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


def crew_doc_upload_to(instance, filename):
    ext = Path(filename or '').suffix.lower()
    number = instance.member.number if instance.member_id else 'tmp'
    return f'crew/{number}/{uuid.uuid4().hex}{ext}'


class CrewMember(models.Model):
    number = models.CharField('No', max_length=24, unique=True)
    first_name = models.CharField('Ad', max_length=80)
    last_name = models.CharField('Soyad', max_length=80)
    national_id = models.CharField('T.C. kimlik no', max_length=11, blank=True)
    phone = models.CharField('Telefon', max_length=20)
    phone2 = models.CharField('2. telefon', max_length=20, blank=True)
    email = models.EmailField('E-posta', blank=True)
    title = models.CharField('Unvan', max_length=80, blank=True)
    address = models.TextField('Ev adresi', blank=True)
    city = models.CharField('İl', max_length=80, blank=True)
    district = models.CharField('İlçe', max_length=80, blank=True)
    notes = models.TextField('Not', blank=True)
    is_active = models.BooleanField('Aktif', default=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crew_profile',
        verbose_name='Kullanıcı',
    )
    printer_mac = models.CharField('Yazıcı MAC', max_length=32, blank=True)
    printer_ip = models.CharField('Yazıcı IP', max_length=45, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='crew_created',
        verbose_name='Oluşturan',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Personel'
        verbose_name_plural = 'Personel'
        ordering = ['first_name', 'last_name', 'id']

    def __str__(self):
        return self.display_name

    def get_absolute_url(self) -> str:
        from django.urls import reverse
        return reverse('portal-crew-item', kwargs={'number': self.number})

    @property
    def display_name(self) -> str:
        name = f'{self.first_name} {self.last_name}'.strip()
        return name or self.number

    @property
    def place_line(self) -> str:
        parts = [part for part in (self.district, self.city) if part]
        return ' / '.join(parts)


class CrewDocument(models.Model):
    member = models.ForeignKey(
        CrewMember,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Personel',
    )
    title = models.CharField('Evrak', max_length=160)
    original_name = models.CharField('Dosya adı', max_length=200, blank=True)
    file = models.FileField('Dosya', upload_to=crew_doc_upload_to, blank=True)
    expires_on = models.DateField('Son tarih')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='crew_docs_created',
        verbose_name='Oluşturan',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Evrak'
        verbose_name_plural = 'Evraklar'
        ordering = ['expires_on', 'title']

    def __str__(self):
        return f'{self.member.display_name} · {self.title}'

    def get_file_url(self) -> str:
        if not self.file:
            return ''
        return f'{self.member.get_absolute_url()}?file={self.pk}'


@receiver(pre_delete, sender=CrewDocument)
def _purge_crew_file(sender, instance, **kwargs):
    folder = None
    if instance.member_id:
        folder = Path(settings.MEDIA_ROOT) / 'crew' / instance.member.number
    if instance.file:
        instance.file.delete(save=False)
    if folder and folder.is_dir() and not any(folder.iterdir()):
        folder.rmdir()
