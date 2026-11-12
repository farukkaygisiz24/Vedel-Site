import re
from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def fill_sku_prefixes(apps, schema_editor):
    Category = apps.get_model('stock', 'Category')
    used = set()
    for prefix in Category.objects.exclude(sku_prefix='').values_list('sku_prefix', flat=True):
        used.add(prefix)
    for cat in Category.objects.filter(sku_prefix='').order_by('pk'):
        raw = str(cat.name or '').replace('ı', 'I').replace('i', 'I').replace('İ', 'I').upper()
        letters = re.sub(r'[^A-Z]', '', raw)[:6]
        if len(letters) < 2:
            letters = 'CAT'
        code = letters
        serial = 2
        while code in used:
            suffix = str(serial)
            code = (letters[: max(2, 6 - len(suffix))] + suffix)[:6]
            serial += 1
            if serial > 99:
                code = f'C{cat.pk}'[:6]
                break
        cat.sku_prefix = code
        cat.save(update_fields=['sku_prefix'])
        used.add(code)


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_saleline_cost_price_alter_sale_work_type_and_more'),
        ('stock', '0003_product_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='sku_prefix',
            field=models.CharField(default='', max_length=6, verbose_name='Stok öneki'),
            preserve_default=False,
        ),
        migrations.RunPython(fill_sku_prefixes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='category',
            name='sku_prefix',
            field=models.CharField(
                max_length=6,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        '^[A-Z]{2,6}$',
                        'Stok öneki 2–6 harf olmalı.',
                    )
                ],
                verbose_name='Stok öneki',
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.CharField(blank=True, max_length=80, verbose_name='Marka'),
        ),
        migrations.AddField(
            model_name='stockmovement',
            name='buy_price',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.00'),
                max_digits=12,
                verbose_name='Alış',
            ),
        ),
        migrations.AddField(
            model_name='stockmovement',
            name='supplier',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='stock_supplies',
                to='sales.party',
                verbose_name='Tedarikçi',
            ),
        ),
    ]
