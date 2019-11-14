import datetime as dt
import os

from django.conf import settings
from django.core.cache import cache

import pandas as pd
from hspatial import PointTimeseries, extract_point_from_raster
from osgeo import gdal
from swb import calculate_crop_evapotranspiration, calculate_soil_water


class AgrifieldSWBMixin:
    """Functionality about running the SWB model for an Agrifield.

    This class is to be mixed in models.Agrifield; it contains the part of the
    functionality that has to do with running the swb model on the Agrifield.
    """

    @property
    def root_depth(self):
        return (float(self.root_depth_min) + float(self.root_depth_max)) / 2

    @property
    def draintime(self):
        raster_a = os.path.join(settings.AIRA_DATA_SOIL, "a_1d.tif")
        a = extract_point_from_raster(self.location, gdal.Open(raster_a))
        raster_b = os.path.join(settings.AIRA_DATA_SOIL, "b.tif")
        b = extract_point_from_raster(self.location, gdal.Open(raster_b))
        return round(a * self.root_depth ** b)

    def _point_timeseries(self, category, varname):
        return PointTimeseries(
            self.location,
            prefix=os.path.join(
                getattr(settings, "AIRA_DATA_" + category), "daily_" + varname
            ),
            start_date=self.start_of_season,
        ).get()

    @property
    def start_of_season(self):
        return dt.datetime(dt.date.today().year, 3, 15, 0, 0)

    def _get_timeseries_from_rasters(self, var):
        historical = self._point_timeseries("HISTORICAL", var)
        forecast = self._point_timeseries("FORECAST", var)
        self.historical_end_date = historical.data.index[-1]
        forecast_start_date = self.historical_end_date + dt.timedelta(minutes=1)
        forecast.data = forecast.data[forecast_start_date:]
        self.forecast_start_date = forecast.data.index[0]
        return pd.concat((historical.data["value"], forecast.data["value"]))

    def _determine_effective_precipitation(self):
        EFFECTIVE_PRECIPITATION_FACTOR = 0.8
        self.timeseries["effective_precipitation"] = (
            self._get_timeseries_from_rasters("rain") * EFFECTIVE_PRECIPITATION_FACTOR
        )

    def _determine_evaporation(self):
        self.timeseries["ref_evapotranspiration"] = self._get_timeseries_from_rasters(
            "evaporation"
        )

    def _determine_actual_net_irrigation(self):
        self.timeseries["actual_net_irrigation"] = 0  # Zero is the default
        start = self.timeseries.index[0]
        end = self.timeseries.index[-1]
        for irrigation_log in self.irrigationlog_set.filter(time__range=(start, end)):
            date = irrigation_log.time.date()
            applied_water = irrigation_log.applied_water
            if applied_water is None:
                # When an irrigation event has been logged but we don't know how
                # much, we assume we reached field capacity. At that point we use
                # "True" instead of a number, which signals to
                # swb.calculate_soil_water() to assume we irrigated with the recommended
                # amount.
                self.timeseries.at[date, "actual_net_irrigation"] = True
            else:
                applied_water_mm = float(applied_water / self.area * 1000)
                self.timeseries.at[date, "actual_net_irrigation"] = applied_water_mm

    def _determine_crop_evapotranspiration(self):
        calculate_crop_evapotranspiration(
            timeseries=self.timeseries,
            planting_date=self.crop_type.most_recent_planting_date,
            kc_unplanted=self.crop_type.kc_init,
            kc_ini=self.crop_type.kc_init,
            kc_mid=self.crop_type.kc_mid,
            kc_end=self.crop_type.kc_end,
            init=self.crop_type.days_kc_init,
            dev=self.crop_type.days_kc_dev,
            mid=self.crop_type.days_kc_mid,
            late=self.crop_type.days_kc_late,
        )

    def prepare_timeseries(self):
        """Setup self.timeseries, a DataFrame with the data needed to run the model.
        """
        self.timeseries = pd.DataFrame()
        self._determine_effective_precipitation()
        self._determine_evaporation()
        self.timeseries.dropna()
        self._determine_crop_evapotranspiration()
        self._determine_actual_net_irrigation()

    def run_swb_model(self):
        return calculate_soil_water(
            timeseries=self.timeseries,
            theta_s=float(self.theta_s),
            theta_fc=self.field_capacity,
            theta_wp=self.wilting_point,
            zr=self.root_depth,
            zr_factor=1000,
            p=float(self.p),
            draintime=self.draintime,
            theta_init=self.field_capacity,
            mif=self.irrigation_optimizer,
        )

    def run_swb_model_normally(self):
        d = self.run_swb_model()
        self.raw = d["raw"]
        self.taw = d["taw"]
        self.timeseries["recommendation"] = self.timeseries["dr"] > self.raw
        self.timeseries["ifinal"] = (
            self.timeseries["recommended_net_irrigation"] / self.irrigation_efficiency
        )
        self.timeseries["ifinal_m3"] = self.timeseries["ifinal"] / 1000 * self.area

    def _extract_columns_from_timeseries(self, *cols):
        result = {}
        for col in cols:
            result[col] = self.timeseries[col].copy()
        return result

    def _import_columns_to_timeseries(self, saved_columns):
        for col, value in saved_columns.items():
            self.timeseries[col] = value

    def _rename_result_columns_in_timeseries(self, suffix):
        self.timeseries.rename(
            columns={
                "dr": "dr" + suffix,
                "theta": "theta" + suffix,
                "ks": "ks" + suffix,
                "recommended_net_irrigation": "recommended_net_irrigation" + suffix,
            },
            inplace=True,
        )

    def run_swb_model_for_performance_chart(self):
        saved_columns = self._extract_columns_from_timeseries(
            "actual_net_irrigation", "dr", "theta", "ks", "recommended_net_irrigation"
        )

        # We want the model to run ignoring the actual net irrigation, and instead
        # assume that the actual irrigation equals recommended irrigation.
        self.timeseries["actual_net_irrigation"] = True

        self.run_swb_model()
        self._rename_result_columns_in_timeseries(suffix="_theoretical")
        self._import_columns_to_timeseries(saved_columns)
        self.timeseries["ifinal_theoretical"] = self.timeseries.apply(
            lambda x: (
                x.recommended_net_irrigation_theoretical / self.irrigation_efficiency
            ),
            axis=1,
        )

    def execute_model(self):
        if not self.in_covered_area:
            return
        self.prepare_timeseries()
        self.run_swb_model_normally()
        self.run_swb_model_for_performance_chart()
        result = {
            "raw": self.raw,
            "taw": self.taw,
            "timeseries": self.timeseries,
            "historical_end_date": self.historical_end_date,
            "forecast_start_date": self.forecast_start_date,
        }
        cache.set("model_run_{}".format(self.id), result, None)
        return result


class AgrifieldSWBResultsMixin:
    """Mostly properties related to accessing SWB model run results.

    This class is to be mixed in models.Agrifield; it contains mostly properties
    accessing the results of the SWB model run. They are mostly useful in templates.
    """

    @property
    def results(self):
        if self.in_covered_area:
            return cache.get("model_run_{}".format(self.id))
        else:
            return None

    @property
    def needs_irrigation(self):
        return self.results["timeseries"]["ifinal"].sum() > 0

    @property
    def alternative_irrigations(self):
        forecast_start_date = self.results["forecast_start_date"]
        timeseries = self.results["timeseries"]
        return timeseries.loc[timeseries["ifinal"] > 0][forecast_start_date:]

    @property
    def forecast_data(self):
        forecast_start_date = self.results["forecast_start_date"]
        timeseries = self.results["timeseries"]
        return timeseries[forecast_start_date:]
