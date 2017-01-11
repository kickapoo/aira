import csv
from datetime import date, timedelta
import os
import json

from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from django.contrib.auth.models import User
from .models import Profile, Agrifield, IrrigationLog
from .forms import ProfileForm, AgrifieldForm, IrrigationlogForm

from .irma_utils import *

# def get_object(self, queryset=None):
#         obj = super(ContactDelete, self).get_object()
#         if not obj.owner == self.request.user:
#             raise Http404


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
        object_list = Agrifield.objects.filter(owner=user).order_by('-created_at')

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
        object_list = Agrifield.objects.filter(owner=user).order_by('-created_at')
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


















class IrrigationPerformance(TemplateView):
    template_name = 'aira/performance-chart.html'

    def get_context_data(self, **kwargs):
        context = super(IrrigationPerformance,
                        self).get_context_data(**kwargs)
        # Load data paths
        f = Agrifield.objects.get(pk=self.kwargs['pk_a'])
        f.can_edit(self.request.user)
        f.chart = get_performance_chart(f)
        if f.chart:
            f.chart.sum_ifinal = sum(f.chart.chart_ifinal)
            f.chart.sum_applied_water = sum(f.chart.applied_water)
            f.chart.percentage_diff = _("Not Available")
            if f.chart.sum_ifinal != 0.0:
                f.chart.percentage_diff = round(
                    ((f.chart.sum_applied_water - f.chart.sum_ifinal) /
                     f.chart.sum_ifinal) * 100 or 0.0)
        context['f'] = f
        return context


def performance_csv(request, pk):
    f = Agrifield.objects.get(pk=pk)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}-performance.csv"'.format(f.id)
    f.can_edit(request.user)
    results = get_performance_chart(f)
    writer = csv.writer(response)
    writer.writerow(['Date', 'Estimated Irrigation Water Amount',
                     'Applied Irrigation Water Amount',
                     'Effective precipitation'])
    writer.writerow(['', 'amount (mm)', 'amount (mm)', 'amount (mm)'])
    for row in zip(results.chart_dates, results.chart_ifinal,
                   results.applied_water, results.chart_peff):
            writer.writerow(row)
    return response


class ConversionTools(TemplateView):
    template_name = 'aira/tools.html'


class AdvicePageView(TemplateView):
    template_name = 'aira/advice.html'

    def get_context_data(self, **kwargs):
        context = super(AdvicePageView, self).get_context_data(**kwargs)
        # Load data paths
        Inet_in = "NO"
        f = Agrifield.objects.get(pk=self.kwargs['pk'])
        f.can_edit(self.request.user)
        context['f'] = f
        if not agripoint_in_raster(f):
            return context
        context['fpars'] = get_parameters(f)
        f.results = model_results(f, "NO")
        return context


class UpdateIrrigationLog(UpdateView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    template_name = 'aira/irrigationlog_update.html'

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs['pk_a'])
        return reverse('home', kwargs={'username': field.owner})

    def get_context_data(self, **kwargs):
        context = super(UpdateIrrigationLog, self).get_context_data(**kwargs)
        afieldobj = Agrifield.objects.get(pk=self.kwargs['pk_a'])
        afieldobj.can_edit(self.request.user)
        log = IrrigationLog.objects.get(pk=self.kwargs['pk'])
        log.can_edit(afieldobj)
        context['agrifield_id'] = afieldobj.id
        return context


class DeleteIrrigationLog(DeleteView):
    model = IrrigationLog
    form_class = IrrigationlogForm

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs['pk_a'])
        return reverse('home', kwargs={'username': field.owner})


def remove_supervised_user_from_user_list(request):
    # Called in templates:aira:home
    if request.is_ajax() and request.POST:
        supervised_profile = Profile.objects.get(
                                     pk=int(request.POST.get('supervised_id')))
        supervised_profile.supervisor = None
        supervised_profile.save()
        response_data = {
            "message": "Success!!!",
        }
        return HttpResponse(
                json.dumps(response_data),
                content_type='application/json')
    raise Http404
