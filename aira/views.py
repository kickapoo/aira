from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Profile, Agrifield
from .forms import ProfileForm, AgrifieldForm

from fmap import generate_map


class IndexPageView(TemplateView):
    template_name = 'index.html'


class HomePageView(TemplateView):
    template_name = 'home.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomePageView, self).dispatch(*args, **kwargs)

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
            lats = [f.lat for f in context['agrifields']]
            lons = [f.lon for f in context['agrifields']]
            descprition = [f.name for f in context['agrifields']]
            print lats, lons, descprition
            generate_map(lats, lons, descprition)
        except Agrifield.DoesNotExist:
            context['agrifields'] = None

        return context


# Profile Create/Update
class CreateProfile(CreateView):
    model = Profile
    form_class = ProfileForm
    success_url = "/home"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateProfile, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.farmer = self.request.user
        return super(CreateProfile, self).form_valid(form)


class UpdateProfile(UpdateView):
    model = Profile
    form_class = ProfileForm
    success_url = "/home"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateProfile, self).dispatch(*args, **kwargs)


# Agrifield Create/Update/Delete
class CreateAgrifield(CreateView):
    model = Agrifield
    form_class = AgrifieldForm
    success_url = "/home"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateAgrifield, self).dispatch(*args, **kwargs)

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
    template_name = "agrifield_update.html"
    success_url = '/home'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateAgrifield, self).dispatch(*args, **kwargs)


class DeleteAgrifield(DeleteView):
    model = Agrifield
    form_class = AgrifieldForm
    success_url = '/home'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteAgrifield, self).dispatch(*args, **kwargs)
