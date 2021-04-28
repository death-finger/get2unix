from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from utils.redis_client import RedisOperator
from get2unix.settings import VC_CACHE_DB
import json
from django.http import JsonResponse


class Index(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        data = {
            'user': request.user,
            'title': "VM Inventory"
        }
        return render(request, 'vmware/inventory.html', {'data': data})
