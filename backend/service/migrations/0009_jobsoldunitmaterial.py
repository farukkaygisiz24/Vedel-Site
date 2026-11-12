import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0008_jobsoldunit_single_care'),
        ('stock', '0011_product_device_outdoor'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobSoldUnitMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Adet')),
                ('name', models.CharField(max_length=200, verbose_name='Ürün adı')),
                ('unit_label', models.CharField(blank=True, max_length=16, verbose_name='Birim')),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='job_unit_materials',
                    to='stock.product',
                    verbose_name='Ürün',
                )),
                ('unit', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='materials',
                    to='service.jobsoldunit',
                    verbose_name='Cihaz',
                )),
            ],
            options={
                'verbose_name': 'Montaj malzemesi',
                'verbose_name_plural': 'Montaj malzemeleri',
                'ordering': ['id'],
            },
        ),
    ]
