from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_compact_sale_numbers'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='contact2_name',
            field=models.CharField(blank=True, max_length=160, verbose_name='2. ulaşım adı soyadı'),
        ),
        migrations.AlterField(
            model_name='party',
            name='phone2',
            field=models.CharField(blank=True, max_length=20, verbose_name='2. ulaşım telefon'),
        ),
    ]
