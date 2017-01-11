import json
from collections import OrderedDict
from datetime import datetime, date, timedelta

from django.utils import dateparse
from django.shortcuts import redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.db.models import Sum
from django.utils import timezone


from aira.models import Agrifield, IrrigationLog
from aira.irma_utils.model import agrifield_meteo_data, agrifield_meteo_forecast_data


def get_irrigationlog_per_month_value(agrifield):
    """
    """
    result = OrderedDict({
        'January': 0,
        'February': 0,
        'March': 0,
        'April': 0,
        'May': 0,
        'June': 0,
        'July': 0,
        'August': 0,
        'September': 0,
        'November': 0,
        'December': 0,
    })

    db_result = IrrigationLog.objects.filter(agrifield=agrifield).values('applied_water', 'time')
    for i in db_result:
        month = str(i.get('time').strftime("%B"))
        year = str(i.get('time').strftime("%Y"))
        if str(timezone.now().year) == year:
            if month in result.keys():
                result[month] = result[month] + i.get('applied_water')
            else:
                result[month] = i.get('applied_water')
    return result


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


def create_irrigationlog(request):
    if request.is_ajax() and request.POST:

        agrifield = Agrifield.objects.get(
                            pk=int(request.POST.get('agrifield_id')))

        date = datetime.strptime(request.POST.get('date'), "%d/%m/%y").date()
        time = dateparse.parse_time(request.POST.get('time'))

        log = IrrigationLog.objects.create(
                agrifield=agrifield,
                time=datetime.combine(date, time),
                applied_water=float(request.POST.get('aw'))
        )

        response_data = {
            "message": "Irrigation Log Added",
            "time": log.time.strftime('%B %d, %Y'),
            "id": log.id,
            "aw": float(log.applied_water)
        }
        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
    return Http404


def delete_log(request):
    # Called in templates:aira:irrigationlog
    if request.is_ajax() and request.POST:
        pk = int(request.POST.get('log_id'))
        log = IrrigationLog.objects.get(pk=pk)
        log.delete()
        response_data = {
            "message": "Log  deleted",
        }
        return HttpResponse(
                json.dumps(response_data),
                content_type='application/json')
    raise Http404


def irrigationlog_stats(request):
    if request.is_ajax() and request.GET:
        pk = int(request.GET.get('agrifield_id'))
        agrifield = Agrifield.objects.get(pk=pk)
        now = timezone.now()
        year = date(now.year, 1, 1)
        annual = agrifield.irrigationlog_set.filter(
                  time__range=(year, now)).aggregate(Sum('applied_water'))
        month = agrifield.irrigationlog_set.filter(
                  time__range=(now - timedelta(30), now)).aggregate(Sum('applied_water'))
        last7days = agrifield.irrigationlog_set.filter(
                  time__range=(now - timedelta(7), now)).aggregate(Sum('applied_water'))
        last3days = agrifield.irrigationlog_set.filter(
                  time__range=(now - timedelta(3), now)).aggregate(Sum('applied_water'))

        response_data = {
            'month': month['applied_water__sum'],
            'annual': annual['applied_water__sum'],
            'last7days': last7days['applied_water__sum'],
            'last3days': last3days['applied_water__sum'],
        }
        return HttpResponse(
                json.dumps(response_data),
                content_type='application/json')
    raise Http404


def monthly_irrigationlog_plot(request):
    if request.is_ajax() and request.GET:
        pk = int(request.GET.get('agrifield_id'))
        agrifield = Agrifield.objects.get(pk=pk)
        plot_data = get_irrigationlog_per_month_value(agrifield)
        # Make sure that is order by month
        months_list = ['January', 'February', 'March', 'April', 'May',
                       'June', 'July', 'August', 'September', 'November',
                       'December']
        response_data = {
            'labels': months_list,
            'values': [plot_data[month] for month in months_list]
        }
        return HttpResponse(
                json.dumps(response_data),
                content_type='application/json')
    raise Http404


def agrifield_meteo(request):
    if request.is_ajax() and request.GET:
        pk = int(request.GET.get('agrifield_id'))
        agrifield = Agrifield.objects.get(pk=pk)
        rain, evap = agrifield_meteo_data(agrifield)

        pthlema_rain_json = [
            {'x': i[0].isoformat(), 'y':i[1]} for i in rain.items()
        ]
        pthlema_evap_json = [
            {'x': i[0].isoformat(), 'y':i[1]} for i in evap.items()
        ]
        response_data = {
            'rain': pthlema_rain_json[-30:],
            'evap': pthlema_evap_json[-30:]
        }
        return HttpResponse(
                json.dumps(response_data),
                content_type='application/json')
    return Http404


def agrifield_meteo_forecast(request):
    if request.is_ajax() and request.GET:
        pk = int(request.GET.get('agrifield_id'))
        agrifield = Agrifield.objects.get(pk=pk)
        rain, evap = agrifield_meteo_forecast_data(agrifield)

        pthlema_rain_json = [
            {'x': i[0].isoformat(), 'y':i[1]} for i in rain.items()
        ]
        pthlema_evap_json = [
            {'x': i[0].isoformat(), 'y':i[1]} for i in evap.items()
        ]
        response_data = {
            'rain': pthlema_rain_json,
            'evap': pthlema_evap_json
        }
        return HttpResponse(
                json.dumps(response_data),
                content_type='application/json')
    return Http404
