from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0006_jobsoldunitphoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobsoldunit',
            name='interval_months',
            field=models.PositiveSmallIntegerField(
                choices=[(3, '3 ay'), (6, '6 ay'), (9, '9 ay'), (12, '12 ay')],
                default=6,
                verbose_name='İç ünite bakım aralığı',
            ),
        ),
        migrations.AddField(
            model_name='jobsoldunit',
            name='last_serviced_on',
            field=models.DateField(blank=True, null=True, verbose_name='İç ünite son bakım'),
        ),
        migrations.AddField(
            model_name='jobsoldunit',
            name='next_due',
            field=models.DateField(blank=True, null=True, verbose_name='İç ünite sonraki bakım'),
        ),
        migrations.AddField(
            model_name='jobsoldunit',
            name='outdoor_interval_months',
            field=models.PositiveSmallIntegerField(
                choices=[(3, '3 ay'), (6, '6 ay'), (9, '9 ay'), (12, '12 ay')],
                default=6,
                verbose_name='Dış ünite bakım aralığı',
            ),
        ),
        migrations.AddField(
            model_name='jobsoldunit',
            name='outdoor_last_serviced_on',
            field=models.DateField(blank=True, null=True, verbose_name='Dış ünite son bakım'),
        ),
        migrations.AddField(
            model_name='jobsoldunit',
            name='outdoor_next_due',
            field=models.DateField(blank=True, null=True, verbose_name='Dış ünite sonraki bakım'),
        ),
    ]
