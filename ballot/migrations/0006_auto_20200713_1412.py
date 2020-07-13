# Generated by Django 2.2.14 on 2020-07-13 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ballot', '0005_auto_20200713_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='end_date',
            field=models.DateField(null=True, verbose_name='End Date'),
        ),
        migrations.AlterUniqueTogether(
            name='polloption',
            unique_together={('text', 'poll')},
        ),
    ]
