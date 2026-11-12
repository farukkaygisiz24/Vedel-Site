from django.db import migrations


def rename_merkez_depo(apps, schema_editor):
    Category = apps.get_model('stock', 'Category')
    if Category.objects.filter(name='Merkez Depo').exists():
        return
    item = Category.objects.filter(name='MERKEZ DEPO').first()
    if item is None:
        return
    item.name = 'Merkez Depo'
    item.save(update_fields=['name'])


def revert_merkez_depo(apps, schema_editor):
    Category = apps.get_model('stock', 'Category')
    if Category.objects.filter(name='MERKEZ DEPO').exists():
        return
    item = Category.objects.filter(name='Merkez Depo').first()
    if item is None:
        return
    item.name = 'MERKEZ DEPO'
    item.save(update_fields=['name'])


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0007_product_category_required'),
    ]

    operations = [
        migrations.RunPython(rename_merkez_depo, revert_merkez_depo),
    ]
