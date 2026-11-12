from django.db import migrations, models
import django.db.models.deletion


def seed_packs(apps, schema_editor):
    JobSoldUnit = apps.get_model('service', 'JobSoldUnit')
    JobSoldPack = apps.get_model('service', 'JobSoldPack')
    JobSoldUnitPhoto = apps.get_model('service', 'JobSoldUnitPhoto')
    JobSoldUnitMaterial = apps.get_model('service', 'JobSoldUnitMaterial')
    for unit in JobSoldUnit.objects.select_related('product', 'job').order_by('id'):
        product = unit.product
        kind = (product.device_kind if product else '') or ''
        if kind == 'multi_outdoor':
            pack = JobSoldPack.objects.create(
                job_id=unit.job_id,
                kind='multi',
                source_key=f'o:{unit.sale_line_id or 0}:{unit.line_index}',
                sort=unit.pk,
                outdoor_sale_line_id=unit.sale_line_id,
                outdoor_product_id=unit.product_id,
                outdoor_name=unit.model or unit.outdoor_name,
                outdoor_serial=unit.serial or unit.outdoor_serial,
                outdoor_index=unit.line_index,
                interval_months=unit.interval_months,
                last_serviced_on=unit.last_serviced_on,
                next_due=unit.next_due,
            )
            JobSoldUnitPhoto.objects.filter(unit=unit).update(pack=pack)
            JobSoldUnitMaterial.objects.filter(unit=unit).update(pack=pack)
            continue
        if kind == 'multi_indoor':
            continue
        pack = JobSoldPack.objects.create(
            job_id=unit.job_id,
            kind='split',
            source_key=f's:{unit.sale_line_id or 0}:{unit.line_index}',
            sort=unit.pk,
            outdoor_name=unit.outdoor_name,
            outdoor_serial=unit.outdoor_serial,
            outdoor_index=0,
            interval_months=unit.interval_months,
            last_serviced_on=unit.last_serviced_on,
            next_due=unit.next_due,
        )
        JobSoldUnit.objects.filter(pk=unit.pk).update(pack=pack)
        JobSoldUnitPhoto.objects.filter(unit=unit).update(pack=pack)
        JobSoldUnitMaterial.objects.filter(unit=unit).update(pack=pack)


def unseed_packs(apps, schema_editor):
    apps.get_model('service', 'JobSoldPack').objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('sales', '0009_payment_installment_choices'),
        ('stock', '0015_category_klima_product_kind'),
        ('service', '0009_jobsoldunitmaterial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobSoldPack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('split', 'Split'), ('multi', 'Multi')], max_length=16, verbose_name='Tip')),
                ('source_key', models.CharField(max_length=80, verbose_name='Kaynak')),
                ('sort', models.PositiveSmallIntegerField(default=0, verbose_name='Sıra')),
                ('outdoor_name', models.CharField(blank=True, max_length=160, verbose_name='Dış ünite')),
                ('outdoor_serial', models.CharField(blank=True, max_length=80, verbose_name='Dış ünite seri no')),
                ('outdoor_index', models.PositiveSmallIntegerField(default=0, verbose_name='Dış sıra')),
                ('interval_months', models.PositiveSmallIntegerField(choices=[(3, '3 ay'), (6, '6 ay'), (9, '9 ay'), (12, '12 ay')], default=6, verbose_name='Bakım aralığı')),
                ('last_serviced_on', models.DateField(blank=True, null=True, verbose_name='Son bakım')),
                ('next_due', models.DateField(blank=True, null=True, verbose_name='Sonraki bakım')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sold_packs', to='service.job', verbose_name='İş')),
                ('outdoor_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_packs', to='stock.product', verbose_name='Dış ünite ürün')),
                ('outdoor_sale_line', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_packs', to='sales.saleline', verbose_name='Dış ünite kalemi')),
            ],
            options={
                'verbose_name': 'Cihaz paketi',
                'verbose_name_plural': 'Cihaz paketleri',
                'ordering': ['sort', 'id'],
                'unique_together': {('job', 'source_key')},
            },
        ),
        migrations.AddField(
            model_name='jobsoldunit',
            name='pack',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='units', to='service.jobsoldpack', verbose_name='Paket'),
        ),
        migrations.AddField(
            model_name='jobsoldunitphoto',
            name='pack',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='service.jobsoldpack', verbose_name='Paket'),
        ),
        migrations.AlterField(
            model_name='jobsoldunitphoto',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='service.jobsoldunit', verbose_name='Cihaz'),
        ),
        migrations.AddField(
            model_name='jobsoldunitmaterial',
            name='pack',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='service.jobsoldpack', verbose_name='Paket'),
        ),
        migrations.AlterField(
            model_name='jobsoldunitmaterial',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='service.jobsoldunit', verbose_name='Cihaz'),
        ),
        migrations.RunPython(seed_packs, unseed_packs),
    ]
