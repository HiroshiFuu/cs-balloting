# Generated by Django 2.2.14 on 2020-11-02 04:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('live_poll_multiple', '0002_auto_20201102_0411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livepollmultipleresult',
            name='live_poll',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='live_poll_multiple.LivePollMultiple'),
        ),
    ]