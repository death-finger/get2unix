# Generated by Django 3.0.6 on 2020-08-23 11:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0004_auto_20200822_2234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sudotasks',
            name='status',
            field=models.SmallIntegerField(choices=[('PENDING', 0), ('ADDED', 1), ('EXPIRED', 2), ('REMOVED', 3), ('FAILED', 4), ('RUNNING', 5)], default=0),
        ),
        migrations.CreateModel(
            name='AWXJobs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_id', models.IntegerField(unique=True)),
                ('inv_id', models.IntegerField()),
                ('host_id', models.IntegerField()),
                ('removed', models.BooleanField(default=False)),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='security.SudoTasks')),
            ],
        ),
    ]
