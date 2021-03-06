# Generated by Django 3.2.9 on 2021-12-23 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shift_maker', '0002_auto_20211223_0224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shift',
            name='slot',
            field=models.ManyToManyField(blank=True, null=True, to='shift_maker.Slot'),
        ),
        migrations.AlterField(
            model_name='user',
            name='assigning_slot',
            field=models.ManyToManyField(blank=True, related_name='slot_users', to='shift_maker.Slot'),
        ),
    ]
