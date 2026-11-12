from django.db import migrations


def relabel_mount_jobs(apps, schema_editor):
    Job = apps.get_model('service', 'Job')
    for job in Job.objects.filter(sale_id__isnull=False).select_related('sale'):
        sale = job.sale
        if not sale or not sale.number or job.number == sale.number:
            continue
        if Job.objects.filter(number=sale.number).exclude(pk=job.pk).exists():
            continue
        job.number = sale.number
        job.save(update_fields=['number'])


def noop(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0013_job_closed_list_pricing'),
    ]

    operations = [
        migrations.RunPython(relabel_mount_jobs, noop),
    ]
