from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0008_merkez_depo_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='alert_qty',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=12,
                null=True,
                verbose_name='Kritik eşik',
            ),
        ),
    ]
