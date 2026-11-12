from django.conf import settings
from django.db import migrations


def seed_merkez_depo(apps, schema_editor):
    Category = apps.get_model('stock', 'Category')
    Product = apps.get_model('stock', 'Product')
    User = apps.get_model(settings.AUTH_USER_MODEL)

    user = (
        User.objects.filter(is_superuser=True).order_by('pk').first()
        or User.objects.filter(is_staff=True).order_by('pk').first()
        or User.objects.order_by('pk').first()
    )
    merkez = Category.objects.filter(name='MERKEZ DEPO').first()
    stk = Category.objects.filter(sku_prefix='STK').first()

    if merkez is None and stk is not None:
        merkez = stk
        merkez.name = 'MERKEZ DEPO'
        if not Category.objects.filter(slug='merkez-depo').exclude(pk=merkez.pk).exists():
            merkez.slug = 'merkez-depo'
        merkez.save()
    elif merkez is None and user is not None and stk is None:
        slug = 'merkez-depo'
        serial = 2
        while Category.objects.filter(slug=slug).exists():
            slug = f'merkez-depo-{serial}'
            serial += 1
        merkez = Category.objects.create(
            name='MERKEZ DEPO',
            slug=slug,
            sku_prefix='STK',
            brand='',
            created_by=user,
        )
    elif merkez is not None and merkez.sku_prefix != 'STK' and stk is None:
        merkez.sku_prefix = 'STK'
        merkez.save(update_fields=['sku_prefix'])

    if merkez is None:
        orphan = Product.objects.filter(category__isnull=True).first()
        if orphan is not None:
            owner = user or User.objects.filter(pk=orphan.created_by_id).first()
            if owner is None:
                raise RuntimeError('Merkez Depo için kullanıcı yok.')
            slug = 'merkez-depo'
            serial = 2
            while Category.objects.filter(slug=slug).exists():
                slug = f'merkez-depo-{serial}'
                serial += 1
            prefix = 'STK'
            if Category.objects.filter(sku_prefix=prefix).exists():
                prefix = 'DEPO'
            merkez = Category.objects.create(
                name='MERKEZ DEPO',
                slug=slug,
                sku_prefix=prefix,
                brand='',
                created_by=owner,
            )

    if merkez is not None:
        Product.objects.filter(category__isnull=True).update(category_id=merkez.pk)
    else:
        first = Category.objects.order_by('pk').first()
        if first is not None:
            Product.objects.filter(category__isnull=True).update(category_id=first.pk)

    if Product.objects.filter(category__isnull=True).exists():
        raise RuntimeError('Kategorisiz ürün kaldı; Merkez Depo oluşturulamadı.')


def unseed_merkez_depo(apps, schema_editor):
    Product = apps.get_model('stock', 'Product')
    Category = apps.get_model('stock', 'Category')
    merkez = Category.objects.filter(name='MERKEZ DEPO', sku_prefix='STK').first()
    if merkez is None:
        return
    Product.objects.filter(category=merkez).update(category=None)
    if not merkez.products.exists():
        merkez.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0005_category_brand'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(seed_merkez_depo, unseed_merkez_depo),
    ]
