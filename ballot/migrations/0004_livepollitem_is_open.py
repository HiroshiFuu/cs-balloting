# Generated by Django 2.2.12 on 2020-09-03 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ballot', '0003_livepoll_is_chosen'),
    ]

    operations = [
        migrations.AddField(
            model_name='livepollitem',
            name='is_open',
            field=models.BooleanField(default=False, verbose_name='Is Open'),
        ),
    ]
