from datetime import timedelta
from django.utils import timezone

from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Profile, Agrifield, IrrigationLog
from .forms import ProfileForm, AgrifieldForm, IrrigationlogForm

from .irma import utils as irma_utils
from .irma.main import get_parameters
from .irma.main import view_run


class IndexPageView(TemplateView):
    template_name = 'aira/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexPageView, self).get_context_data(**kwargs)
        print timezone.now() - timedelta(days=1)
        context['yesterday'] = (timezone.now() - timedelta(days=1)).date()
        return context


class HomePageView(TemplateView):
    template_name = 'aira/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        # Fetch models.Profile(User)
        try:
            context['profile'] = Profile.objects.get(farmer=self.request.user)
        except Profile.DoesNotExist:
            context['profile'] = None
        # Fetch models.Agrifield(User)
        try:
            agrifields = Agrifield.objects.filter(owner=self.request.user).all()
            context['agrifields'] = agrifields
            context['fields_count'] = agrifields.count()
            # Map
            # Defaults are city of Arta location
            # lats = [f.latitude for f in context['agrifields']] or [39.15]
            # lons = [f.longitude for f in context['agrifields']] or [20.98]
            # context['coords'] = zip(lats, lons)
            # Irma Model

            for f in agrifields:
                if not irma_utils.agripoint_in_raster(f):
                    f.outside_arta_raster = True
                else:
                    if irma_utils.timelog_exists(f):
                        f.irr_event = True
                        if irma_utils.last_timelog_in_dataperiod(f):
                            f.last_irr_event_outside_period = False
                            f.model = "With irrigation event run"
                            swb_view, f.sd, f.ed, f.adv, ovfc= view_run(f, flag_run="irr_event")
                        else:
                            f.last_irr_event_outside_period = True
                            f.model = "None irrigation event run"
                            swb_view, f.sd, f.ed, f.adv, ovfc = view_run(f, flag_run="no_irr_event")
                            f.over_fc = ovfc
                    else:
                        f.irr_event = False
                        f.model = "None irrigation event run"
                        swb_view, f.sd, f.ed, f.adv, ovfc = view_run(f, flag_run="no_irr_event")
                        f.over_fc = ovfc
                    f.fc_mm = swb_view.fc_mm
        except Agrifield.DoesNotExist:
            context['agrifields'] = None
        return context


class AdvicePageView(TemplateView):
    template_name = 'aira/advice.html'

    def get_context_data(self, **kwargs):
        context = super(AdvicePageView, self).get_context_data(**kwargs)
        f = Agrifield.objects.get(pk=self.kwargs['pk'])
        context['f'] = f
        context['fpars'] = get_parameters(f)
        if irma_utils.timelog_exists(f):
            f.irr_event = True
            if irma_utils.last_timelog_in_dataperiod(f):
                f.last_irr_event_outside_period = False
                f.model = "With irrigation event run"
                swb_view, f.sd, f.ed, f.adv, ovfc = view_run(f, flag_run="irr_event")
                f.swb_report = swb_view.wbm_report
            else:
                f.last_irr_event_outside_period = True
                f.model = "None irrigation event run"
                swb_view, f.sd, f.ed, f.adv, ovfc = view_run(f, flag_run="no_irr_event")
                f.swb_report = swb_view.wbm_report
        else:
            f.irr_event = False
            f.model = "None irrigation event run"
            swb_view, f.sd, f.ed, f.adv, ovfc = view_run(f, flag_run="no_irr_event")
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
    success_url = "/home"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(CreateAgrifield, self).form_valid(form)

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
    success_url = '/home'


class DeleteAgrifield(DeleteView):
    model = Agrifield
    form_class = AgrifieldForm
    success_url = '/home'


class CreateIrrigationLog(CreateView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    success_url = "/home"

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
    success_url = '/home'


class DeleteIrrigationLog(DeleteView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    success_url = '/home'
