# Generated by Django 2.2.12 on 2020-08-12 12:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ballot', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='survey',
            options={'managed': True, 'verbose_name': 'Survey', 'verbose_name_plural': 'Surveys'},
        ),
    ]
