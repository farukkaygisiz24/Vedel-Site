from django.db import migrations, models

import service.models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0003_jobsoldunit'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobsoldunit',
            name='outdoor_serial',
            field=models.CharField(blank=True, max_length=80, verbose_name='Dış ünite seri no'),
        ),
        migrations.AddField(
            model_name='jobsoldunit',
            name='outdoor_photo_a',
            field=models.FileField(
                blank=True,
                upload_to=service.models.job_unit_photo_to,
                verbose_name='Dış görsel 1',
            ),
        ),
        migrations.AddField(
            model_name='jobsoldunit',
            name='outdoor_photo_b',
            field=models.FileField(
                blank=True,
                upload_to=service.models.job_unit_photo_to,
                verbose_name='Dış görsel 2',
            ),
        ),
        migrations.AlterField(
            model_name='jobsoldunit',
            name='serial',
            field=models.CharField(blank=True, max_length=80, verbose_name='İç ünite seri no'),
        ),
        migrations.AlterField(
            model_name='jobsoldunit',
            name='photo_a',
            field=models.FileField(
                blank=True,
                upload_to=service.models.job_unit_photo_to,
                verbose_name='İç görsel 1',
            ),
        ),
        migrations.AlterField(
            model_name='jobsoldunit',
            name='photo_b',
            field=models.FileField(
                blank=True,
                upload_to=service.models.job_unit_photo_to,
                verbose_name='İç görsel 2',
            ),
        ),
    ]
