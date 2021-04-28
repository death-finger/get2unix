from django.views.generic import View
from django.http import JsonResponse
from libs.vmware import deploy_vm_from_template, create_snapshot
from utils.redis_client import RedisOperator
from vmware.models import Tasks, DeployLists, Snapshots
from libs.vmware import trigger_scan_dc
import json
from get2unix.settings import VC_CACHE_DB
from datetime import datetime


class Inventory(View):

    def get(self, request):

        data = []
        for vc, rdb in VC_CACHE_DB.items():
            r = RedisOperator(rdb)
            for res in r.keys('VM_*'):
                vm = json.loads(r.get(res))
                data.append({
                    'hostname': str(res)[5:-1],
                    'vc': vc,
                    'guest': vm['guestFullName'],
                    'state': vm['guestState'],
                    'cpu': vm['numCpu'] if vm['numCpu'] else 0,
                    'memory': round(vm['memorySizeMB']/1024, 1) if vm['memorySizeMB'] else 0,
                    'ip': vm['ipAddress'],
                    'path': vm['vmPathName'],
                })

        return JsonResponse({
            'code': 200,
            'msg': 'OK',
            'data': data
        })


class GetSnapshots(View):

    def get(self, request, *args, **kwargs):
        snapshot_queryset = Snapshots.objects.all().order_by('-id')
        data = []
        for snapshot_obj in snapshot_queryset:
            data.append({
                'id': snapshot_obj.id,
                'vm_name': snapshot_obj.vm_name,
                'vm_vc': snapshot_obj.vm_vc,
                'vm_path': snapshot_obj.vm_path,
                'time_created': snapshot_obj.time_created.strftime("%Y-%m-%d %H:%M:%S"),
                'keep_days': snapshot_obj.keep_days,
                'snap_name': snapshot_obj.snap_name,
                'snap_desc': snapshot_obj.snap_name,
                'operator': snapshot_obj.operator,
                'state': snapshot_obj.state_dict[snapshot_obj.state]
            })
        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': data
        })

    def post(self, request, *args, **kwargs):
        snap_args = {
            'vm_vc': request.POST.get('vm_vc').strip(),
            'vm_name_list': request.POST.get('vm_name_list').strip().split(),
            'time_created': datetime.now(),
            'keep_days': request.POST.get('keep_days') or 5,
            'snap_name': request.POST.get('snap_name').strip() or datetime.strftime(datetime.now(), "%Y%m%d%H%M%S"),
            'snap_desc': request.POST.get('snap_desc'),
            'snap_mem': True if request.POST.get("snap_mem") == 1 else False,
            'snap_qui': True if request.POST.get('snap_qui') == 1 else False,
            'snap_remove_child': True if request.POST.get('snap_remove_child') == 1 else False,
            'snap_sol': True,
            'operator': request.user.username
        }

        result = create_snapshot(snap_args)

        return JsonResponse({
            'code': 200,
            "msg": "OK",
        })


class CheckHostname(View):
    def post(self, request, *args, **kwargs):
        hostname_list = request.POST.get('host_list').strip().split()
        host_find = []
        host_miss = []
        count = 0
        vc = request.POST.get('vc').strip()
        token = request.session.get('token')
        r = RedisOperator(VC_CACHE_DB[vc])

        for i in hostname_list:
            result = r.get("VM_" + i)
            if result:
                host_find.append(json.loads(result)["instanceUuid"])
            elif not result and count == 0:
                # TODO: 这里的 scan 会非常慢, 要考虑有没有其他解决方案
                trigger_scan_dc(vc, token, r)
                result = r.get("VM_" + i)
                if result:
                    host_find.append(json.loads(result)["instanceUuid"])
                else:
                    host_miss.append(i)
                    count += 1
            else:
                host_miss.append(i)
                count += 1

        return JsonResponse({
            'code': 200,
            "msg": "ok",
            "data": {"find": host_find,
                     "miss": host_miss},
        })


class GetTaskInfo(View):
    def get(self, request, *args, **kwargs):
        try:
            task_id = kwargs["id"]
        except KeyError:
            task_id = ""
        if task_id:
            task_model = Tasks.objects.get(key=task_id)

            return JsonResponse({
                "code": 200,
                "msg": "OK",
                "data": task_model,
            })
        else:
            username = 'corp\\' + request.user.username
            tasks = Tasks.objects.filter(user=username, type=0)
            dataList = []
            for item in tasks:
                dataList.append({
                    "id": item.id,
                    "task_key": item.key,
                    "event_id": item.chain_id,
                    "user": item.user,
                    "entity_name": item.entity_name,
                    "queue_time": item.queue_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "state": item.state,
                    "progress": item.progress,
                    "checked": False
                })

            return JsonResponse({
                "code": 200,
                "msg": "ok",
                "data": dataList,
            })

    def post(self, request, *args, **kwargs):
        id_list = request.POST.get('task_id')
        for i in id_list.split(','):
            Tasks.objects.filter(id=i).delete()
        return JsonResponse({
            "code": 200,
            "msg": "ok",
        })


class GetVMwareOpts(View):
    def post(self, request):
        result = []
        current_name = request.POST.get("current_name")
        query_type = request.POST.get("query_type").upper() + "_ARCH"
        deploy_id = request.POST.get('deploy_id')

        if query_type == "TEMPLATE_ARCH":
            obj = DeployLists.objects.create(vcenter=current_name)
            deploy_id = obj.id
            r = RedisOperator(VC_CACHE_DB[current_name])
            data = json.loads(r.get("TEMPLATE"))
            for i in data:
                result.append(i['name'])
        else:
            obj = DeployLists.objects.filter(id=deploy_id)
            vc = obj.first().vcenter
            r = RedisOperator(VC_CACHE_DB[vc])

            if query_type == "DATACENTER_ARCH":
                obj.update(template=current_name)
                data = json.loads(r.get("CLUSTER_ARCH"))
                for k, v in data.items():
                    result.append(k)
            elif query_type == 'CLUSTER_ARCH':
                obj.update(datacenter=current_name)
                data = json.loads(r.get(query_type))
                self.load_dict(data[current_name], result)
            elif query_type == 'DATASTORE_ARCH':
                obj.update(cluster=current_name)
                dc = obj.first().datacenter
                data = json.loads(r.get(query_type))
                self.load_dict(data[dc], result)
            elif query_type == "CUSTSPEC_ARCH":
                obj.update(datastore=current_name)
                result = json.loads(r.get(query_type))
            elif query_type == "VLAN_ARCH":
                obj.update(custspec=current_name)
                dc = obj.first().datacenter
                data = json.loads(r.get(query_type))
                self.load_dict(data[dc], result)

        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': {
                "deploy_id": deploy_id,
                "result": sorted(result),
            },
        })

    def load_dict(self, d, r):
        for k, v in d.items():
            if type(v) == dict:
                r.append(k)
                self.load_dict(d[k], r)
            elif type(v) == list:
                ds = "%s | %s/%s GB" % (k, round(int(v[0])/(1024*1024*1024*1024), 2),
                                        round(int(v[1])/(1024*1024*1024*1024), 2))
                r.append(ds)
            else:
                r.append(k)


class Deploy(View):
    def get(self, request):

        state_to_str = {
            0: 'draft',
            1: 'added',
            2: 'verified',
            3: 'running',
            4: 'success',
            5: 'failed'
        }

        deploy_list = DeployLists.objects.filter(user=request.user.username).all()

        result = []
        for i in deploy_list:
            result.append({
                'id': i.id,
                'template': i.template,
                'vcenter': i.vcenter,
                'servername': i.servername,
                'datacenter': i.datacenter,
                'cluster': i.cluster,
                'datastore': i.datastore,
                'custspec': i.custspec,
                'vlan': i.vlan,
                'ipaddress': i.ipaddress,
                'netmask': i.netmask,
                'gateway': i.gateway,
                'cpu': i.cpu,
                'memory': i.memory,
                'state': state_to_str[i.state],
                'checked': False
            })

        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': result,
        })

    def post(self, request):
        deploy_dict = {
            'id': request.POST.get('deploy_id'),
            'template': request.POST.get('template'),
            'servername': request.POST.get('servername'),
            'vcenter': request.POST.get('vcenter'),
            'datacenter': request.POST.get('datacenter'),
            'cluster': request.POST.get('cluster'),
            'datastore': request.POST.get('datastore'),
            'custspec': request.POST.get('custspec'),
            'vlan': request.POST.get('vlan'),
            'ipaddress': request.POST.get('ipaddress'),
            'netmask': request.POST.get('netmask'),
            'gateway': request.POST.get('gateway'),
            'cpu': request.POST.get('cpu') or 4,
            'memory': request.POST.get('memory') or 8,
            'user': request.user.username,
            'state': 1,
            'token': request.session.get('token')
        }
        DeployLists.objects.filter(id=deploy_dict['id']).update(**deploy_dict)
        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': '',
        })


class DeployAction(View):
    def post(self, request):
        if request.POST.get('delete'):
            deploy_id = request.POST.get('deploy_id')
            for i in deploy_id.split(','):
                DeployLists.objects.filter(id=i).delete()
            return JsonResponse({
                'code': 200,
                'msg': 'ok',
                'data': ""
            })
        elif request.POST.get('run'):
            deploy_id = request.POST.get('deploy_id')
            for i in deploy_id.split(','):
                deploy_obj = DeployLists.objects.get(id=i)
                # verify the state == 2
                if deploy_obj.state == 2:
                    deploy_dict = {
                        'id': deploy_obj.id,
                        'template': deploy_obj.template,
                        'servername': deploy_obj.servername,
                        'vcenter': deploy_obj.vcenter,
                        'datacenter': deploy_obj.datacenter,
                        'cluster': deploy_obj.cluster,
                        'datastore': deploy_obj.datastore,
                        'custspec': deploy_obj.custspec,
                        'vlan': deploy_obj.vlan,
                        'ipaddress': deploy_obj.ipaddress,
                        'netmask': deploy_obj.netmask,
                        'gateway': deploy_obj.gateway,
                        'cpu': deploy_obj.cpu,
                        'memory': deploy_obj.memory,
                        'state': deploy_obj.state,
                        'user': deploy_obj.user,
                        'token': deploy_obj.token[2:-1],
                        'mode': 'run'
                    }
                    deploy_vm_from_template(deploy_dict)
                else:
                    return JsonResponse({
                        'code': 500,
                        'mgs': 'Deploy Task has not passed the verification!'
                    })
            return JsonResponse({
                'code': 200,
                'msg': 'ok',
                'data': ""
            })

