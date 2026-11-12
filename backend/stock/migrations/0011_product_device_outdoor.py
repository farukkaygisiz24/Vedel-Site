from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0010_product_alert_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_device',
            field=models.BooleanField(default=False, verbose_name='Cihaz'),
        ),
        migrations.AddField(
            model_name='product',
            name='outdoor_name',
            field=models.CharField(blank=True, max_length=160, verbose_name='Dış ünite'),
        ),
        migrations.AddField(
            model_name='product',
            name='outdoor',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='indoor_units',
                to='stock.product',
                verbose_name='Dış ünite stoku',
            ),
        ),
    ]
