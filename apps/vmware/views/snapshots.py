# from django.shortcuts import render
# from django.views.generic import View
# from django.http import JsonResponse
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# from libs.vmware import create_snapshot
# from datetime import datetime
# from get2unix.settings import VC_LIST
#
#
# class BulkTakeSnapshot(LoginRequiredMixin, PermissionRequiredMixin, View):
#     login_url = '/login/'
#     permission_required = ('vmware.can_read_vmware_tasks', 'vmware.can_change_vmware_tasks',
#                            'vmware.can_add_vmware_tasks', 'vmware.can_delete_vmware_tasks')
#
#     def get(self, request, *args, **kwargs):
#         data = {
#             "vcenter_list": VC_LIST,
#             "user": request.user,
#             "title": "VM Snapshots"
#         }
#
#         return render(request, 'vmware/snapshots.html', {'data': data,})
from rest_framework import viewsets
from rest_framework.response import Response
from vmware.models import Snapshots
from vmware.serializers import SnapshotSerializer
from utils.redis_client import RedisOperator
from get2unix.settings import VC_CACHE_DB


class SnapshotViewSet(viewsets.ViewSet):
    queryset = Snapshots.objects.all()
    serializer_class = SnapshotSerializer

    def list(self, request):
        return Response(self.serializer_class(self.queryset, many=True).data)

    def create(self, request):
        data_new = []
        data_exist = []
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
                data_exist.append()
            data.append(snap_dict)
        serializer = self.serializer_class(data=data, many=True)
        serializer.is_valid()
        serializer.save()
