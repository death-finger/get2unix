from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class Index(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = "/login/"
    permission_required = ('can_read_security_sudoscan',)

    def get(self, request):
        data = {
            'user': request.user,
            'title': "Sudo Scan Report"
        }
        return render(request, 'security/sudoscan.html', {"data": data})

