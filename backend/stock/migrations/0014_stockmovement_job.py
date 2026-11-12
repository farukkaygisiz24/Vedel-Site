from django.db import migrations, models


def fill_job(apps, schema_editor):
    StockMovement = apps.get_model('stock', 'StockMovement')
    Job = apps.get_model('service', 'Job')
    jobs = {item.number: item.pk for item in Job.objects.all()}
    rows = StockMovement.objects.filter(reason='job', job_id__isnull=True).exclude(note='')
    for move in rows:
        number = str(move.note or '').split()[0].strip().upper()
        pk = jobs.get(number)
        if not pk:
            continue
        move.job_id = pk
        move.save(update_fields=['job_id'])


def unfill_job(apps, schema_editor):
    StockMovement = apps.get_model('stock', 'StockMovement')
    StockMovement.objects.filter(reason='job').update(job_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
        ('stock', '0013_klima_montaj_malzemesi'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockmovement',
            name='job',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name='stock_movements',
                to='service.job',
                verbose_name='Servis işi',
            ),
        ),
        migrations.RunPython(fill_job, unfill_job),
    ]
