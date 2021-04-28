from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class Index(LoginRequiredMixin, View):
    login_url = '/login/'
    # permission_required = ('can_read_security_tempsudo',)

    def get(self, request):
        data = {
            'user': request.user,
            'title': "Vulnerability Scan Report"
        }
        return render(request, 'security/vulscan.html', {"data": data})