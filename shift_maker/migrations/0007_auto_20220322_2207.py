# Generated by Django 3.2.9 on 2022-03-22 13:07

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('shift_maker', '0006_auto_20220319_0605'),
    ]

    operations = [
        migrations.AddField(
            model_name='slot',
            name='for_template',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='shift',
            name='deadline',
            field=models.DateField(default=datetime.datetime(2022, 3, 25, 13, 7, 16, 108183, tzinfo=utc)),
        ),
    ]
