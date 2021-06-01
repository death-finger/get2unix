from django.db import models


class SudoTasks(models.Model):

    status_choices = (
        ('PENDING', 0),
        ('ADDED', 1),
        ('EXPIRED', 2),
        ('REMOVED', 3),
        ('FAILED', 4),
        ('RUNNING', 5),
        ('REMOVING', 6),
        ('SUDO_SCAN', 7),
    )
    status_dict = {
        0: 'PENDING',
        1: 'ADDED',
        2: 'EXPIRED',
        3: 'REMOVED',
        4: 'FAILED',
        5: 'RUNNING',
        6: 'REMOVING',
        7: 'SUDO_SCAN',
    }

    users = models.TextField(null=False, unique=False)
    operator = models.CharField(max_length=100, unique=False, null=False)
    ticket = models.CharField(max_length=255, unique=False, null=False)
    hosts = models.TextField(null=False, unique=False)
    time_created = models.DateTimeField(auto_now_add=True)
    effective_days = models.SmallIntegerField(default=3, null=False, unique=False)
    status = models.SmallIntegerField(choices=status_choices, default=0)
    nopasswd = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ('can_read_security_tempsudo', 'Permission to read security/tempsudo'),
        ]


class CollectorTasks(models.Model):

    status_choices = (
        ('PENDING', 0),
        ('RUNNING', 1),
        ('AWX_DONE', 2),
        ('DONE', 3),
    )
    status_dict = {
        0: 'PENDING',
        1: 'RUNNING',
        2: 'AWX_DONE',
        3: 'DONE',
    }

    host_list = models.TextField(null=False, unique=False)
    id_code = models.CharField(max_length=255, unique=True, null=True, verbose_name="hashed id for filename")
    operator = models.CharField(max_length=100, unique=False, null=False)
    time_created = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(choices=status_choices, default=0)

    class Meta:
        permissions = [
            ('can_read_security_sudoscan', 'Permission to read security/sudoscan'),
        ]


class SudoScanResults(models.Model):

    user_type_choices = (
        ('USER', 0),
        ('LOCAL_GROUP', 1),
        ('NET_GROUP', 2),
    )
    user_type_dict = {
        0: 'USER',
        1: 'LOCAL_GROUP',
        2: 'NET_GROUP'
    }

    task_id = models.ForeignKey(to="CollectorTasks", to_field='id', on_delete=models.CASCADE)
    hostname = models.CharField(max_length=100, unique=False, null=False)
    user = models.CharField(max_length=255, unique=False, null=False)
    user_type = models.SmallIntegerField(choices=user_type_choices)
    src_host = models.CharField(max_length=100, unique=False, null=False)
    run_as = models.CharField(max_length=255, unique=False, null=False)
    commands = models.TextField(null=True, unique=False)

    class Meta:
        permissions = [
            ('can_read_security_sudoscan', 'Permission to read security/sudoscan'),
        ]


class TaskJobs(models.Model):

    task_type_choices = (
        ('SUDO', 0),
        ('COLLECTOR', 1),
        ('VULSCAN', 2)
    )
    task_type_dict = {
        0: 'SUDO',
        1: 'COLLECTOR',
        2: 'VULSCAN'
    }

    task_id = models.BigIntegerField(unique=False, null=False)
    task_type = models.SmallIntegerField(choices=task_type_choices, null=False)
    job_id = models.ForeignKey(to="AWXJobs", to_field="id", on_delete=models.CASCADE)


class AWXJobs(models.Model):
    job_id = models.IntegerField(null=False, unique=True)
    inv_id = models.IntegerField(null=False, unique=False)
    host_id_list = models.TextField(null=False, unique=False)
    removed = models.BooleanField(default=False)


class Hosts(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)


class Users(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)


class Groups(models.Model):
    type_choices = (
        ('USER_GROUP', 0),
        ('HOST_GROUP', 1),
    )
    status_dict = {
        0: 'USER_GROUP',
        1: 'HOST_GROUP',
    }

    name = models.CharField(max_length=255, null=False, unique=True)
    type = models.SmallIntegerField(choices=type_choices, default=0)


class HostsGroups(models.Model):
    host_id = models.ForeignKey(to='Hosts', on_delete=models.CASCADE)
    group_id = models.ForeignKey(to='Groups', on_delete=models.CASCADE)


class UsersGroup(models.Model):
    user_id = models.ForeignKey(to='Users', on_delete=models.CASCADE)
    group_id = models.ForeignKey(to='Groups', on_delete=models.CASCADE)


class SudoConfigs(models.Model):
    group_id = models.ForeignKey(to='Groups', on_delete=models.CASCADE)
    host = models.CharField(max_length=20, default='ALL')
    run_as = models.CharField(max_length=255, default='ALL')
    commands = models.TextField(null=False, unique=False)
    command_alias = models.CharField(max_length=255, unique=False, null=True)
    args = models.CharField(max_length=255, unique=False, null=True)


class CveList(models.Model):
    status_choices = (
        ('NOT_FIXED', 0),
        ('FIXED', 1),
        ('IGNORED', 2),
        ('DEFERRED', 3),
    )
    status_dict = {
        0: 'NOT_FIXED',
        1: 'FIXED',
        2: 'IGNORED',
        3: 'DEFERRED',
    }

    cve_id = models.CharField(max_length=25)
    affected_packages = models.TextField()
    status = models.SmallIntegerField(choices=status_choices, default=0)
    details = models.CharField(max_length=255, null=True)
    next_check_date = models.DateTimeField(null=True)


class VulsScanResult(models.Model):
    server_name = models.CharField(max_length=255, unique=True, null=False)
    family = models.CharField(max_length=255, unique=False, null=True)
    release = models.CharField(max_length=255, unique=False, null=True)
    scan_date = models.DateTimeField(unique=False, null=False)
    cve_list = models.ManyToManyField(to='CveList')


class VulsScanTasks(models.Model):
    status_choices = (
        ('PENDING', 0),
        ('RUNNING', 1),
        ('AWX_DONE', 2),
        ('DONE', 3),
    )
    status_dict = {
        0: 'PENDING',
        1: 'RUNNING',
        2: 'AWX_DONE',
        3: 'DONE',
    }

    id_code = models.CharField(max_length=255, unique=True, null=True, verbose_name='hashed code for filename')
    status = models.SmallIntegerField(choices=status_choices, default=0)