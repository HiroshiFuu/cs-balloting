# Generated by Django 2.2.16 on 2020-12-17 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_poll_multiple', '0011_livepollmultipleitemvote_lots'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livepollmultiple',
            name='text',
            field=models.CharField(default='', max_length=511),
            preserve_default=False,
        ),
    ]