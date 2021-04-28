# Generated by Django 3.0.6 on 2020-06-02 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vmware', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deploylists',
            name='cluster',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='deploylists',
            name='cpu',
            field=models.SmallIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='deploylists',
            name='datacenter',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='deploylists',
            name='datastore',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='deploylists',
            name='gateway',
            field=models.GenericIPAddressField(null=True),
        ),
        migrations.AlterField(
            model_name='deploylists',
            name='ip',
            field=models.GenericIPAddressField(null=True),
        ),
        migrations.AlterField(
            model_name='deploylists',
            name='mask',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='deploylists',
            name='memory',
            field=models.SmallIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='deploylists',
            name='profile',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='deploylists',
            name='vlan',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='deploylists',
            name='vm_name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
