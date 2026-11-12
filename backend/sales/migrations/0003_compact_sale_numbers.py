import re

from django.db import migrations


def compact_numbers(apps, schema_editor):
    Sale = apps.get_model('sales', 'Sale')
    for sale in Sale.objects.all():
        compact = re.sub(r'[^A-Za-z0-9]', '', str(sale.number or '')).upper()
        if compact and compact != sale.number:
            sale.number = compact
            sale.save(update_fields=['number'])


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(compact_numbers, migrations.RunPython.noop),
    ]
