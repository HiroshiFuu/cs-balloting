# Generated by Django 2.2.16 on 2020-12-17 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_poll', '0006_livepollitemvote_lots'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livepollitem',
            name='text',
            field=models.CharField(max_length=511),
        ),
    ]
