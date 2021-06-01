import json
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from security.models import SudoTasks


class Index(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ('can_read_security_tempsudo',)

    def get(self, request):

        data = {
            'user': request.user,
            'title': "Temporary Sudo Management"
        }
        return render(request, 'security/tempsudo.html', {"data": data})


class SudoTask(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ('can_read_security_tempsudo',)

    def get(self, request):
        task_list = SudoTasks.objects.all()
        data_list = []
        for item in task_list:
            data_list.append({
                'id': item.id,
                'users': json.loads(item.users),
                'operator': item.operator,
                'ticket': item.ticket,
                'hosts': json.loads(item.hosts),
                'time_created': item.time_created.strftime("%Y-%m-%d %H:%M:%S"),
                'effective_days': str(item.effective_days) + " Days",
                'status': item.status_dict[item.status],
                'checked': False
            })
        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': data_list,
        })

    # TODO: Move this into api/vmware_api
    def post(self, request):
        if request.POST.get('action') == 'add':
            users = request.POST.get('users').lstrip().rstrip().split('\n')
            hosts = request.POST.get('hosts').lstrip().rstrip().split('\n')
            ticket = request.POST.get('ticket')
            days = request.POST.get('effective_days')
            nopasswd = True if request.POST.get('nopasswd') != "false" else False
            data = {
                'users': json.dumps(users),
                'operator': request.user.username,
                'ticket': ticket,
                'hosts': json.dumps(hosts),
                'effective_days': days,
                'status': 0,
                'nopasswd': nopasswd,
            }
            SudoTasks.objects.create(**data)

        elif request.POST.get('action') == 'delete':
            id_list = request.POST.get('task_id')
            for id in id_list.split(','):
                task_obj = SudoTasks.objects.filter(id=id)
                if task_obj.first().status != 3:
                    task_obj.update(status=2)

        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': ""
        })
