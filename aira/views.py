from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib.auth.models import User
from .models import Profile, Agrifield, IrrigationLog
from .forms import ProfileForm, AgrifieldForm, IrrigationlogForm

from .irma import utils as irma_utils
from .irma.main import get_parameters
from .irma.main import view_run
from .irma.main import get_default_db_value
from .irma.main import availiable_data_period
from django.core.urlresolvers import reverse
from django.http import Http404


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
        context['yesterday'] = (timezone.now() - timedelta(days=1)).date()
        start_data, end_data = availiable_data_period(lat=39.15, long=20.98)
        context['start_date'] = start_data
        context['end_date'] = end_data
        return context


class AlbedoMapsPageView(TemplateView):
    template_name = 'aira/albedo_maps.html'


class HomePageView(TemplateView):
    template_name = 'aira/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        # Load data paths
        url_username = kwargs.get('username')
        context['url_username'] = kwargs.get('username')
        if kwargs.get('username') == None:
            url_username = self.request.user
            context['url_username'] = self.request.user
        # User is url_slug <username>
        user = User.objects.get(username=url_username)
        daily_r_fps, daily_e_fps, hourly_r_fps, hourly_e_fps = irma_utils.load_meteodata_file_paths()
        Inet_in = "YES"
        # Fetch models.Profile(User)
        # Fetch alwayer self.request.user
        try:
            context['profile'] = Profile.objects.get(farmer=self.request.user)
        except Profile.DoesNotExist:
            context['profile'] = None
        # Fetch models.Agrifield(User)
        try:
            agrifields = Agrifield.objects.filter(owner=user).all()
            for f in agrifields:
                f.can_edit(self.request.user)
            # For Profile section
            # Select self.request.user user that set him supervisor
            if Profile.objects.filter(supervisor=self.request.user).exists():
                supervising_users = Profile.objects.filter(
                    supervisor=self.request.user)
                context['supervising_users'] = supervising_users
            context['agrifields'] = agrifields
            context['fields_count'] = len(agrifields)
            for f in agrifields:
                if not irma_utils.agripoint_in_raster(f):
                    f.outside_arta_raster = True
                else:
                    if irma_utils.timelog_exists(f):
                        f.irr_event = True
                        if irma_utils.last_timelog_in_dataperiod(f, daily_r_fps, daily_e_fps):
                            f.last_irr_event_outside_period = False
                            flag_run = "irr_event"
                            swb_view, f.sd, f.ed, f.adv, ovfc, f.sdh, f.edh, f.ifinal = view_run(
                                f, flag_run, Inet_in, daily_r_fps, daily_e_fps,
                                hourly_r_fps, hourly_e_fps)
                            f.adv_sorted = sorted(f.adv.iteritems())
                            f.last_irrigate_date = f.irrigationlog_set.latest().time
                        else:
                            f.last_irr_event_outside_period = True
                            flag_run = "no_irr_event"
                            swb_view, f.sd, f.ed, f.adv, ovfc, f.sdh, f.edh, f.ifinal = view_run(
                                f, flag_run, Inet_in, daily_r_fps, daily_e_fps,
                                hourly_r_fps, hourly_e_fps)
                            f.adv_sorted = sorted(f.adv.iteritems())
                            f.over_fc = ovfc
                    else:
                        f.irr_event = False
                        flag_run = "no_irr_event"
                        swb_view, f.sd, f.ed, f.adv, ovfc, f.sdh, f.edh, f.ifinal = view_run(
                            f, flag_run, Inet_in, daily_r_fps, daily_e_fps,
                            hourly_r_fps, hourly_e_fps)
                        f.adv_sorted = sorted(f.adv.iteritems())
                        f.over_fc = ovfc
                    f.fc_mm = swb_view.fc_mm
        except Agrifield.DoesNotExist:
            context['agrifields'] = None
        return context


class AdvicePageView(TemplateView):
    template_name = 'aira/advice.html'

    def get_context_data(self, **kwargs):
        context = super(AdvicePageView, self).get_context_data(**kwargs)
        # Load data paths
        daily_r_fps, daily_e_fps, hourly_r_fps, hourly_e_fps = irma_utils.load_meteodata_file_paths()
        Inet_in = "NO"
        f = Agrifield.objects.get(pk=self.kwargs['pk'])
        f.can_edit(self.request.user)
        context['f'] = f
        context['fpars'] = get_parameters(f)
        if irma_utils.timelog_exists(f):
            f.irr_event = True
            if irma_utils.last_timelog_in_dataperiod(f, daily_r_fps, daily_e_fps):
                f.last_irr_event_outside_period = False
                flag_run = "irr_event"
                swb_view, f.sd, f.ed, f.adv, ovfc, f.sdh, f.edh, f.ifinal = view_run(
                    f, flag_run, Inet_in, daily_r_fps, daily_e_fps,
                    hourly_r_fps, hourly_e_fps)
                f.adv_sorted = sorted(f.adv.iteritems())
                f.swb_report = swb_view.wbm_report
            else:
                f.last_irr_event_outside_period = True
                flag_run = "no_irr_event"
                swb_view, f.sd, f.ed, f.adv, ovfc, f.sdh, f.edh, f.ifinal = view_run(
                    f, flag_run, Inet_in, daily_r_fps, daily_e_fps,
                    hourly_r_fps, hourly_e_fps)
                f.adv_sorted = sorted(f.adv.iteritems())
                f.swb_report = swb_view.wbm_report
        else:
            f.irr_event = False
            f.model = "None irrigation event run"
            flag_run = "no_irr_event"
            swb_view, f.sd, f.ed, f.adv, ovfc, f.sdh, f.edh, f.ifinal = view_run(
                f, flag_run, Inet_in, daily_r_fps, daily_e_fps,
                hourly_r_fps, hourly_e_fps)
            f.adv_sorted = sorted(f.adv.iteritems())
            f.swb_report = swb_view.wbm_report
        return context


# Profile Create/Update
class CreateProfile(CreateView):
    model = Profile
    form_class = ProfileForm
    success_url = "/home"

    def form_valid(self, form):
        form.instance.farmer = self.request.user
        return super(CreateProfile, self).form_valid(form)


class UpdateProfile(UpdateView):
    model = Profile
    form_class = ProfileForm
    success_url = "/home"

    def get_context_data(self, **kwargs):
        context = super(UpdateProfile, self).get_context_data(**kwargs)
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        if not self.request.user == profile.farmer:
            raise Http404
        return context


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
        print irma_utils.agripoint_in_raster(afieldobj)
        if irma_utils.agripoint_in_raster(afieldobj):
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
        return context


class DeleteIrrigationLog(DeleteView):
    model = IrrigationLog
    form_class = IrrigationlogForm

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs['pk_a'])
        return reverse('home', kwargs={'username': field.owner})
