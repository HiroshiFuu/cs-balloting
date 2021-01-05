# Generated by Django 2.2.16 on 2020-12-17 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_poll', '0007_auto_20201217_0018'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='livepollitem',
            options={'managed': True, 'ordering': ['poll__company', 'order'], 'verbose_name': 'Live Poll Item', 'verbose_name_plural': 'Live Poll Items'},
        ),
        migrations.AlterField(
            model_name='livepollitem',
            name='text',
            field=models.TextField(max_length=511),
        ),
    ]