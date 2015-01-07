from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Profile, Agrifield, IrrigationLog
from .forms import ProfileForm, AgrifieldForm, IrrigationlogForm
from .fmap import generate_map

from .irma_model import irrigation_amount_view


class IndexPageView(TemplateView):
    template_name = 'index.html'


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        generate_map([], [], [])
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
            #Map
            lats = [f.lat for f in context['agrifields']]
            lons = [f.lon for f in context['agrifields']]
            descprition = [str(f.name) for f in context['agrifields']]
            generate_map(lats, lons, descprition)
            #Irma Model
            for f in agrifields:
                f.irw = irrigation_amount_view(f.id)

        except Agrifield.DoesNotExist:
            context['agrifields'] = None
            context['irws'] = None

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
            context['agrifields'] = Agrifield.objects.filter(owner=self.request.user).all()
            context['fields_count'] = context['agrifields'].count()
        except Agrifield.DoesNotExist:
            context['agrifields'] = None
        return context


class UpdateAgrifield(UpdateView):
    model = Agrifield
    form_class = AgrifieldForm
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
            context['logs'] = IrrigationLog.objects.filter(agrifield=self.kwargs['pk']).all()
            context['logs_count'] = context['logs'].count()
        except Agrifield.DoesNotExist:
            context['logs'] = None
        return context


class UpdateIrrigationLog(UpdateView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    success_url = '/home'


class DeleteIrrigationLog(DeleteView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    success_url = '/home'
