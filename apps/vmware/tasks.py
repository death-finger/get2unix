from __future__ import absolute_import, unicode_literals
from celery import shared_task
from utils.vmware_client import VMWare
from utils.redis_client import RedisOperator
from vmware.models import DeployLists, Snapshots
from libs.vmware import deploy_vm_from_template
from get2unix.settings import VC_CACHE_DB, VC_LIST, SVC_ACCOUNT
import threading
from django.utils import timezone
from utils.terraform_client import *
import os


@shared_task
def flush_vmware_arch():
    for vc in VC_LIST:
        c = VMWare(host=vc + ".corp.ebay.com", port=443, username=SVC_ACCOUNT[0], password=SVC_ACCOUNT[1])
        x = c.connect()
        r = RedisOperator(VC_CACHE_DB[vc])
        print('Start VC Arch Scan on %s' % vc)
        threading.Thread(target=c.task_scan_dc, args=(x, r)).start()


@shared_task
def flush_vmware_full_scan():
    for vc in VC_LIST:
        c = VMWare(host=vc + ".corp.ebay.com", port=443, username=SVC_ACCOUNT[0], password=SVC_ACCOUNT[1])
        x = c.connect()
        r = RedisOperator(VC_CACHE_DB[vc])
        print('Start VC Full Scan on %s' % vc)
        threading.Thread(target=c.task_scan_dc, args=(x, r, True)).start()


@shared_task
def verify_deploy_tasks():
    deploy_list = DeployLists.objects.filter(state=1).all()
    for deploy in deploy_list:
        deploy_dict = {
            'id': deploy.id,
            'template': deploy.template,
            'servername': deploy.servername,
            'vcenter': deploy.vcenter,
            'datacenter': deploy.datacenter,
            'cluster': deploy.cluster,
            'datastore': deploy.datastore,
            'custspec': deploy.custspec,
            'vlan': deploy.vlan,
            'ipaddress': deploy.ipaddress,
            'netmask': deploy.netmask,
            'gateway': deploy.gateway,
            'cpu': deploy.cpu,
            'memory': deploy.memory,
            'state': deploy.state,
            'user': deploy.user,
            'token': deploy.token[2:-1],
            'mode': 'check'
        }
        deploy_vm_from_template(deploy_dict)


@shared_task
def run_snapshot_expire_scan():
    check_list = Snapshots.objects.filter(state=1)
    for item in check_list:
        time_delta = timezone.now() - item.time_created
        if time_delta.days > item.keep_days:
            item.state = 2
            item.save()


@shared_task
def run_snapshot_tasks():
    snapshot_queryset = Snapshots.objects.filter(state__in=(0, 1, 2)).order_by('vm_vc')
    task_list = {}
    result_list = {}

    if not snapshot_queryset:
        result_list = {"CODE": 0, "TASK": "run_snapshot_tasks", "STATUS": "skipped",
                       "DETAILS": "None of the Snapshots objects are in state 0, 1 or 2"}
    else:
        for dc in snapshot_queryset.values('vm_vc').distinct():
            task_list[dc['vm_vc']] = []
            result_list[dc['vm_vc']] = ""
        for snapshot_obj in snapshot_queryset.filter(state__in=(0, 1)):
            task_list[snapshot_obj.vm_vc].append(snapshot_obj)

    for dc, tasks in task_list.items():
        tf_file_path = tf_file_builder(dc, tasks)
        threading.Thread(target=run_tfm_concurrency, args=(snapshot_queryset.filter(vm_vc=dc),
                                                           os.path.dirname(tf_file_path['tf_file']),
                                                           SVC_ACCOUNT[0], SVC_ACCOUNT[1], dc)).start()


def run_tfm_concurrency(snapshot_queryset, tf_file, account, password, dc):
    result = terraform_runner(tf_file, "plan", account, password, dc)
    if result['code']:
        print("Failed to execute run_snap_tasks, terraform_runner plan received error message: %s" % result['msg'])
        return_data = {"CODE": 1, "TASK": "run_snapshot_tasks", "DC": dc, "STATUS": "failed",
                       "DETAILS": result['msg']}
    else:
        result = terraform_runner(tf_file, "apply", account, password, dc)
        if result['code']:
            print("Failed to execute run_snap_tasks, terraform_runner apply received error message: %s" % result['msg'])
            return_data = {"CODE": 2, "TASK": "run_snapshot_tasks", "DC": dc, "STATUS": "failed",
                           "DETAILS": result['msg']}
        else:
            snapshot_queryset.filter(state=0).update(state=1)
            snapshot_queryset.filter(state=2).update(state=3)
            return_data = {"CODE": 0, "TASK": "run_snapshot_tasks", "DC": dc, "STATUS": "success",
                           "DETAILS": result['msg']}
    print(return_data)
