from ansible.plugins.callback import CallbackBase
from utils.redis_client import RedisOperator
import json
from assets.models import Inventory, HostStatus
from datetime import datetime

r = RedisOperator('ansible_db')


class ModelResultsCollector(CallbackBase):
    server_type_dict = {
        'VMware': 0,
        'PHYSICAL': 1
    }
    play_result_dict = {
        'unreachable': 0,
        'failed': 1,
        'skipped': 2,
        'ok': 3
    }

    def __init__(self, *args, **kwargs):
        super(ModelResultsCollector, self).__init__(*args, **kwargs)

    def v2_runner_on_unreachable(self, result):
        r.set(result._host.get_name(), "unreachable")
        r.set(result._host.get_name(), json.dumps(result._result))
        inv_id = Inventory.objects.get(hostname=result._host).id
        update_dict = {
            "hostname_id": inv_id,
            "dist": 'N/A',
            "dist_version": 'N/A',
            'selinux_status': 'N/A',
            'selinux_type': 'N/A',
            'selinux_mode': 'N/A',
            'selinux_config_mode': 'N/A',
            'date_last_checked': datetime.now().astimezone(),
            'return_code': self.play_result_dict['unreachable']
        }
        hs_obj = HostStatus.objects.filter(hostname_id=inv_id)
        if hs_obj:
            hs_obj.update(**update_dict)
        else:
            HostStatus.objects.create(**update_dict)

    def v2_runner_on_ok(self, result):
        r.set(result._host.get_name(), "ok")
        r.set(result._host.get_name(), json.dumps(result._result))
        data = result._result['ansible_facts']
        inv_id = Inventory.objects.get(hostname=result._host).id
        update_dict = {
            "hostname_id": inv_id,
            "dist": data['ansible_distribution'],
            "dist_version": data['ansible_distribution_version'],
            'type': self.server_type_dict[data['ansible_virtualization_type']],
            'uptime': data['ansible_uptime_seconds'],
            'ip': data['ansible_default_ipv4']['address'],
            'cpu_core': data['ansible_processor_cores'],
            'cpu_vcpu': data['ansible_processor_vcpus'],
            'memory_total': data['ansible_memory_mb']['real']['total'],
            'memory_used': data['ansible_memory_mb']['nocache']['used'],
            'memory_free': data['ansible_memory_mb']['nocache']['free'],
            'swap_total': data['ansible_memory_mb']['swap']['total'],
            'swap_free': data['ansible_memory_mb']['swap']['free'],
            'selinux_status': data['ansible_selinux']['status'],
            'selinux_type': data['ansible_selinux']['type'],
            'selinux_mode': data['ansible_selinux']['mode'],
            'selinux_config_mode': data['ansible_selinux']['config_mode'],
            'date_last_checked': datetime.now().astimezone(),
            'return_code': self.play_result_dict['ok']
        }
        hs_obj = HostStatus.objects.filter(hostname_id=inv_id)
        if hs_obj:
            hs_obj.update(**update_dict)
        else:
            HostStatus.objects.create(**update_dict)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        inv_id = Inventory.objects.get(hostname=result._host).id
        update_dict = {
            "hostname_id": inv_id,
            "dist": 'N/A',
            "dist_version": 'N/A',
            'selinux_status': 'N/A',
            'selinux_type': 'N/A',
            'selinux_mode': 'N/A',
            'selinux_config_mode': 'N/A',
            'date_last_checked': datetime.now().astimezone(),
            'return_code': self.play_result_dict['failed']
        }
        hs_obj = HostStatus.objects.filter(hostname_id=inv_id)
        if hs_obj:
            hs_obj.update(**update_dict)
        else:
            HostStatus.objects.create(**update_dict)
