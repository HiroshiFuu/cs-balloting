# Generated by Django 2.2.16 on 2020-11-27 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_poll_multiple', '0003_auto_20201102_0453'),
    ]

    operations = [
        migrations.AddField(
            model_name='livepollmultiple',
            name='threshold',
            field=models.PositiveIntegerField(default=2, verbose_name='Threshold'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='livepollmultiple',
            name='batch_no',
            field=models.PositiveIntegerField(unique=True, verbose_name='Batch No.'),
        ),
    ]
