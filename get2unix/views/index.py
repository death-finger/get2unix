from django.views.generic import View
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.pwcrypt import EncryptStr


class Index(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        data = {
            'user': request.user,
            'title': 'Dashboard'
        }
        return render(request, 'base.html', {'data': data})


def login(request):
    if request.session.get('token') is not None:
        return HttpResponseRedirect('/', {'user': request.user})
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            request.session['token'] = EncryptStr().encrypt(username, password)
            print(request.session['token'])
            return HttpResponseRedirect('/', {'user': request.user})
        else:
            if request.method == 'POST':
                return render(request, 'login.html', {'login_error_info': 'Invalid username or password',
                                                      'username': username})
            else:
                return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login/')


class AccessDenied(View):
    def get(self, request):
        return render(request, '403.html', {'user': request.user})
    
    def put(self, request, *args, **kwagrs):
        return JsonResponse({'msg': "Access Denied", "code": 403, 'data': []})

    def post(self, request, *args, **kwagrs):
        return JsonResponse({'msg': "Access Denied", "code": 403, 'data': []})

    def delete(self, request, *args, **kwagrs):
        return JsonResponse({'msg': "Access Denied", "code": 403, 'data': []})
    

class PageNotFound(View):
    def get(self, request):
        return render(request, '404.html', {'user', request.user})

    def put(self, request, *args, **kwagrs):
        return JsonResponse({'msg': "Page not found", "code": 404, 'data': []})

    def post(self, request, *args, **kwagrs):
        return JsonResponse({'msg': "Page not found", "code": 404, 'data': []})

    def delete(self, request, *args, **kwagrs):
        return JsonResponse({'msg': "Page not found", "code": 404, 'data': []})

def test(request):
    return render(request, 'index.html')