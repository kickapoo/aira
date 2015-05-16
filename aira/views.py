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

from django.core.urlresolvers import reverse


class TryPageView(TemplateView):

    def get(self, request):
        user = authenticate(username="demo", password="demo")
        login(request, user)
        return redirect("home", user)


class IndexPageView(TemplateView):
    template_name = 'aira/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexPageView, self).get_context_data(**kwargs)
        context['yesterday'] = (timezone.now() - timedelta(days=1)).date()
        daily_r_fps, daily_e_fps, hourly_r_fps, hourly_e_fps = irma_utils.load_meteodata_file_paths()
        context['start_date'] = str(daily_e_fps[0][72:-4])
        context['end_date'] = daily_e_fps[-1][72:-4]
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
            context['url_username']  = self.request.user
        # User is url_slug <username>
        user = User.objects.get(username = url_username)
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


# Agrifield Create/Update/Delete
class CreateAgrifield(CreateView):
    model = Agrifield
    form_class = AgrifieldForm
    success_url = '/home'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(CreateAgrifield, self).form_valid(form)

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs['pk'])
        return reverse('home', kwargs={'username': field.owner })

    def get_context_data(self, **kwargs):
        context = super(CreateAgrifield, self).get_context_data(**kwargs)
        try:
            context['agrifields'] = Agrifield.objects.filter(
                owner=self.request.user).all()
            context['fields_count'] = context['agrifields'].count()
        except Agrifield.DoesNotExist:
            context['agrifields'] = None
        return context


# IrrigationLog Create/Update/Delete
class UpdateAgrifield(UpdateView):
    model = Agrifield
    form_class = AgrifieldForm
    template_name = 'aira/agrifield_update.html'

    def get_success_url(self):
        print self.kwargs
        field = Agrifield.objects.get(pk=self.kwargs['pk'])
        print field.owner
        return reverse('home', kwargs={'username': field.owner })

    def get_context_data(self, **kwargs):
        context = super(UpdateAgrifield, self).get_context_data(**kwargs)
        afieldobj = Agrifield.objects.get(pk=self.kwargs['pk'])
        context['default_parms'] = get_default_db_value(afieldobj)
        return context


class DeleteAgrifield(DeleteView):
    model = Agrifield
    form_class = AgrifieldForm

    def get_success_url(self):
        print self.kwargs
        field = Agrifield.objects.get(pk=self.kwargs['pk'])
        print field.owner
        return reverse('home', kwargs={'username': field.owner })


class CreateIrrigationLog(CreateView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    success_url = "/home"

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs['pk'])
        return reverse('home', kwargs={'username': field.owner })

    def form_valid(self, form):
        form.instance.agrifield = Agrifield.objects.get(pk=self.kwargs['pk'])
        return super(CreateIrrigationLog, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateIrrigationLog, self).get_context_data(**kwargs)
        try:
            context['agrifield'] = Agrifield.objects.get(pk=self.kwargs['pk'])
            context['logs'] = IrrigationLog.objects.filter(
                agrifield=self.kwargs['pk']).all()
            context['logs_count'] = context['logs'].count()
        except Agrifield.DoesNotExist:
            context['logs'] = None
        return context


class UpdateIrrigationLog(UpdateView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    template_name = 'aira/irrigationlog_update.html'

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs['pk'])
        return reverse('home', kwargs={'username': field.owner })


class DeleteIrrigationLog(DeleteView):
    model = IrrigationLog
    form_class = IrrigationlogForm

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs['pk'])
        return reverse('home', kwargs={'username': field.owner })
