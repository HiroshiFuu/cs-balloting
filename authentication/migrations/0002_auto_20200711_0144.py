# Generated by Django 2.2.14 on 2020-07-10 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='weight',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Vote Weighting'),
        ),
    ]
