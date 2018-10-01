import csv
from datetime import date, timedelta
import json
import os

from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User

from .forms import ProfileForm, AgrifieldForm, IrrigationlogForm
from .irma.main import (agripoint_in_raster, get_default_db_value,
                        get_parameters, get_performance_chart,
                        load_meteodata_file_paths, model_results)
from .models import Profile, Agrifield, IrrigationLog


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
                     f.chart.sum_ifinal)*100 or 0.0)
        context['f'] = f
        return context


def performance_csv(request, pk):
    f = Agrifield.objects.get(pk=pk)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="{}-performance.csv"'.format(f.id)
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


class TryPageView(TemplateView):

    def get(self, request):
        user = authenticate(username="demo", password="demo")
        login(request, user)
        return redirect("home", user)


class ConversionTools(TemplateView):
    template_name = 'aira/tools.html'


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


class HomePageView(TemplateView):
    template_name = 'aira/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        # Load data paths
        url_username = kwargs.get('username')
        context['url_username'] = kwargs.get('username')
        if kwargs.get('username') is None:
            url_username = self.request.user
            context['url_username'] = self.request.user
        # User is url_slug <username>
        user = User.objects.get(username=url_username)

        # Fetch models.Profile(User)
        try:
            context['profile'] = Profile.objects.get(farmer=self.request.user)
        except Profile.DoesNotExist:
            context['profile'] = None
        # Fetch models.Agrifield(User)
        try:
            agrifields = Agrifield.objects.filter(owner=user).all()
            for f in agrifields:
                # Check if user is allowed or 404
                f.can_edit(self.request.user)
            # For Profile section
            # Select self.request.user user that set him supervisor
            if Profile.objects.filter(supervisor=self.request.user).exists():
                supervising_users = Profile.objects.filter(
                    supervisor=self.request.user)
                context['supervising_users'] = supervising_users

            for f in agrifields:
                if not agripoint_in_raster(f):
                    f.outside_arta_raster = True
                f.results = model_results(f, "YES")

            context['agrifields'] = agrifields
            context['fields_count'] = len(agrifields)
        except Agrifield.DoesNotExist:
            context['agrifields'] = None
        return context


class AdvicePageView(TemplateView):
    template_name = 'aira/advice.html'

    def get_context_data(self, **kwargs):
        context = super(AdvicePageView, self).get_context_data(**kwargs)
        # Load data paths
        f = Agrifield.objects.get(pk=self.kwargs['pk'])
        f.can_edit(self.request.user)
        context['f'] = f
        if not agripoint_in_raster(f):
            return context
        context['fpars'] = get_parameters(f)
        f.results = model_results(f, "NO")
        return context


# Profile Create/Update
class CreateProfile(CreateView):
    model = Profile
    form_class = ProfileForm
    success_url = "/home"

    def get_form(self, form_class):
        form = super(CreateProfile, self).get_form(form_class)
        if self.request.user in form.fields['supervisor'].queryset:
            form.fields['supervisor'].queryset = \
                        form.fields['supervisor'].queryset.exclude(
                        pk=self.request.user.id)
        return form

    def form_valid(self, form):
        form.instance.farmer = self.request.user
        return super(CreateProfile, self).form_valid(form)


class UpdateProfile(UpdateView):
    model = Profile
    form_class = ProfileForm
    success_url = "/home"

    def get_form(self, form_class):
        form = super(UpdateProfile, self).get_form(form_class)
        if self.request.user in form.fields['supervisor'].queryset:
            form.fields['supervisor'].queryset = \
                        form.fields['supervisor'].queryset.exclude(
                        pk=self.request.user.id)
        return form

    def get_context_data(self, **kwargs):
        context = super(UpdateProfile, self).get_context_data(**kwargs)
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        if not self.request.user == profile.farmer:
            raise Http404
        return context


class DeleteProfile(DeleteView):
    model = Profile

    def get_success_url(self):
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        user = User.objects.get(pk=profile.farmer.id)
        # Delete all user data using bult in cascade delete
        user.delete()
        return reverse('welcome')


# Agrifield Create/Update/Delete
class CreateAgrifield(CreateView):
    model = Agrifield
    form_class = AgrifieldForm

    def form_valid(self, form):
        user = User.objects.get(username=self.kwargs['username'])
        form.instance.owner = user
        return super(CreateAgrifield, self).form_valid(form)

    def get_success_url(self):
        url_username = self.kwargs['username']
        return reverse('home', kwargs={'username': url_username})

    def get_context_data(self, **kwargs):
        context = super(CreateAgrifield, self).get_context_data(**kwargs)
        try:
            url_username = self.kwargs['username']
            user = User.objects.get(username=url_username)
            context['agrifields'] = Agrifield.objects.filter(
                owner=user).all()
            context['fields_count'] = context['agrifields'].count()
            context['agrifield_user'] = user

        except Agrifield.DoesNotExist:
            context['agrifields'] = None
        return context


# IrrigationLog Create/Update/Delete
class UpdateAgrifield(UpdateView):
    model = Agrifield
    form_class = AgrifieldForm
    template_name = 'aira/agrifield_update.html'

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs['pk'])
        return reverse('home', kwargs={'username': field.owner})

    def get_context_data(self, **kwargs):
        context = super(UpdateAgrifield, self).get_context_data(**kwargs)
        afieldobj = Agrifield.objects.get(pk=self.kwargs['pk'])
        afieldobj.can_edit(self.request.user)
        context['agrifield_user'] = afieldobj.owner
        if agripoint_in_raster(afieldobj):
            context['default_parms'] = get_default_db_value(afieldobj)
        return context


class DeleteAgrifield(DeleteView):
    model = Agrifield
    form_class = AgrifieldForm

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs['pk'])
        return reverse('home', kwargs={'username': field.owner})

    def get_context_data(self, **kwargs):
        context = super(DeleteAgrifield, self).get_context_data(**kwargs)
        afieldobj = Agrifield.objects.get(pk=self.kwargs['pk'])
        afieldobj.can_edit(self.request.user)
        return context


class CreateIrrigationLog(CreateView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    success_url = "/home"

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs['pk'])
        return reverse('home', kwargs={'username': field.owner})

    def form_valid(self, form):
        form.instance.agrifield = Agrifield.objects.get(pk=self.kwargs['pk'])
        return super(CreateIrrigationLog, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateIrrigationLog, self).get_context_data(**kwargs)
        try:
            context['agrifield'] = Agrifield.objects.get(pk=self.kwargs['pk'])
            afieldobj = Agrifield.objects.get(pk=self.kwargs['pk'])
            afieldobj.can_edit(self.request.user)
            context['logs'] = IrrigationLog.objects.filter(
                agrifield=afieldobj).all()
            context['logs_count'] = context['logs'].count()
            context['agrifield_user'] = afieldobj.owner
        except Agrifield.DoesNotExist:
            context['logs'] = None
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
