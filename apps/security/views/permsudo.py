from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from security.models import UsersGroup, Users, Groups


class SudoConfigs(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        return render(request, 'security/permsudo/sudoconfigs.html')


class UserGroups(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        return render(request, 'security/permsudo/usergroups.html')


class UserGroupsList(LoginRequiredMixin, View):
    login_url = '/login'

    def get(self, request):
        groups_list = Groups.objects.filter(type=0)
        data_list = []
        for item in groups_list:
            user_id_list = UsersGroup.objects.filter(group_id=item)
            data_list.append({
                'id': item.id,
                'group_name': item.name,
                'user_list': [x.user_id.name for x in user_id_list],
                'checked': False
            })
        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': data_list,
        })


class HostGroups(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        return render(request, 'security/permsudo/hostgroups.html')