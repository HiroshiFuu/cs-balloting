# Generated by Django 2.2.16 on 2020-12-03 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_poll_multiple', '0006_livepollmultiple_allocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='livepollmultiple',
            name='text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
