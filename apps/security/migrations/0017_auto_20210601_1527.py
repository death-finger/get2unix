# Generated by Django 3.0.6 on 2021-06-01 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0016_auto_20210420_1218'),
    ]

    operations = [
        migrations.AddField(
            model_name='sudotasks',
            name='nopasswd',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='sudotasks',
            name='status',
            field=models.SmallIntegerField(choices=[('PENDING', 0), ('ADDED', 1), ('EXPIRED', 2), ('REMOVED', 3), ('FAILED', 4), ('RUNNING', 5), ('REMOVING', 6), ('SUDO_SCAN', 7)], default=0),
        ),
    ]
