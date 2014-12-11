from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
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
        if Profile.objects.filter(farmer=self.request.user).exists():
            context['profile'] = Profile.objects.get(farmer=self.request.user)
        return context


class CreateProfile(CreateView):
    model = Profile
    success_url = "/home"


class UpdateProfile(UpdateView):
    model = Profile
    form_class = ProfileForm
    success_url = "/home"
