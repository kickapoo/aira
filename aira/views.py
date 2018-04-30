from datetime import date, timedelta
import os

from django.utils import timezone
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from .swb.utils import load_meteodata_file_paths
from .forms import AgrifieldForm, ProfileForm, IrrigationlogForm
from .models import Agrifield, Profile, IrrigationLog


class IndexPageView(TemplateView):
    template_name = 'aira/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexPageView, self).get_context_data(**kwargs)
        daily_r_fps, daily_e_fps = load_meteodata_file_paths()[:2]
        dates_r = sorted([os.path.basename(x).split('.')[0].partition('-')[2]
                          for x in daily_r_fps])
        dates_e = sorted([os.path.basename(x).split('.')[0].partition('-')[2]
                          for x in daily_e_fps])
        common_dates = [x for x in dates_r if x in dates_e]
        y1, m1, d1 = (int(x) for x in common_dates[0].split('-'))
        y2, m2, d2 = (int(x) for x in common_dates[-1].split('-'))
        context['start_date'] = date(y1, m1, d1)
        context['end_date'] = date(y2, m2, d2) - timedelta(days=1)
        return context


class HomePageView(ListView):
    template_name = 'aira/home.html'
    model = Agrifield

    def get_queryset(self):
        if 'username' in self.kwargs:
            kwargs_username = self.kwargs['username']
            supervised_user = User.objects.get(username=kwargs_username)
            agrifields = self.model.objects.filter(owner=supervised_user)
            return agrifields
        return self.model.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        return context


class UpdateProfile(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'aira/profile_form.html'
    success_url = 'home'

    def get_object(self):
        return Profile.objects.get(farmer=self.request.user)

    def get_form(self, form_class):
        form = super(UpdateProfile, self).get_form(form_class)
        if self.request.user in form.fields['supervisor'].queryset:
            form.fields['supervisor'].queryset = \
                        form.fields['supervisor'].queryset.exclude(
                        pk=self.request.user.id)
        return form


class CreateAgrifield(CreateView):
    model = Agrifield
    form_class = AgrifieldForm
    template_name = 'aira/agrifield_create.html'

    def form_valid(self, form):
        user = User.objects.get(username=self.kwargs['username'])
        form.instance.owner = user
        return super(CreateAgrifield, self).form_valid(form)

    def get_success_url(self):
        user = User.objects.get(username=self.kwargs['username'])
        return reverse('add-agrifield', kwargs={'username': user.username})

    def get_context_data(self, **kwargs):
        context = super(CreateAgrifield, self).get_context_data(**kwargs)
        user = User.objects.get(username=self.kwargs['username'])
        object_list = Agrifield.objects.filter(
            owner=user).order_by('-created_at')

        paginator = Paginator(object_list, 5)
        page = self.request.GET.get('page')

        try:
            object_list = paginator.page(page)
        except PageNotAnInteger:
            object_list = paginator.page(1)
        except EmptyPage:
            object_list = paginator.page(paginator.num_pages)

        context['object_list'] = object_list
        return context


class UpdateAgrifield(UpdateView):
    model = Agrifield
    form_class = AgrifieldForm
    slug_url_kwarg = 'slug'
    template_name = 'aira/agrifield_update.html'

    def get_success_url(self):
        agrifield = Agrifield.objects.get(slug=self.kwargs['slug'])
        return reverse('edit-agrifield', kwargs={
                                            'slug': agrifield.slug,
                                            'username': agrifield.owner})

    def get_context_data(self, **kwargs):
        context = super(UpdateAgrifield, self).get_context_data(**kwargs)
        agrifield = Agrifield.objects.get(slug=self.kwargs['slug'])
        user = User.objects.get(username=agrifield.owner.username)
        object_list = Agrifield.objects.filter(
            owner=user).order_by('-created_at')
        paginator = Paginator(object_list, 5)

        page = self.request.GET.get('page')

        try:
            object_list = paginator.page(page)
        except PageNotAnInteger:
            object_list = paginator.page(1)
        except EmptyPage:
            object_list = paginator.page(paginator.num_pages)

        context['object_list'] = object_list
        context['viewing_user'] = user
        context['default_parms'] = agrifield.db_default_agroparameters()
        context['agrifield'] = agrifield
        return context


class CreateIrrigationLog(CreateView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    success_url = 'home'
    template_name = 'aira/advisor.html'

    def form_valid(self, form):
        form.instance.agrifield = Agrifield.objects.get(pk=self.kwargs['pk'])
        return super(CreateIrrigationLog, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateIrrigationLog, self).get_context_data(**kwargs)
        context['agrifield'] = Agrifield.objects.get(slug=self.kwargs['slug'])
        object_list = IrrigationLog.objects.filter(
                                        agrifield=context['agrifield']).all()
        paginator = Paginator(object_list, 5)
        page = self.request.GET.get('page')
        try:
            object_list = paginator.page(page)
        except PageNotAnInteger:
            object_list = paginator.page(1)
        except EmptyPage:
            object_list = paginator.page(paginator.num_pages)

        context['object_list'] = object_list
        context['today'] = timezone.now().date()
        context['now'] = timezone.now().time()
        return context
