from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0015_job_sale_cascade_drop_orphan_sal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='interval_months',
            field=models.PositiveSmallIntegerField(
                choices=[(3, '3 ay'), (6, '6 ay'), (9, '9 ay'), (12, '12 ay')],
                default=6,
                verbose_name='Bakım aralığı',
            ),
        ),
    ]
