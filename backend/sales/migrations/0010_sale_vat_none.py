from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0009_payment_installment_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='vat_mode',
            field=models.CharField(
                choices=[('plus', '+ KDV'), ('included', 'KDV dahil'), ('none', 'KDV yok')],
                max_length=16,
                verbose_name='KDV',
            ),
        ),
    ]
