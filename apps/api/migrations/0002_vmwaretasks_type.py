# Generated by Django 3.0.6 on 2020-06-01 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vmwaretasks',
            name='type',
            field=models.SmallIntegerField(choices=[('snapshot', 0), ('depoly', 1)], default=0),
            preserve_default=False,
        ),
    ]
