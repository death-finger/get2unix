from django.db import models


class Tasks(models.Model):
    task_type_choices = (
        ('snapshot', 0),
        ('depoly', 1),
    )
    task_type_dict = {
        0: 'snapshot',
        1: 'deploy',
    }

    chain_id = models.BigIntegerField(unique=True, null=False)
    key = models.CharField(max_length=50, unique=True)
    user = models.CharField(max_length=255, null=True)
    queue_time = models.DateTimeField()
    state = models.CharField(max_length=20, null=True)
    progress = models.PositiveSmallIntegerField(unique=False, default=0)
    entity_name = models.CharField(max_length=255, null=True)
    type = models.SmallIntegerField(choices=task_type_choices)
    msg = models.TextField(unique=False, null=True)

    class Meta:
        permissions = [
            ('can_read_vmware_tasks', 'Permission to read vmware tasks'),
            ('can_change_vmware_tasks', 'Permission to modify vmware tasks'),
            ('can_add_vmware_tasks', 'Permission to add vmware tasks'),
            ('can_delete_vmware_tasks', 'Permission to delete vmware tasks'),
        ]


class DeployLists(models.Model):
    deploy_state_choices = (
        ('draft', 0),
        ('added', 1),
        ('verified', 2),
        ('running', 3),
        ('success', 4),
        ('error', 5),
    )
    task_type_dict = {
        0: 'draft',
        1: 'added',
        2: 'verified',
        3: 'running',
        4: 'success',
        5: 'error',
    }
    template = models.CharField(max_length=100, unique=False, null=True)
    servername = models.CharField(max_length=100, unique=False, null=True)
    vcenter = models.CharField(max_length=100, null=True)
    datacenter = models.CharField(max_length=50, unique=False, null=True)
    cluster = models.CharField(max_length=100, unique=False, null=True)
    datastore = models.CharField(max_length=100, unique=False, null=True)
    custspec = models.CharField(max_length=100, unique=False, null=True)
    vlan = models.CharField(max_length=50, unique=False, null=True)
    ipaddress = models.GenericIPAddressField(unique=False, null=True)
    netmask = models.CharField(max_length=30, unique=False, null=True)
    gateway = models.GenericIPAddressField(unique=False, null=True)
    cpu = models.SmallIntegerField(null=True)
    memory = models.SmallIntegerField(null=True)
    state = models.SmallIntegerField(choices=deploy_state_choices, default=0)
    user = models.CharField(max_length=255, unique=False, null=True)
    token = models.TextField(null=True)
    chain_id = models.BigIntegerField(unique=True, null=True)

    class Meta:
        permissions = [
            ('can_read_vmware_deploy_list', 'Permission to read vmware deploy list'),
            ('can_change_vmware_deploy_list', 'Permission to modify vmware deploy listt'),
            ('can_add_vmware_deploy_list', 'Permission to add vmware deploy list'),
            ('can_delete_vmware_deploy_list', 'Permission to delete vmware deploy listt'),
        ]


class Snapshots(models.Model):
    state_choices = (
        ('pending', 0),
        ('done', 1),
        ('expired', 2),
        ('removed', 3),
        ('fail', 4),
        ('retry', 5),
    )
    state_dict = {
        0: 'pending',
        1: 'done',
        2: 'expired',
        3: 'removed',
        4: 'fail',
        5: 'retry',
    }
    vm_name = models.CharField(max_length=255, null=False, unique=False)
    vm_uuid = models.CharField(max_length=255, null=False, unique=True)
    vm_path = models.TextField()
    vm_vc = models.CharField(max_length=255, null=False, unique=False)
    time_created = models.DateTimeField(auto_now_add=True)
    keep_days = models.SmallIntegerField(default=5, null=False, unique=False)
    snap_name = models.CharField(max_length=255, null=False, unique=False)
    # snap_uuid = models.UUIDField()
    snap_desc = models.TextField()
    snap_mem = models.BooleanField(default=False)
    snap_qui = models.BooleanField(default=False)
    snap_remove_child = models.BooleanField(default=False)
    snap_sol = models.BooleanField(default=False)
    state = models.SmallIntegerField(choices=state_choices, default=0)
    operator = models.CharField(max_length=255, null=False, unique=False)

    class Meta:
        permissions = [
            ('can_read_vmware_snapshots', 'Permission to read vmware snapshots'),
            ('can_change_vmware_snapshots', 'Permission to modify vmware snapshots'),
            ('can_add_vmware_snapshots', 'Permission to add vmware snapshots'),
            ('can_delete_vmware_snapshots', 'Permission to delete vmware snapshots'),
        ]
