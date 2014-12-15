from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import (Profile, Agrifield, Crop,
                     IrrigationLog)
from .forms import (ProfileForm, AgrifieldForm,
                    CropForm, IrrigationlogForm)


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

        context['data'] = []
        if Agrifield.objects.filter(owner=self.request.user).exists():
            agrifields = Agrifield.objects.filter(owner=self.request.user).all()
            context['agrifields'] = agrifields
            for f in agrifields:
                crops = None
                if Crop.objects.filter(agrifield=f.id).exists():
                    crops = Crop.objects.filter(agrifield=f.id).all()
                    for c in crops:
                        llog = None
                        lwater = None
                        if IrrigationLog.objects.filter(agrifield_crop=c.id).exists():
                            llog = IrrigationLog.objects.filter(agrifield_crop=c.id).latest()
                            lwater = llog.water_amount
                        context['data'].append((f.id, f.name, c.id, c.crop_type, llog, lwater))
        return context


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
        agrifields = Agrifield.objects.filter(owner=self.request.user).all()
        context['agrifields'] = agrifields
        return context


class UpdateAgrifield(UpdateView):
    model = Agrifield
    form_class = AgrifieldForm
    success_url = '/home'


class AgrifieldDelete(DeleteView):
    model = Agrifield
    form_class = AgrifieldForm
    success_url = '/home'


class CreateCrop(CreateView):
    model = Crop
    form_class = CropForm
    success_url = "/home"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateCrop, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.agrifield = Agrifield.objects.get(pk=self.kwargs['pk'])
        return super(CreateCrop, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateCrop, self).get_context_data(**kwargs)
        field = Agrifield.objects.get(pk=self.kwargs['pk'])
        crops = []
        if Crop.objects.filter(agrifield=self.kwargs['pk']).exists():
            crops = Crop.objects.filter(agrifield=self.kwargs['pk']).all()
        context['crops'] = crops
        context['field'] = field
        return context


class UpdateCrop(UpdateView):
    model = Crop
    success_url = "/home"
    form_class = CropForm


class DeleteCrop(DeleteView):
    model = Crop
    success_url = "/home"


class CreateLog(CreateView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    success_url = '/home'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateLog, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.agrifield_crop = Crop.objects.get(pk=self.kwargs['pk'])
        return super(CreateLog, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateLog, self).get_context_data(**kwargs)
        crop = Crop.objects.get(pk=self.kwargs['pk'])
        logs = []
        if IrrigationLog.objects.filter(agrifield_crop=self.kwargs['pk']).exists():
            logs = IrrigationLog.objects.filter(agrifield_crop=self.kwargs['pk']).all()
        context['logs'] = logs
        context['crop'] = crop
        return context


class UpdateLog(UpdateView):
    model = IrrigationLog
    success_url = '/home'


class DeleteLog(DeleteView):
    model = IrrigationLog
    success_url = '/home'
