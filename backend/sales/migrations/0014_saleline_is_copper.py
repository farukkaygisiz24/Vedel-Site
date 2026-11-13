from django.db import migrations, models


COPPER_LINE_DESCRIPTION = 'Bakır boru'


def backfill_copper_lines(apps, schema_editor):
    """Mark agreed copper lines made before the flag existed.

    They were saved with description 'Bakır boru' and no sale stock movement.
    """
    SaleLine = apps.get_model('sales', 'SaleLine')
    SaleLine.objects.filter(
        description=COPPER_LINE_DESCRIPTION,
        stock_movements__isnull=True,
    ).update(is_copper=True)


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0013_uniq_party_legal_tax_no'),
        ('stock', '0016_category_copper_pipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleline',
            name='is_copper',
            field=models.BooleanField(default=False, verbose_name='Anlaşılan bakır boru'),
        ),
        migrations.RunPython(backfill_copper_lines, migrations.RunPython.noop),
    ]
