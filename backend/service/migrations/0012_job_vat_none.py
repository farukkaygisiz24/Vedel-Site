from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0011_job_submitted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='vat_mode',
            field=models.CharField(
                choices=[('plus', '+ KDV'), ('included', 'KDV dahil'), ('none', 'KDV yok')],
                default='plus',
                max_length=16,
                verbose_name='KDV',
            ),
        ),
    ]
