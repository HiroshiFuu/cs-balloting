# Generated by Django 2.2.16 on 2020-11-28 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_poll_multiple', '0005_remove_livepollmultipleitemvote_vote_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='livepollmultiple',
            name='allocation',
            field=models.PositiveIntegerField(default=1, verbose_name='Allocation'),
            preserve_default=False,
        ),
    ]
