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
from django.conf.urls import url
from .views import vmware_api, security_api

urlpatterns = [
    url(r'^vmware/check/$', vmware_api.CheckHostname.as_view()),
    url(r'^vmware/tasks/$', vmware_api.GetTaskInfo.as_view()),
    url(r'^vmware/tasks/(?P<id>[0-9]+)/$', vmware_api.GetTaskInfo.as_view()),
    url(r'^vmware/getopts/$', vmware_api.GetVMwareOpts.as_view()),
    url(r'^vmware/inventory/$', vmware_api.Inventory.as_view()),
    url(r'^vmware/snapshots/$', vmware_api.GetSnapshots.as_view()),
    url(r'^vmware/deploy/$', vmware_api.Deploy.as_view()),
    url(r'^vmware/deploy/action/$', vmware_api.DeployAction.as_view()),
    url(r'^security/sudoscan/$', security_api.SudoScan.as_view()),
    url(r'^security/sudoscan/(?P<id>[0-9]+)$', security_api.SudoScanResult.as_view()),
    url(r'^security/vulscan/$', security_api.VulScan.as_view()),
    url(r'^security/vulscan/details/(?P<id>[0-9]+)$', security_api.VulScanDetail.as_view())
]
