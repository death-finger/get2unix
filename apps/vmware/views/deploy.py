from django.shortcuts import render
from django.views.generic import View
from get2unix.settings import VC_LIST
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class BulkDeployVM(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ('vmware.can_read_vmware_deploy_list', 'vmware.can_change_vmware_deploy_list',
                           'vmware.can_add_vmware_deploy_list', 'vmware.can_delete_vmware_deploy_list')

    def get(self, request):
        data = {
            "vc_list": VC_LIST,
            'user': request.user,
            'title': "VM Deploy"
        }

        return render(request, 'vmware/deploy.html', {"data": data})
