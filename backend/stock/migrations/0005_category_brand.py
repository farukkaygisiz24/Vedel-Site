from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0004_sku_prefix_brand_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='brand',
            field=models.CharField(blank=True, max_length=80, verbose_name='Marka'),
        ),
    ]
