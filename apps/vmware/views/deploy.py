from get2unix.settings import VC_LIST
from rest_framework import viewsets
from rest_framework.response import Response
from vmware.serializers import DeploySerializer
from vmware.models import DeployLists

# class BulkDeployVM(LoginRequiredMixin, PermissionRequiredMixin, View):
#     login_url = '/login/'
#     permission_required = ('vmware.can_read_vmware_deploy_list', 'vmware.can_change_vmware_deploy_list',
#                            'vmware.can_add_vmware_deploy_list', 'vmware.can_delete_vmware_deploy_list')
#
#     def get(self, request):
#         data = {
#             "vc_list": VC_LIST,
#             'user': request.user,
#             'title': "VM Deploy"
#         }
#
#         return render(request, 'vmware/deploy.html', {"data": data})


class DeployViewSet(viewsets.ModelViewSet):
    queryset = DeployLists.objects.all()
    serializer_class = DeploySerializer

    def list(self, request):
        return Response(self.serializer_class(self.queryset, many=True).data)

    def create(self, request):
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
            'cpu': int(request.POST.get('cpu')) or 4,
            'memory': int(request.POST.get('memory')) or 8,
            'user': request.user.username,
            'state': 1,
            'token': request.session.get('token')
        }
        serializer = self.serializer_class(data=deploy_dict)
        serializer.is_valid()
        serializer.save()
        print('OK')