import os
import glob

import folium
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from .models import Profile, Agrifield, Crop, IrrigationLog
from .forms import ProfileForm, AgriFieldFormset, CropFormset,\
    IrrigationLogFormset

from .irma_model import raster2pointTS, swb_finish_date, \
    run_swb_model

map_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def index(request):
    content = RequestContext(request)
    content_dict = {}
    return render_to_response('aira/index.html', content_dict, content)


@login_required()
def user_map(request):
    content = RequestContext(request)
    return render_to_response('map/user_map.html', {}, content)


@login_required()
def home(request):
    content = RequestContext(request)
    map_osm = folium.Map(location=[38, 23],
                         zoom_start=7)
    farmer = Profile()
    if Profile.objects.filter(farmer=request.user).exists():
        farmer = Profile.objects.get(farmer=request.user)
    farmer_agrifields = None
    count_agrifields = None
    if Agrifield.objects.filter(owner=request.user).exists():
        farmer_agrifields = Agrifield.objects.filter(owner=request.user)
        # Change count to a django query .count()
        count_agrifields = len(farmer_agrifields)
        # Map farmer fields
        lats = [agrifield.lat for agrifield in farmer_agrifields]
        lons = [agrifield.lon for agrifield in farmer_agrifields]
        agrifield_coords = zip(lons, lats)
        for coord in agrifield_coords:
            map_osm.circle_marker(list(coord),
                                  popup='{}-{}'.format('Owner',
                                                       str(request.user)),
                                  radius=1000,
                                  line_color='#FF0000', fill_color='#FF0000')

    map_osm.create_map(path=os.path.join(map_path,
                       'aira_project/templates/map/user_map.html'))
    content_dict = {'farmer': farmer,
                    'farmer_agrifields': farmer_agrifields,
                    'count_agrifields': count_agrifields}
    return render_to_response('aira/home.html', content_dict, content)


@login_required()
def next_irrigation(request, field_id, crop_id):
    content = RequestContext(request)
    precip_files = glob.glob(os.path.join(settings.AIRA_DATA_FILE_DIR,
                             'daily_rain*.tif'))
    evap_files = glob.glob(os.path.join(settings.AIRA_DATA_FILE_DIR,
                           'daily_evaporation*.tif'))
    f = Agrifield.objects.get(pk=field_id)
    c = Crop.objects.get(pk=crop_id)
    # Location Parameters
    lat = f.lat
    lon = f.lon
    # Meteo Parameters
    precip = raster2pointTS(lat, lon, precip_files)
    evap = raster2pointTS(lat, lon, evap_files)
    print precip
    print evap
    # fc later will be provided from a raster map
    # wp later will be provided from a raster map
    fc = 0.5
    wp = 1
    # Parameters provided from aira.models
    rd = float(c.crop_type.root_depth)
    kc = float(c.crop_type.crop_coefficient)
    irrigation_efficiency = float(c.irrigation_type.efficiency)
    initial_soil_moisture = fc
    p = 1
    rd_factor = 1
    next_irr = "No irrigation log to calculate model"
    if c.irrigationlog_set.exists():
        start_date = c.irrigationlog_set.latest().time.replace(tzinfo=None)
        finish_date = swb_finish_date(precip, evap)
        next_irr = run_swb_model(precip, evap, fc, wp, rd, kc, p,
                                 irrigation_efficiency, rd_factor,
                                 start_date, initial_soil_moisture, finish_date)
    content_dict = {'f': f,
                    'c': c,
                    'next_irr': round(next_irr, 2)}
    return render_to_response('aira/next_irrigation.html',
                              content_dict, content)


@login_required()
def edit_profile(request):
    content = RequestContext(request)
    profile = Profile(farmer=request.user)
    if Profile.objects.filter(farmer=request.user).exists():
        profile = Profile.objects.get(farmer=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            p.farmer = request.user
            p.save()
            return redirect('aira.views.home')
    else:
        form = ProfileForm(instance=profile)
    content_dict = {'form': form}
    return render_to_response('aira/edit_profile.html', content_dict, content)


@login_required()
def update_fields(request):
    content = RequestContext(request)
    if request.method == "POST":
        field_forms = AgriFieldFormset(request.POST or None,
                                       instance=request.user)
        if field_forms.is_valid():
            field_forms.save()
            return redirect(update_fields)
    else:
        qs = Agrifield.objects.order_by('-name')
        field_forms = AgriFieldFormset(instance=request.user, queryset=qs)
    contect_dict = {'formset': field_forms}
    return render_to_response('aira/update_fields.html',
                              contect_dict, content)


@login_required()
def update_crop(request, field_id):
    content = RequestContext(request)
    if request.method == "POST":
        crop_form = CropFormset(request.POST or None,
                                instance=get_object_or_404(Agrifield,
                                                           pk=field_id))
        if crop_form.is_valid():
            crop_form.save()
            return redirect('update_crop', field_id=field_id)
    else:
        qs = Crop.objects.order_by('-crop_type')
        crop_form = CropFormset(instance=get_object_or_404(Agrifield,
                                pk=field_id), queryset=qs)
    content_dict = {'formset': crop_form, 'field_id': field_id}
    return render_to_response('aira/update_crop.html',
                              content_dict, content)


@login_required()
def update_irrigationlog(request, crop_id):
    content = RequestContext(request)
    if request.method == "POST":
        formset = IrrigationLogFormset(request.POST or None,
                                       instance=get_object_or_404(Crop,
                                                                  pk=crop_id))
        if formset.is_valid():
            for form in formset.forms:
                for field in form:
                    print field
                    form.save()
            return redirect('update_irrigationlog',
                            crop_id=crop_id)
    else:
        qs = IrrigationLog.objects.filter(agrifield_crop=crop_id)
        formset = IrrigationLogFormset(instance=get_object_or_404(Crop, pk=crop_id), queryset=qs)
    contect_dict = {'formset': formset,
                    'crop_id': crop_id}
    return render_to_response('aira/update_irrigationlog.html',
                              contect_dict, content)
