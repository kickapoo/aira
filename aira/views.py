import csv
import datetime as dt
import json
import os
from glob import glob

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

import pandas as pd
from hspatial import PointTimeseries

from .forms import AgrifieldForm, IrrigationlogForm, ProfileForm
from .models import Agrifield, IrrigationLog, Profile


class IrrigationPerformanceView(DetailView):
    model = Agrifield
    template_name = "aira/performance_chart/main.html"

    def get_context_data(self, **kwargs):
        self.object.can_edit(self.request.user)
        context = super().get_context_data(**kwargs)
        results = self.object.results
        if not results:
            return context
        sum_ifinal_theoretical = results["timeseries"].ifinal_theoretical.sum()
        actual_net_irrigation = results["timeseries"].actual_net_irrigation
        actual_net_irrigation = pd.to_numeric(actual_net_irrigation)
        actual_net_irrigation[actual_net_irrigation.isna()] = 0
        sum_actual_net_irrigation = actual_net_irrigation.sum()
        context["sum_actual_net_irrigation"] = sum_actual_net_irrigation
        context["percentage_diff"] = _("Not Available")
        if sum_ifinal_theoretical >= 0.1:
            context["percentage_diff"] = round(
                (sum_actual_net_irrigation - sum_ifinal_theoretical)
                / sum_ifinal_theoretical
                * 100
            )
        return context


def performance_csv(request, pk):
    f = Agrifield.objects.get(pk=pk)
    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="{}-performance.csv"'.format(f.id)
    f.can_edit(request.user)
    writer = csv.writer(response)
    writer.writerow(
        [
            "Date",
            "Estimated Irrigation Water Amount",
            "Applied Irrigation Water Amount",
            "Effective precipitation",
        ]
    )
    writer.writerow(["", "amount (mm)", "amount (mm)", "amount (mm)"])
    for date, row in f.results["timeseries"].iterrows():
        writer.writerow(
            [
                date,
                row.ifinal_theoretical,
                row.actual_net_irrigation if row.actual_net_irrigation else 0,
                row.effective_precipitation,
            ]
        )
    return response


class DemoView(TemplateView):
    def get(self, request):
        user = authenticate(username="demo", password="demo")
        login(request, user)
        return redirect("home", user)


class ConversionToolsView(TemplateView):
    template_name = "aira/tools/main.html"


class FrontPageView(TemplateView):
    template_name = "aira/frontpage/main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filenames = sorted(
            glob(os.path.join(settings.AIRA_DATA_HISTORICAL, "daily_rain-*.tif"))
        )
        one_day = dt.timedelta(days=1)
        context["start_date"] = self._get_date_from_filename(filenames[0])
        context["end_date"] = self._get_date_from_filename(filenames[-1]) - one_day
        return context

    def _get_date_from_filename(self, filename):
        datestr = os.path.basename(filename).split(".")[0].partition("-")[2]
        y, m, d = (int(x) for x in datestr.split("-"))
        return dt.date(y, m, d)


class AgrifieldListView(TemplateView):
    template_name = "aira/home/main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Load data paths
        url_username = kwargs.get("username")
        context["url_username"] = kwargs.get("username")
        if kwargs.get("username") is None:
            url_username = self.request.user
            context["url_username"] = self.request.user
        # User is url_slug <username>
        user = User.objects.get(username=url_username)

        # Fetch models.Profile(User)
        try:
            context["profile"] = Profile.objects.get(farmer=self.request.user)
        except Profile.DoesNotExist:
            context["profile"] = None
        # Fetch models.Agrifield(User)
        try:
            agrifields = Agrifield.objects.filter(owner=user).all()
            for f in agrifields:
                # Check if user is allowed or 404
                f.can_edit(self.request.user)
            # For Profile section
            # Select self.request.user user that set him supervisor
            if Profile.objects.filter(supervisor=self.request.user).exists():
                supervising_users = Profile.objects.filter(supervisor=self.request.user)
                context["supervising_users"] = supervising_users

            context["agrifields"] = agrifields
            context["fields_count"] = len(agrifields)
        except Agrifield.DoesNotExist:
            context["agrifields"] = None
        return context


class RecommendationView(DetailView):
    model = Agrifield
    template_name = "aira/recommendation/main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object.can_edit(self.request.user)
        return context


# Profile Create/Update
class CreateProfileView(CreateView):
    model = Profile
    form_class = ProfileForm
    success_url = "/home"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user in form.fields["supervisor"].queryset:
            form.fields["supervisor"].queryset = form.fields[
                "supervisor"
            ].queryset.exclude(pk=self.request.user.id)
        return form

    def form_valid(self, form):
        form.instance.farmer = self.request.user
        return super().form_valid(form)


class UpdateProfileView(UpdateView):
    model = Profile
    form_class = ProfileForm
    success_url = "/home"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user in form.fields["supervisor"].queryset:
            form.fields["supervisor"].queryset = form.fields[
                "supervisor"
            ].queryset.exclude(pk=self.request.user.id)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(pk=self.kwargs["pk"])
        if not self.request.user == profile.farmer:
            raise Http404
        return context


class DeleteProfileView(DeleteView):
    model = Profile

    def get_success_url(self):
        profile = Profile.objects.get(pk=self.kwargs["pk"])
        user = User.objects.get(pk=profile.farmer.id)
        # Delete all user data using bult in cascade delete
        user.delete()
        return reverse("welcome")


class CreateAgrifieldView(CreateView):
    model = Agrifield
    form_class = AgrifieldForm
    template_name = "aira/agrifield_edit/main.html"

    def form_valid(self, form):
        user = User.objects.get(username=self.kwargs["username"])
        form.instance.owner = user
        return super().form_valid(form)

    def get_success_url(self):
        url_username = self.kwargs["username"]
        return reverse("home", kwargs={"username": url_username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            url_username = self.kwargs["username"]
            user = User.objects.get(username=url_username)
            context["agrifields"] = Agrifield.objects.filter(owner=user).all()
            context["agrifield_owner"] = user

        except Agrifield.DoesNotExist:
            context["agrifields"] = None
        return context


class UpdateAgrifieldView(UpdateView):
    model = Agrifield
    form_class = AgrifieldForm
    template_name = "aira/agrifield_edit/main.html"

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs["pk"])
        return reverse("home", kwargs={"username": field.owner})

    def get_context_data(self, **kwargs):
        self.object.can_edit(self.request.user)
        context = super().get_context_data(**kwargs)
        context["agrifield_owner"] = self.object.owner
        return context


class DeleteAgrifieldView(DeleteView):
    model = Agrifield
    form_class = AgrifieldForm
    template_name = "aira/agrifield_delete/confirm.html"

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs["pk"])
        return reverse("home", kwargs={"username": field.owner})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        afieldobj = Agrifield.objects.get(pk=self.kwargs["pk"])
        afieldobj.can_edit(self.request.user)
        return context


class CreateIrrigationLogView(CreateView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    success_url = "/home"
    template_name_suffix = "/create"

    def get_success_url(self):
        field = Agrifield.objects.get(pk=self.kwargs["pk"])
        return reverse("home", kwargs={"username": field.owner})

    def form_valid(self, form):
        form.instance.agrifield = Agrifield.objects.get(pk=self.kwargs["pk"])
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        self.agrifield = get_object_or_404(Agrifield, pk=self.kwargs["pk"])
        self.agrifield.can_edit(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["agrifield"] = self.agrifield
        return context


class UpdateIrrigationLogView(UpdateView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    template_name_suffix = "/update"

    def get_success_url(self):
        return reverse("home", kwargs={"username": self.object.agrifield.owner})

    def get_object(self):
        irrigation_log = super().get_object()
        irrigation_log.agrifield.can_edit(self.request.user)
        return irrigation_log


class DeleteIrrigationLogView(DeleteView):
    model = IrrigationLog
    form_class = IrrigationlogForm
    template_name_suffix = "/confirm_delete"

    def get_object(self):
        irrigation_log = super().get_object()
        irrigation_log.agrifield.can_edit(self.request.user)
        return irrigation_log

    def get_success_url(self):
        return reverse("home", kwargs={"username": self.object.agrifield.owner})


def remove_supervised_user_from_user_list(request):
    # Called in templates:aira:home
    if request.is_ajax() and request.POST:
        supervised_profile = Profile.objects.get(
            pk=int(request.POST.get("supervised_id"))
        )
        supervised_profile.supervisor = None
        supervised_profile.save()
        response_data = {"message": "Success!!!"}
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    raise Http404


class AgrifieldTimeseriesView(View):
    def get(self, *args, **kwargs):
        filename = self._get_point_timeseries(*args, **kwargs)
        return FileResponse(
            open(filename, "rb"), as_attachment=True, content_type="text_csv"
        )

    def _get_point_timeseries(self, *args, **kwargs):
        agrifield = get_object_or_404(Agrifield, pk=kwargs.get("agrifield_id"))
        variable = kwargs.get("variable")
        prefix = os.path.join(settings.AIRA_DATA_HISTORICAL, "daily_" + variable)
        dest = os.path.join(
            settings.AIRA_TIMESERIES_CACHE_DIR,
            "agrifield{}-{}.hts".format(agrifield.id, variable),
        )
        PointTimeseries(point=agrifield.location, prefix=prefix).get_cached(
            dest, version=2
        )
        return dest


class DownloadSoilAnalysisView(View):
    def get(self, *args, **kwargs):
        agrifield = get_object_or_404(Agrifield, pk=kwargs.get("agrifield_id"))
        agrifield.can_edit(self.request.user)
        if not agrifield.soil_analysis:
            raise Http404
        return FileResponse(agrifield.soil_analysis, as_attachment=True)
