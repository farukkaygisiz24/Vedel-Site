import django.db.models.deletion
from django.db import migrations, models


def drop_orphan_sal_jobs(apps, schema_editor):
    Job = apps.get_model('service', 'Job')
    Job.objects.filter(sale_id__isnull=True, number__istartswith='SAL').exclude(
        status='closed'
    ).delete()


def noop(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [
        ('service', '0014_relabel_mount_job_numbers'),
        ('sales', '0011_payment_party_allocation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='sale',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='service_job',
                to='sales.sale',
                verbose_name='Satış fişi',
            ),
        ),
        migrations.RunPython(drop_orphan_sal_jobs, noop),
    ]
