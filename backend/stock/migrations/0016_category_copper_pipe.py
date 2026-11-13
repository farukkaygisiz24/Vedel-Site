from decimal import Decimal

from django.conf import settings
from django.db import migrations, models


COPPER_NAME = 'Bakır Boru'
COPPER_SLUG = 'bakir-boru'
COPPER_PREFIX = 'BAK'
MOUNT_SLUG = 'klima-montaj-malzemesi'


def seed_copper_category(apps, schema_editor):
    Category = apps.get_model('stock', 'Category')
    Product = apps.get_model('stock', 'Product')
    User = apps.get_model(settings.AUTH_USER_MODEL)

    copper = Category.objects.filter(slug=COPPER_SLUG).first()
    if copper is None:
        copper = Category.objects.filter(sku_prefix=COPPER_PREFIX).first()
    if copper is None:
        copper = Category.objects.filter(name=COPPER_NAME).first()
    if copper is None:
        user = (
            User.objects.filter(is_superuser=True).order_by('pk').first()
            or User.objects.filter(is_staff=True).order_by('pk').first()
            or User.objects.order_by('pk').first()
        )
        if user is None:
            return
        copper = Category.objects.create(
            name=COPPER_NAME,
            slug=COPPER_SLUG,
            sku_prefix=COPPER_PREFIX,
            brand='',
            is_klima=False,
            is_copper_pipe=True,
            included_copper_meters=Decimal('0.00'),
            created_by=user,
        )
    else:
        changed = []
        if copper.slug != COPPER_SLUG and not Category.objects.filter(slug=COPPER_SLUG).exclude(pk=copper.pk).exists():
            copper.slug = COPPER_SLUG
            changed.append('slug')
        if not copper.is_copper_pipe:
            copper.is_copper_pipe = True
            changed.append('is_copper_pipe')
        if copper.is_klima:
            copper.is_klima = False
            changed.append('is_klima')
        if changed:
            copper.save(update_fields=changed)

    mount = Category.objects.filter(slug=MOUNT_SLUG).first()
    if mount is None:
        return
    qs = Product.objects.filter(category=mount, name__icontains='Bakır Boru')
    qs.update(category=copper)


def unseed_copper_category(apps, schema_editor):
    Category = apps.get_model('stock', 'Category')
    Product = apps.get_model('stock', 'Product')
    copper = Category.objects.filter(slug=COPPER_SLUG).first()
    if copper is None:
        return
    mount = Category.objects.filter(slug=MOUNT_SLUG).first()
    if mount is not None:
        Product.objects.filter(category=copper).update(category=mount)
    if not Product.objects.filter(category=copper).exists():
        copper.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0015_category_klima_product_kind'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='included_copper_meters',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.00'),
                max_digits=8,
                verbose_name='Split dahil bakır (mt)',
            ),
        ),
        migrations.AddField(
            model_name='category',
            name='is_copper_pipe',
            field=models.BooleanField(default=False, verbose_name='Bakır boru'),
        ),
        migrations.RunPython(seed_copper_category, unseed_copper_category),
    ]
