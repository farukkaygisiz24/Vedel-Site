from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0004_jobsoldunit_outdoor_serial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobsoldunit',
            name='room',
            field=models.CharField(blank=True, max_length=80, verbose_name='Oda'),
        ),
    ]
