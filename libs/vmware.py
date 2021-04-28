import json
from utils.vmware_client import VMWare
from utils.redis_client import RedisOperator
from utils.pwcrypt import EncryptStr
from get2unix.settings import VC_CACHE_DB
from vmware.models import Snapshots


def create_snapshot(snap_args):
    redis_client = RedisOperator(VC_CACHE_DB[snap_args['vm_vc']])
    for vm in snap_args['vm_name_list']:
        snap_dict = {
            "vm_name": vm.strip(),
            "vm_uuid": json.loads(redis_client.get('VM_' + vm.strip()))['instanceUuid'],
            "vm_path": json.loads(redis_client.get('VM_' + vm.strip()))['datacenter'],
            "vm_vc": snap_args['vm_vc'],
            "time_created": snap_args['time_created'],
            "keep_days": snap_args['keep_days'],
            "snap_name": snap_args['snap_name'],
            "snap_desc": snap_args['snap_desc'],
            "snap_mem": snap_args['snap_mem'],
            "snap_qui": snap_args['snap_qui'],
            "snap_remove_child": snap_args['snap_remove_child'],
            "snap_sol": snap_args['snap_sol'],
            "state": 0,
            "operator": snap_args['operator']
        }
        snap_obj = Snapshots.objects.filter(vm_name=snap_dict['vm_name'])
        if snap_obj:
            snap_obj.update(**snap_dict)
        else:
            Snapshots.objects.create(**snap_dict)
    return 0


def trigger_scan_dc(vc, token, redis_client):
    vc = vc + ".corp.ebay.com"
    username, password = EncryptStr().decrypt(token)
    username = 'corp\\' + username
    si = VMWare(host=vc, port=443, username=username, password=password)
    client = si.connect()
    si.task_scan_dc(client, redis_client)


def deploy_vm_from_template(deploy_args):
    vc = deploy_args['vcenter'] + ".corp.ebay.com"
    username, password = EncryptStr().decrypt(deploy_args['token'])
    username = 'corp\\' + username

    si = VMWare(host=vc, port=443, username=username, password=password)
    client = si.connect()
    r = RedisOperator(VC_CACHE_DB[deploy_args['vcenter']])
    task = si.create_vm_from_template(client, r, deploy_args)
    return task
