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
from .views import permsudo, tempsudo, sudoscan, vulscan

urlpatterns = [
    url(r'^permsudo/$', permsudo.SudoConfigs.as_view()),
    url(r'^permsudo/list/$', permsudo.UserGroupsList.as_view()),
    url(r'^permsudo/usergroups/$', permsudo.UserGroups.as_view()),
    url(r'^permsudo/hostgroups/$', permsudo.HostGroups.as_view()),
    url(r'^tempsudo/$', tempsudo.Index.as_view()),
    url(r'^tempsudo/task/$', tempsudo.SudoTask.as_view()),
    url(r'^sudoscan/$', sudoscan.Index.as_view()),
    url(r'^vulscan/$', vulscan.Index.as_view()),
]
