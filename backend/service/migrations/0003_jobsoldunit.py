import django.db.models.deletion
from django.db import migrations, models

import service.models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0009_payment_installment_choices'),
        ('stock', '0011_product_device_outdoor'),
        ('service', '0002_job_pending_time_assignee'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobSoldUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.CharField(blank=True, max_length=120, verbose_name='Marka')),
                ('model', models.CharField(max_length=160, verbose_name='Model')),
                ('outdoor_name', models.CharField(blank=True, max_length=160, verbose_name='Dış ünite')),
                ('line_index', models.PositiveSmallIntegerField(default=0, verbose_name='Sıra')),
                ('serial', models.CharField(blank=True, max_length=80, verbose_name='Seri no')),
                ('photo_a', models.FileField(blank=True, upload_to=service.models.job_unit_photo_to, verbose_name='Görsel 1')),
                ('photo_b', models.FileField(blank=True, upload_to=service.models.job_unit_photo_to, verbose_name='Görsel 2')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sold_units', to='service.job', verbose_name='İş')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_units', to='stock.product', verbose_name='Ürün')),
                ('sale_line', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_units', to='sales.saleline', verbose_name='Satış kalemi')),
            ],
            options={
                'verbose_name': 'Satılan cihaz',
                'verbose_name_plural': 'Satılan cihazlar',
                'ordering': ['id'],
                'unique_together': {('job', 'sale_line', 'line_index')},
            },
        ),
    ]
