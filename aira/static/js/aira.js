aira.agrifieldEditDocumentReady = () => {
  document.getElementById('id_use_custom_parameters').onclick = () => {
    const customPar = document.getElementById('custom_par');
    customPar.style.display = (
      customPar.style.display === 'none' ? 'block' : 'none'
    );
  };

  /* The following should be set directly in the HTML, with the "step"
     * attribute. However, we are generating this through django-bootstrap3's
     * {% bootstrap_field %}; it isn't clear if and how this can be configured.
     */
  document.getElementById('id_custom_efficiency').step = 0.05;
  document.getElementById('id_custom_irrigation_optimizer').step = 0.01;
  document.getElementById('id_custom_root_depth_max').step = 0.1;
  document.getElementById('id_custom_root_depth_min').step = 0.1;
  document.getElementById('id_custom_max_allowed_depletion').step = 0.01;
  document.getElementById('id_custom_field_capacity').step = 0.01;
  document.getElementById('id_custom_wilting_point').step = 0.01;
  document.getElementById('id_custom_thetaS').step = 0.01;
};

aira.setupDateTimePickerForAppliedIrrigation = () => {
  $('#id_timestamp').datetimepicker({
    format: 'yyyy-mm-dd hh:ii',
    autoclose: true,
    todayBtn: true,
    pickerPosition: 'bottom-left',
  });
};

aira.map = {
  create() {
    this.olmap = new OpenLayers.Map('map',
      {
        units: 'm',
        displayProjection: 'EPSG:4326',
        controls: [new OpenLayers.Control.LayerSwitcher(),
          new OpenLayers.Control.Navigation(),
          new OpenLayers.Control.Zoom(),
          new OpenLayers.Control.MousePosition(),
          new OpenLayers.Control.ScaleLine()],
      });
    this.addBaseLayers();
    this.olmap.setCenter(
      new OpenLayers.LonLat(...aira.mapDefaultCenter).transform('EPSG:4326', 'EPSG:3857'),
      aira.mapDefaultZoom,
    );
  },

  addBaseLayers() {
    this.addOpenCycleMapBaseLayer();
    this.addHellenicCadastreBaseLayer();
    this.addGoogleSatelliteBaseLayer();
  },

  addOpenCycleMapBaseLayer() {
    const openCycleMap = new OpenLayers.Layer.OSM(
      'Open Cycle Map',
      [`https://a.tile.thunderforest.com/cycle/\${z}/\${x}/\${y}.png?${aira.thunderforestApiKeyQueryElement}`,
        `https://b.tile.thunderforest.com/cycle/\${z}/\${x}/\${y}.png?${aira.thunderforestApiKeyQueryElement}`,
        `https://c.tile.thunderforest.com/cycle/\${z}/\${x}/\${y}.png?${aira.thunderforestApiKeyQueryElement}`],
      {
        isBaseLayer: true,
        projection: 'EPSG:3857',
      },
    );
    this.olmap.addLayer(openCycleMap);
  },

  addHellenicCadastreBaseLayer() {
    const ktimatologioMap = new OpenLayers.Layer.WMS('Hellenic Cadastre',
      '//gis.ktimanet.gr/wms/wmsopen/wmsserver.aspx',
      { layers: 'KTBASEMAP', transparent: false },
      {
        isBaseLayer: true,
        projection: new OpenLayers.Projection('EPSG:900913'),
        iformat: 'image/png',
      });
    this.olmap.addLayer(ktimatologioMap);
  },

  addGoogleSatelliteBaseLayer() {
    const googleMaps = new OpenLayers.Layer.Google(
      'Google Satellite', { type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22 },
    );
    this.olmap.addLayer(googleMaps);
  },

  addCoveredAreaLayer(map, kmlUrl) {
    const kml = new OpenLayers.Layer.Vector('Covered area',
      {
        strategies: [new OpenLayers.Strategy.Fixed()],
        visibility: true,
        protocol: new OpenLayers.Protocol.HTTP(
          {
            url: kmlUrl,
            format: new OpenLayers.Format.KML(),
          },
        ),
      });
    this.olmap.addLayer(kml);
  },
};

aira.agrifieldsMap = Object.create(aira.map);
Object.assign(aira.agrifieldsMap, {
  addAgrifields(agrifields, layerName) {
    this.agrifields = agrifields;
    this.layerName = layerName;
    this.addAgrifieldsLayer();
    this.centerMapIfOnlyOneField();
    this.addPopup();
    return this.agrifieldsLayer;
  },

  addAgrifieldsLayer() {
    this.agrifieldsLayer = new OpenLayers.Layer.Vector(this.layerName);
    this.agrifields.forEach((item) => {
      const geometry = new OpenLayers.Geometry.Point(...item.coords)
        .transform('EPSG:4326', 'EPSG:3857');
      const attributes = {
        description: `<a href="${item.url}">${item.name}</a>`,
      };
      const style = {
        externalGraphic: 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.12/img/marker.png',
        graphicHeight: 25,
        graphicWidth: 21,
        graphicXOffset: -12,
        graphicYOffset: -25,
      };
      const feature = new OpenLayers.Feature.Vector(geometry, attributes, style);
      this.agrifieldsLayer.addFeatures(feature);
    });
    this.olmap.addLayer(this.agrifieldsLayer);
  },

  centerMapIfOnlyOneField() {
    if (this.agrifields.length === 1) {
      this.olmap.setCenter(
        new OpenLayers.LonLat(...this.agrifields[0].coords)
          .transform('EPSG:4326', 'EPSG:3857'),
        18,
      );
    }
  },

  addPopup() {
    this.agrifieldSelector = new OpenLayers.Control.SelectFeature(
      this.agrifieldsLayer, { onSelect: this.createPopup, onUnselect: this.destroyPopup },
    );
    this.olmap.addControl(this.agrifieldSelector);
    this.agrifieldSelector.activate();
  },

  createPopup(feature) {
    this.popup = new OpenLayers.Popup.FramedCloud('pop',
      feature.geometry.getBounds().getCenterLonLat(),
      null,
      `<div class="markerContent">${feature.attributes.description}</div>`,
      null,
      true,
      (() => { aira.agrifieldsMap.agrifieldSelector.unselectAll(); }));
    aira.agrifieldsMap.olmap.addPopup(this.popup);
  },

  destroyPopup(feature) { // eslint-disable-line no-unused-vars
    this.popup.destroy();
    this.popup = null;
  },
});

aira.agrifieldEditMap = Object.create(aira.agrifieldsMap);
Object.assign(aira.agrifieldEditMap, {
  registerClickEvent(layer) {
    this.olmap.events.register('click', this.olmap, (e) => {
      const coords = this.olmap.getLonLatFromPixel(e.xy);
      const geometry = new OpenLayers.Geometry.Point(coords.lon, coords.lat);
      const attributes = { description: '' };
      const style = {
        externalGraphic: 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.12/img/marker.png',
        graphicHeight: 25,
        graphicWidth: 21,
        graphicXOffset: -12,
        graphicYOffset: -25,
      };
      const feature = new OpenLayers.Feature.Vector(geometry, attributes, style);
      layer.removeAllFeatures();
      layer.addFeatures(feature);
      const lonlat = coords.transform('EPSG:3857', 'EPSG:4326');
      document.getElementById('id_location_1').value = lonlat.lat.toFixed(5);
      document.getElementById('id_location_0').value = lonlat.lon.toFixed(5);
    });
  },
});

aira.meteoMapPanel = {
  get timestepToggle() { return document.getElementById('timestep-toggle'); },
  get dateSelector() { return document.getElementById('date-input'); },
  get activeTimestep() { return this.timestepToggle.getAttribute('current-timestep'); },
  get otherTimestep() { return this.activeTimestep === 'daily' ? 'monthly' : 'daily'; },
  get dateFormat() { return this.activeTimestep === 'daily' ? 'YYYY-MM-DD' : 'YYYY-MM'; },
  get activeDate() { return this.dateSelector.value; },
  get mapserverSubdir() { return this.activeTimestep === 'daily' ? 'historical/' : 'historical/monthly'; },
  get mapserverUrl() {
    let result = aira.mapserverBaseUrl + this.mapserverSubdir;
    if (this.activeTimestep === 'daily') result += `${this.activeDate}/`;
    return result;
  },
  get meteoVarElement() { return document.getElementById(this.activeTimestep === 'daily' ? 'dailyMeteoVar' : 'monthlyMeteoVar'); },
  get layersToRequest() { return this.meteoVarElement.value + this.activeDate; },
  get activeDateIndicator() { return document.getElementById('current-date'); },

  capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  },

  toggleBetweenMonthlyAndDaily() {
    this.timestepToggle.setAttribute('current-timestep', this.otherTimestep);
    this.setTimestep();
  },

  setTimestep() {
    document.getElementById(`raster-selector-${this.activeTimestep}`).style.display = 'block';
    document.getElementById(`raster-selector-${this.otherTimestep}`).style.display = 'none';
    this.timestepToggle.textContent = aira.timestepMessages[`switchTo${this.capitalize(this.otherTimestep)}`];
    this.setDateSelectorInitialValue();
    this.setupDateTimePicker();
    this.setupDateChangingButtons(aira.end_date);
    this.setMapDate(aira.end_date);
  },

  setDateSelectorInitialValue() {
    this.dateSelector.value = this.activeTimestep === 'daily'
      ? aira.end_date : aira.end_date.slice(0, 7);
  },

  setupDateTimePicker() {
    $('#date-input').datetimepicker('remove');
    $('#date-input').datetimepicker({
      startDate: aira.start_date,
      initialDate: aira.end_date,
      endDate: aira.end_date,
      autoclose: true,
      pickerPosition: 'bottom-left',
      format: this.dateFormat.toLowerCase(),
      minView: this.activeTimestep === 'daily' ? 'month' : 'year',
      startView: this.activeTimestep === 'daily' ? 'month' : 'year',
    });
  },

  removeAllOverlayLayers() {
    aira.map.olmap.layers.filter((layer) => !layer.isBaseLayer)
      .forEach((layer) => aira.map.olmap.removeLayer(layer));
  },

  updateMeteoLayer() {
    document.getElementById('map').innerHtml = '';
    this.removeAllOverlayLayers();
    const meteoLayer = new OpenLayers.Layer.WMS(
      this.meteoVarElement.value + this.activeDate,
      this.mapserverUrl,
      { layers: this.layersToRequest, format: 'image/png' },
      { isBaseLayer: false, projection: 'EPSG:3857', opacity: 0.65 },
    );
    aira.map.olmap.addLayer(meteoLayer);

    this.setupPopup();

    const click = new OpenLayers.Control.Click();
    aira.map.olmap.addControl(click);
    click.activate();

    aira.map.olmap.setCenter(
      new OpenLayers.LonLat(...aira.mapDefaultCenter).transform('EPSG:4326', 'EPSG:3857'),
      aira.mapDefaultZoom,
    );
  },

  setupPopup() {
    OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {
      defaultHandlerOptions: {
        single: true,
        double: false,
        pixelTolerance: 0,
        stopSingle: false,
        stopDouble: false,
      },
      initialize: function initialize(options) {
        this.handlerOptions = OpenLayers.Util.extend(
          {}, this.defaultHandlerOptions,
        );
        OpenLayers.Control.prototype.initialize.apply(this, options);
        this.handler = new OpenLayers.Handler.Click(
          this, { click: this.trigger }, this.handlerOptions,
        );
      },
      trigger: this.showPopup,
    });
  },

  showPopup(e) {
    const lonlat = aira.map.olmap.getLonLatFromPixel(e.xy);
    const xhr = new XMLHttpRequest();
    xhr.onload = () => {
      /* The test "length < 250" below is an ugly hack for not showing
          * popups at a masked area. The masked area has the value nodata,
          * which displays as a large negative number with very many digits.
          */
      if (xhr.readyState === 4 && xhr.responseText.length < 250) {
        aira.map.olmap.addPopup(new OpenLayers.Popup.FramedCloud(
          null, lonlat, null,
          xhr.responseText,
          null, true,
        ));
      }
    };

    // Create a small bbox such that the point is at the bottom left of the box
    const xlow = lonlat.lon;
    const xhigh = lonlat.lon + 50;
    const ylow = lonlat.lat;
    const yhigh = lonlat.lat + 50;
    const bbox = `${xlow},${ylow},${xhigh},${yhigh}`;

    // Determine layers
    const vars = aira.meteoMapPanel.activeTimestep === 'daily'
      ? ['temperature', 'humidity', 'wind_speed', 'rain', 'evaporation', 'solar_radiation']
      : ['evaporation'];
    const prefix = aira.meteoMapPanel.activeTimestep === 'daily' ? 'Daily_' : 'Monthly_';
    const layers = vars.map((x) => `${prefix}${x}_${aira.meteoMapPanel.activeDate}`).join();

    // Assemble URL
    const params = new URLSearchParams({
      SERVICE: 'WMS',
      VERSION: '1.1.1',
      REQUEST: 'GetFeatureInfo',
      SRS: 'EPSG:3857',
      info_format: 'text/html',
      BBOX: bbox,
      WIDTH: 2,
      HEIGHT: 2,
      X: 0,
      Y: 0,
      LAYERS: layers,
      QUERY_LAYERS: layers,
    });

    // Make request
    xhr.open('GET', `${aira.meteoMapPanel.mapserverUrl}?${params.toString()}`, false);
    xhr.send();
  },

  initialize() {
    aira.map.create();
    this.dateSelector.value = aira.end_date;
    this.setTimestep();
  },

  setupDateChangingButtons(date) {
    this.activeDateIndicator.textContent = moment(date, this.dateFormat).format(this.dateFormat);
    this.setupPrevDateElement(date);
    this.setupNextDateElement(date);
  },

  setupPrevDateElement(date) {
    const timeUnit = this.activeTimestep === 'daily' ? 'days' : 'months';

    const prevDate = moment(date, this.dateFormat).subtract(1, timeUnit);
    const prevDateElement = document.getElementById('previous-date');
    prevDateElement.innerHTML = (
      `&nbsp;<i class='fa fa-chevron-left'></i>&nbsp;${prevDate.format(this.dateFormat)}`
    );
    prevDateElement.style.display = prevDate.isBefore(aira.start_date) ? 'none' : 'block';
    prevDateElement.setAttribute('date', prevDate.format(this.dateFormat));
  },

  setupNextDateElement(date) {
    const timeUnit = this.activeTimestep === 'daily' ? 'days' : 'months';

    const nextDate = moment(date, this.dateFormat).add(1, timeUnit);
    const nextDateElement = document.getElementById('next-date');
    nextDateElement.innerHTML = (
      `${nextDate.format(this.dateFormat)}&nbsp;<i class='fa fa-chevron-right'></i>&nbsp;`
    );
    nextDateElement.style.display = nextDate.isAfter(aira.end_date) ? 'none' : 'block';
    nextDateElement.setAttribute('date', nextDate.format(this.dateFormat));
  },

  setMapDate(targetDate) {
    this.setupDateChangingButtons(targetDate);
    this.updateMeteoLayer();
  },
};

aira.showAndHideIrrigationFieldsAccordingToType = () => {
  function getFormGroupElement(inputElement) {
    // Handles the case when an input is nested in another div inside the form group
    if (inputElement.parentElement.className.includes('form-group')) {
      return inputElement.parentElement;
    }
    return inputElement.parentElement.parentElement;
  }
  function hideFields(fields) {
    fields.forEach((field) => {
      const input = document.querySelector(`#id_${field}`);
      getFormGroupElement(input).style.display = 'none';
      input.removeAttribute('required');
    });
  }
  function showFields(fields) {
    fields.forEach((field) => {
      const input = document.querySelector(`#id_${field}`);
      getFormGroupElement(input).style.display = '';
      input.setAttribute('required', '');
    });
  }
  function onIrrigationTypeChanged() {
    const selectedType = document.querySelector('input[name="irrigation_type"]:checked').value;
    const fieldsPerType = {
      VOLUME_OF_WATER: ['supplied_water_volume'],
      DURATION_OF_IRRIGATION: ['supplied_duration', 'supplied_flow_rate'],
      FLOWMETER_READINGS: [
        'flowmeter_reading_start',
        'flowmeter_reading_end',
        'flowmeter_water_percentage',
      ],
    };
    Object.keys(fieldsPerType).forEach((type) => {
      if (type === selectedType) {
        showFields(fieldsPerType[type]);
      } else {
        hideFields(fieldsPerType[type]);
      }
    });
  }

  Array.from(document.querySelectorAll('input[name="irrigation_type"]'))
    .forEach((input) => input.addEventListener('change', onIrrigationTypeChanged));
  onIrrigationTypeChanged(); // Called once at the start to display according to default choice
};
