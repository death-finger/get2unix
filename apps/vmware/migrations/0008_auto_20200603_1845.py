# Generated by Django 3.0.6 on 2020-06-03 10:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vmware', '0007_auto_20200603_1842'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deploylists',
            old_name='profile',
            new_name='custspec',
        ),
        migrations.RenameField(
            model_name='deploylists',
            old_name='ip',
            new_name='ipaddress',
        ),
        migrations.RenameField(
            model_name='deploylists',
            old_name='mask',
            new_name='netmask',
        ),
    ]