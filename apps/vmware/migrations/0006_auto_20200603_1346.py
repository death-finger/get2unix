# Generated by Django 3.0.6 on 2020-06-03 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vmware', '0005_auto_20200603_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deploylists',
            name='state',
            field=models.SmallIntegerField(choices=[('draft', 0), ('added', 1), ('verified', 2), ('running', 3), ('success', 4), ('error', 5)], default=0),
        ),
    ]