import json

from django.contrib.auth.models import User
from aira.models import Agrifield
from django.contrib.auth import logout
from django.http import HttpResponse, Http404


def delete_account(request):
    # Called in templates:aira:profile_form
    if request.is_ajax() and request.POST:
        user = User.objects.get(username=request.user.username)
        logout(request)
        user.delete()
        response_data = {
            "message": "Delete User Success",
        }
        return HttpResponse(
                json.dumps(response_data),
                content_type='application/json')
    raise Http404


def set_password(request):
    # Called in templates:aira:profile_form
    if request.is_ajax() and request.POST:
        user = User.objects.get(username=request.user.username)
        user.set_password(request.POST.get('password'))
        user.save()
        response_data = {
            "message": "Account Password User Success",
        }
        return HttpResponse(
                json.dumps(response_data),
                content_type='application/json')
    raise Http404


def delete_agrifield(request):
    """Delete an Agrifield via Ajax call."""

    # Called in templates:aira:home
    if request.is_ajax() and request.POST:
        pk = int(request.POST.get('agrifield_pk'))
        agrifield = Agrifield.objects.get(pk=pk)
        agrifield.delete()
        response_data = {
            "message": "Agrifield deleted",
        }
        return HttpResponse(
                json.dumps(response_data),
                content_type='application/json')
    raise Http404
