# Generated by Django 3.0.6 on 2021-02-01 23:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0010_auto_20210202_0744'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='collectortasks',
            options={'permissions': [('can_read_security_sudoscan', 'Permission to read security/sudoscan')]},
        ),
        migrations.AlterModelOptions(
            name='sudoscanresults',
            options={'permissions': [('can_read_security_sudoscan', 'Permission to read security/sudoscan')]},
        ),
    ]