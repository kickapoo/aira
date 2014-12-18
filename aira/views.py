from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Profile

from .forms import ProfileForm


class IndexPageView(TemplateView):
    template_name = 'index.html'


class HomePageView(TemplateView):
    template_name = 'home.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomePageView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        # Fetch models.Profile(User)
        try:
            context['profile'] = Profile.objects.get(farmer=self.request.user)
        except Profile.DoesNotExist:
            context['profile'] = None

        # Fetch models.Agrifield(User)
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


# Agrifield Create/Update/Delete
class CreateAgrifield(CreateView):
    pass


class UpdateAgrifield(UpdateView):
    pass


class DeleteAgrifield(DeleteView):
    pass
