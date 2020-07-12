# Generated by Django 2.2.14 on 2020-07-12 08:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ballot', '0002_auto_20200711_1308'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='polloption',
            options={'managed': True, 'verbose_name': 'Poll Option', 'verbose_name_plural': 'Poll Options'},
        ),
        migrations.AlterField(
            model_name='polloption',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='ballot.Poll'),
        ),
    ]
