# Generated by Django 2.2.16 on 2020-12-23 00:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('live_poll', '0009_auto_20201217_0053'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='livepollitem',
            options={'managed': True, 'ordering': ['order'], 'verbose_name': 'Live Poll Item', 'verbose_name_plural': 'Live Poll Items'},
        ),
        migrations.AlterUniqueTogether(
            name='livepollitem',
            unique_together={('poll', 'order')},
        ),
    ]