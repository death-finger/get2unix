# Generated by Django 3.0.6 on 2020-08-22 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sudotasks',
            options={'permissions': [('can_read_security_tempsudo', 'Permission to read security/tempsudo')]},
        ),
        migrations.AddField(
            model_name='sudotasks',
            name='hostname',
            field=models.CharField(default=123, max_length=255),
            preserve_default=False,
        ),
    ]
