# Generated by Django 3.0.6 on 2020-11-14 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0006_auto_20200823_2157'),
    ]

    operations = [
        migrations.AddField(
            model_name='sudotasks',
            name='effective_days',
            field=models.SmallIntegerField(default=3),
        ),
    ]