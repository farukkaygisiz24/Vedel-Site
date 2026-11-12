from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0011_product_device_outdoor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockmovement',
            name='reason',
            field=models.CharField(
                choices=[
                    ('sale', 'Satış'),
                    ('in', 'Stok girişi'),
                    ('adjust', 'Düzeltme'),
                    ('job', 'Montaj'),
                ],
                max_length=16,
                verbose_name='Neden',
            ),
        ),
    ]
