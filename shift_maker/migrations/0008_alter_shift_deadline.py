# Generated by Django 3.2.3 on 2022-03-25 22:09

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('shift_maker', '0007_auto_20220322_2207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shift',
            name='deadline',
            field=models.DateField(default=datetime.datetime(2022, 3, 28, 22, 9, 36, 580948, tzinfo=utc)),
        ),
    ]