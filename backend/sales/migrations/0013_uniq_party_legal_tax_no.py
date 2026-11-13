from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0012_sale_mount_fields'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='party',
            constraint=models.UniqueConstraint(
                condition=models.Q(kind='legal') & ~models.Q(tax_no=''),
                fields=('tax_no',),
                name='uniq_party_legal_tax_no',
            ),
        ),
    ]
