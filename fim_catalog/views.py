from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
import datetime

from openconext import metadata, pdpclient, app_list, vootclient

def index(request):
    apps = app_list.get_app_list(request)
    is_admin = vootclient.get_user_groups(request)
    display_name = request.META['displayName']

    context = {
        'app_list': apps,
        'display_name': display_name,
        'is_admin': is_admin,
    }
    return render(request, 'fim_catalog/index.html', context)
