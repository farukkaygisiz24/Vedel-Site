from django.db import migrations, models


def seed_roles(apps, schema_editor):
    Customer = apps.get_model('accounts', 'Customer')
    Customer.objects.filter(is_staff=True).update(role='service_lead')
    Customer.objects.filter(is_staff=False).exclude(role='').update(role='')


def unseed_roles(apps, schema_editor):
    Customer = apps.get_model('accounts', 'Customer')
    Customer.objects.update(role='')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('stock', '0015_category_klima_product_kind'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='role',
            field=models.CharField(
                blank=True,
                choices=[
                    ('sales', 'Satış'),
                    ('service_lead', 'Servis yetkilisi'),
                    ('service', 'Servis'),
                ],
                max_length=20,
                verbose_name='Rol',
            ),
        ),
        migrations.AddField(
            model_name='customer',
            name='stock_categories',
            field=models.ManyToManyField(
                blank=True,
                related_name='portal_users',
                to='stock.category',
                verbose_name='Depo kategorileri',
            ),
        ),
        migrations.RunPython(seed_roles, unseed_roles),
    ]
