from django.conf import settings
from django.db import migrations


MOUNT_NAME = 'Klima Montaj Malzemesi'
MOUNT_SLUG = 'klima-montaj-malzemesi'
MOUNT_PREFIX = 'KMM'


def seed_mount_category(apps, schema_editor):
    Category = apps.get_model('stock', 'Category')
    User = apps.get_model(settings.AUTH_USER_MODEL)
    if Category.objects.filter(slug=MOUNT_SLUG).exists():
        return
    if Category.objects.filter(name=MOUNT_NAME).exists():
        item = Category.objects.filter(name=MOUNT_NAME).first()
        if item and not Category.objects.filter(slug=MOUNT_SLUG).exists():
            item.slug = MOUNT_SLUG
            item.save(update_fields=['slug'])
        return
    if Category.objects.filter(sku_prefix=MOUNT_PREFIX).exists():
        return
    user = (
        User.objects.filter(is_superuser=True).order_by('pk').first()
        or User.objects.filter(is_staff=True).order_by('pk').first()
        or User.objects.order_by('pk').first()
    )
    if user is None:
        return
    Category.objects.create(
        name=MOUNT_NAME,
        slug=MOUNT_SLUG,
        sku_prefix=MOUNT_PREFIX,
        brand='',
        created_by=user,
    )


def unseed_mount_category(apps, schema_editor):
    Category = apps.get_model('stock', 'Category')
    Product = apps.get_model('stock', 'Product')
    item = Category.objects.filter(slug=MOUNT_SLUG, sku_prefix=MOUNT_PREFIX).first()
    if item is None:
        return
    if Product.objects.filter(category=item).exists():
        return
    item.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0012_stockmovement_reason_job'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(seed_mount_category, unseed_mount_category),
    ]
