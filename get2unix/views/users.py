from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import View


