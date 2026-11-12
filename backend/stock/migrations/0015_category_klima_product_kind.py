from django.db import migrations, models


def seed_klima_kinds(apps, schema_editor):
    Category = apps.get_model('stock', 'Category')
    Product = apps.get_model('stock', 'Product')
    mhi = Category.objects.filter(sku_prefix='MHI').first()
    if mhi:
        mhi.is_klima = True
        mhi.save(update_fields=['is_klima'])
    mapping = {
        'MHI-0001': ('split', 'SRC25ZSP-W'),
        'MHI-0002': ('multi_indoor', ''),
        'MHI-0003': ('multi_outdoor', ''),
    }
    for sku, (kind, outdoor) in mapping.items():
        item = Product.objects.filter(sku=sku).first()
        if not item:
            continue
        item.device_kind = kind
        item.is_device = True
        if outdoor:
            item.outdoor_name = outdoor
            item.outdoor_id = None
        else:
            item.outdoor_name = ''
            item.outdoor_id = None
        item.save(update_fields=['device_kind', 'is_device', 'outdoor_name', 'outdoor_id'])
    for item in Product.objects.filter(is_device=True).exclude(device_kind__in=['split', 'multi_indoor', 'multi_outdoor']):
        item.device_kind = 'split'
        item.save(update_fields=['device_kind'])
        if item.category_id:
            Category.objects.filter(pk=item.category_id).update(is_klima=True)


def unseed_klima_kinds(apps, schema_editor):
    Category = apps.get_model('stock', 'Category')
    Product = apps.get_model('stock', 'Product')
    Category.objects.update(is_klima=False)
    Product.objects.update(device_kind='')


class Migration(migrations.Migration):
    dependencies = [
        ('stock', '0014_stockmovement_job'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_klima',
            field=models.BooleanField('Klima', default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='device_kind',
            field=models.CharField(
                'Cihaz tipi',
                blank=True,
                choices=[
                    ('', 'Cihaz değil'),
                    ('split', 'Split'),
                    ('multi_indoor', 'Multi iç ünite'),
                    ('multi_outdoor', 'Multi dış ünite'),
                ],
                default='',
                max_length=16,
            ),
        ),
        migrations.RunPython(seed_klima_kinds, unseed_klima_kinds),
    ]
