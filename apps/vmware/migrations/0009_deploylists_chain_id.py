# Generated by Django 3.0.6 on 2020-06-04 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vmware', '0008_auto_20200603_1845'),
    ]

    operations = [
        migrations.AddField(
            model_name='deploylists',
            name='chain_id',
            field=models.BigIntegerField(null=True, unique=True),
        ),
    ]