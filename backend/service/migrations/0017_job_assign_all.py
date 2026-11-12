from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0016_device_nine_month_care'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='assign_all',
            field=models.BooleanField('Tüm personel', default=False),
        ),
    ]
