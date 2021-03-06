# Generated by Django 3.0.6 on 2021-02-20 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0012_auto_20210202_1002'),
    ]

    operations = [
        migrations.CreateModel(
            name='CveList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cve_id', models.CharField(max_length=25)),
                ('affected_packages', models.TextField()),
                ('status', models.SmallIntegerField(choices=[('NOT_FIXED', 0), ('FIXED', 1), ('IGNORED', 2), ('DEFERRED', 3)], default=0)),
                ('next_check_date', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VulsScanResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server_name', models.CharField(max_length=255, unique=True)),
                ('family', models.CharField(max_length=255, null=True)),
                ('release', models.CharField(max_length=255, null=True)),
                ('scan_date', models.DateTimeField()),
                ('cve_list', models.ManyToManyField(to='security.CveList')),
            ],
        ),
    ]
