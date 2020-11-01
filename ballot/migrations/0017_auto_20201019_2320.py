# Generated by Django 2.2.14 on 2020-10-19 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ballot', '0016_auto_20201019_2250'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='livepollbatch',
            options={'managed': True, 'verbose_name': 'Live Poll Batch', 'verbose_name_plural': 'Live Poll Batches'},
        ),
        migrations.RemoveField(
            model_name='livepollbatch',
            name='vote_batch',
        ),
        migrations.AddField(
            model_name='livepollbatch',
            name='batch_no',
            field=models.PositiveIntegerField(default=1, verbose_name='Batch No.'),
            preserve_default=False,
        ),
    ]