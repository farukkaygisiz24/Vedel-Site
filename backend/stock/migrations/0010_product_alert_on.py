from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0009_product_alert_qty'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='alert_on',
            field=models.BooleanField(default=False, verbose_name='Hatırlat'),
        ),
    ]
