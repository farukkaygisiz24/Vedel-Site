import re

from django.db import migrations, models


def assign_party_numbers(apps, schema_editor):
    Party = apps.get_model('sales', 'Party')
    taken = set()
    for party in Party.objects.order_by('id'):
        if party.kind == 'legal':
            digits = re.sub(r'\D', '', party.tax_no or '')
            if len(digits) != 10:
                digits = f'{party.pk:010d}'
        else:
            digits = re.sub(r'\D', '', party.national_id or '')
            if len(digits) != 11:
                digits = f'{party.pk:011d}'
        base = f'CUSTC{digits}'
        number = base
        serial = 1
        while number in taken:
            number = f'{base}-{serial}'
            serial += 1
        party.number = number
        taken.add(number)
        party.save(update_fields=['number'])


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_party_contact2_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='number',
            field=models.CharField(blank=True, max_length=24, verbose_name='No'),
        ),
        migrations.RunPython(assign_party_numbers, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='party',
            name='number',
            field=models.CharField(max_length=24, unique=True, verbose_name='No'),
        ),
    ]
