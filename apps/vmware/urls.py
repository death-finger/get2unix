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
from .views import deploy, snapshots, inventory

from rest_framework.routers import DefaultRouter


# urlpatterns = [
#     url(r'^$', inventory.Index.as_view()),
#     url(r'^inventory/$', inventory.Index.as_view()),
#     url(r'^snapshots/$', snapshots.BulkTakeSnapshot.as_view()),
#     url(r'^deploy/$', deploy.BulkDeployVM.as_view()),
# ]

# urlpatterns = [
#     url(r'^inventory/$', inventory.InventoryView.as_view()),
#     url(r'^snapshots/$', snapshots.BulkTakeSnapshot.as_view()),
#     url(r'^deploy/$', deploy.DeployView.as_view()),
# ]

router = DefaultRouter()
router.register(r'inventory', inventory.InventoryViewSet, basename='inventory')
router.register(r'deploy', deploy.DeployViewSet, basename='deploy')
urlpatterns = router.urls
