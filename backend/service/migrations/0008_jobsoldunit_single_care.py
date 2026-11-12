from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0007_jobsoldunit_care'),
    ]

    operations = [
        migrations.RemoveField(model_name='jobsoldunit', name='outdoor_interval_months'),
        migrations.RemoveField(model_name='jobsoldunit', name='outdoor_last_serviced_on'),
        migrations.RemoveField(model_name='jobsoldunit', name='outdoor_next_due'),
        migrations.AlterField(
            model_name='jobsoldunit',
            name='interval_months',
            field=models.PositiveSmallIntegerField(
                choices=[(3, '3 ay'), (6, '6 ay'), (9, '9 ay'), (12, '12 ay')],
                default=6,
                verbose_name='Bakım aralığı',
            ),
        ),
        migrations.AlterField(
            model_name='jobsoldunit',
            name='last_serviced_on',
            field=models.DateField(blank=True, null=True, verbose_name='Son bakım'),
        ),
        migrations.AlterField(
            model_name='jobsoldunit',
            name='next_due',
            field=models.DateField(blank=True, null=True, verbose_name='Sonraki bakım'),
        ),
    ]
