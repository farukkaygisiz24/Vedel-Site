from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0011_payment_party_allocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='mount_address',
            field=models.TextField(blank=True, verbose_name='Montaj adres'),
        ),
        migrations.AddField(
            model_name='sale',
            name='mount_city',
            field=models.CharField(blank=True, max_length=80, verbose_name='Montaj il'),
        ),
        migrations.AddField(
            model_name='sale',
            name='mount_contact_name',
            field=models.CharField(blank=True, max_length=160, verbose_name='Montaj kişi'),
        ),
        migrations.AddField(
            model_name='sale',
            name='mount_district',
            field=models.CharField(blank=True, max_length=80, verbose_name='Montaj ilçe'),
        ),
        migrations.AddField(
            model_name='sale',
            name='mount_notes',
            field=models.TextField(blank=True, verbose_name='Montaj açıklama'),
        ),
        migrations.AddField(
            model_name='sale',
            name='mount_phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Montaj telefon'),
        ),
    ]
