from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from libs.vmware import create_snapshot
from datetime import datetime
from get2unix.settings import VC_LIST


class BulkTakeSnapshot(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ('vmware.can_read_vmware_tasks', 'vmware.can_change_vmware_tasks',
                           'vmware.can_add_vmware_tasks', 'vmware.can_delete_vmware_tasks')

    def get(self, request, *args, **kwargs):
        data = {
            "vcenter_list": VC_LIST,
            "user": request.user,
            "title": "VM Snapshots"
        }

        return render(request, 'vmware/snapshots.html', {'data': data,})

