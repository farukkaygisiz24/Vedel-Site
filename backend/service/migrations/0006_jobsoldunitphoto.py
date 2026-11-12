import django.db.models.deletion
from django.db import migrations, models

import service.models


def copy_legacy_photos(apps, schema_editor):
    Unit = apps.get_model('service', 'JobSoldUnit')
    Photo = apps.get_model('service', 'JobSoldUnitPhoto')
    fields = ('photo_a', 'photo_b', 'outdoor_photo_a', 'outdoor_photo_b')
    for unit in Unit.objects.all():
        sort = 0
        for name in fields:
            field = getattr(unit, name)
            if field:
                Photo.objects.create(unit=unit, image=field.name, sort=sort)
                sort += 1


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0005_jobsoldunit_room'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobSoldUnitPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to=service.models.job_unit_photo_to, verbose_name='Görsel')),
                ('sort', models.PositiveSmallIntegerField(default=0, verbose_name='Sıra')),
                (
                    'unit',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='photos',
                        to='service.jobsoldunit',
                        verbose_name='Cihaz',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Cihaz görseli',
                'verbose_name_plural': 'Cihaz görselleri',
                'ordering': ['sort', 'id'],
            },
        ),
        migrations.RunPython(copy_legacy_photos, migrations.RunPython.noop),
        migrations.RemoveField(model_name='jobsoldunit', name='photo_a'),
        migrations.RemoveField(model_name='jobsoldunit', name='photo_b'),
        migrations.RemoveField(model_name='jobsoldunit', name='outdoor_photo_a'),
        migrations.RemoveField(model_name='jobsoldunit', name='outdoor_photo_b'),
    ]
