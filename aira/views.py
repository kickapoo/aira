import os
import folium
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from .models import Profile, Agrifield, Crop
from .forms import ProfileForm, AgriFieldFormset, CropFormset

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
        count_agrifields = len(farmer_agrifields)
        # Map farmer fields
        lats = [agrifield.lat for agrifield in farmer_agrifields]
        lons = [agrifield.lon for agrifield in farmer_agrifields]
        agrifield_coords = zip(lons, lats)
        for coord in agrifield_coords:
            print list(coord)
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
