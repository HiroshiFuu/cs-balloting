# Generated by Django 2.2.14 on 2020-11-02 04:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('live_poll_multiple', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='livepollmultipleitem',
            options={'managed': True, 'ordering': ['live_poll__pk', 'text'], 'verbose_name': 'Live Poll Multiple Item', 'verbose_name_plural': 'Live Poll Multiple Items'},
        ),
        migrations.AlterUniqueTogether(
            name='livepollmultipleitem',
            unique_together={('live_poll', 'text')},
        ),
    ]
