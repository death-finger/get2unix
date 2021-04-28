"""get2unix URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from get2unix.views import index

urlpatterns = [
    url(r'^index', index.test),
    url(r'^admin/', admin.site.urls),
    url(r'^$', index.Index.as_view()),
    url(r'^login/$', index.login),
    url(r'^logout/$', index.logout),
    url(r'^403/$', index.AccessDenied.as_view()),
    url(r'^404/$', index.PageNotFound.as_view()),
    url(r'^api/', include('api.urls')),
    url(r'^vmware/', include('vmware.urls')),
    url(r'^security/', include('security.urls')),
]
