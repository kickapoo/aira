aira.toogleIndexMapsUI = (function namespace() {
    'use strict';

    /* Handling daily and monthly raster toggle
       for external service (arta.irrigation-management.eu)
    */

    var selectTimestampView = function () {
        // Select between daily or monthly View
        var timestamp = $('#timestampSelectorBtn').attr('toggle-timestamp');
        if (timestamp === 'daily') {
            $('#meteo-' + timestamp).show();
            $('#timestampSelectorBtn').attr('raster-timestamp', 'daily');
            calendarSelector('daily');
            selectRasterMap();
            nextTimeStampConfig('monthly');
        }
        if (timestamp === 'monthly') {
            $('#meteo-' + timestamp).show();
            $('#timestampSelectorBtn').attr('raster-timestamp', 'monthly');
            calendarSelector('monthly');
            selectRasterMap();
            nextTimeStampConfig('daily');
        }
    };

    var nextTimeStampConfig = function nextTimeStampConfig(timestamp) {
        // Prepare toogle btn for the next toogle.
        // For instance, if current selection is daily
        // then next toogle is monthly.
        // Need to fix translation issue.
        $('#timestampSelectorBtn').attr('toggle-timestamp', timestamp);
        $('#timestampSelectorBtn').html('Switch ' + timestamp);
        $('#meteo-' + timestamp).hide();
    };

    var calendarSelector = function (timestamp) {
        // Config calendar based of user selection.
        // Options are: daily or monthly
        $('#calendar').datetimepicker('remove');
        switch (timestamp) {
            case 'daily':
                $('#calendar').datetimepicker('remove');
                $('#calendar').datetimepicker({
                  format: 'yyyy-mm-dd',
                  startDate: '2015-01-01',
                  initialDate: aira.yesterday,
                  endDate: aira.yesterday,
                  autoclose: true,
                  pickerPosition: 'bottom-left',
                  minView: 2,
                  startView: 2,
                  todayHighlight: false,
                  linkField: 'datetimepickerMirrorField'});
                break;
            case 'monthly':
                $('#calendar').datetimepicker({
                  format: 'yyyy-mm',
                  startDate: '2015-01',
                  autoclose: true,
                  pickerPosition: 'bottom-left',
                  minView: 3,
                  startView: 3,
                  linkField: 'datetimepickerMirrorField',
                  linkFormat: 'yyyy-mm'});
                break;
        }
    };

    var selectRasterMap = function () {
        // Config map creation
        // Service url are defined here.
        var timestamp = $('#timestampSelectorBtn').attr('raster-timestamp');
        var date = $('#datetimepickerMirrorField').val();
        var meteoVar;
        var url;
        var dateFormat;
        switch (timestamp) {
            case 'daily':
                meteoVar = $('#dailyMeteoVar').val();
                url = 'http://arta.irrigation-management.eu/mapserver/historical/';
                dateFormat = 'YYYY-MM-DD';
                if (moment(date, 'YYYY-MM', true).isValid()) {
                    date = window.keepLastDailyValue;
                }
                createRasterMap(moment(date, dateFormat).format(dateFormat), meteoVar, url, dateFormat, timestamp);
                break;
            case 'monthly':
                meteoVar = $('#monthlyMeteoVar').val();
                url = 'http://arta.irrigation-management.eu/mapserver/historical/monthly/';
                dateFormat = 'YYYY-MM';
                createRasterMap(moment(date, dateFormat).format(dateFormat), meteoVar, url, dateFormat, timestamp);
                break;
        }
    };


    var createRasterMap = function (date, meteoVar, url, dateFormat, timestamp) {
        $('#wms_map').html('');
        $('#datetimepickerMirrorField').val(date);
        $('#datepickerInputSelector').val(date);
        betweenDatesBtns(date, timestamp, dateFormat);
        var dateToRequest;
        var urlToRequest;
        var layersToRequest;
        if (timestamp === 'daily') {
            window.keepLastDailyValue = date;
            dateToRequest = moment(date, dateFormat).add(1, 'days').format(dateFormat);
            urlToRequest = url + dateToRequest + "/";
            layersToRequest = meteoVar + dateToRequest;
        }
        if (timestamp === 'monthly') {
            dateToRequest = date;
            urlToRequest = url;
            layersToRequest = meteoVar + dateToRequest;
        }
        // Keep this for debugging
        // console.log("date:" + date + ';' + 'meteoVar:' + meteoVar + ';' + 'url:' + url);

        // Map object
        var map;
        map = new OpenLayers.Map('wms_map',
                {units: 'm',
                 displayProjection: 'EPSG:4326',
                 controls: [new OpenLayers.Control.LayerSwitcher(),
                            new OpenLayers.Control.Navigation(),
                            new OpenLayers.Control.Zoom(),
                            new OpenLayers.Control.MousePosition(),
                            new OpenLayers.Control.ScaleLine()]
                 });

        //Base layer
        var openCycleMap = new OpenLayers.Layer.OSM.CycleMap(
                  "Open Cycle Map",
                  {isBaseLayer: true,
                   projection: 'EPSG:3857'});
        map.addLayer(openCycleMap);
        // Loop to add WMS layers
        var ktimatologioMap = new OpenLayers.Layer.WMS("Hellenic Cadastre",
                   "http://gis.ktimanet.gr/wms/wmsopen/wmsserver.aspx",
                     {   layers: 'KTBASEMAP', transparent: false},
                     {   isBaseLayer: true,
                         projection: new OpenLayers.Projection("EPSG:900913"),
                         iformat: 'image/png'});
        map.addLayer(ktimatologioMap);

        var meteoVarWMS = new OpenLayers.Layer.WMS(
                  meteoVar + date,
                  urlToRequest,
                  {layers: layersToRequest,
                   format: 'image/png'},
                  {isBaseLayer: false,
                   projection: 'EPSG:3857',
                   opacity: 0.65});

        map.addLayer(meteoVarWMS);

        if (timestamp === 'daily') {
            // When clicking on the map, show popup with values of variables
            OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {
              defaultHandlerOptions: {
                  'single': true,
                  'double': false,
                  'pixelTolerance': 0,
                  'stopSingle': false,
                  'stopDouble': false
              },
              initialize: function (options) {
                  this.handlerOptions = OpenLayers.Util.extend(
                      {}, this.defaultHandlerOptions
                  );
                  OpenLayers.Control.prototype.initialize.apply(
                      this, arguments
                  );
                  this.handler = new OpenLayers.Handler.Click(
                      this, {
                          'click': this.trigger
                      }, this.handlerOptions
                  );
              },
              trigger: function (e) {
                  var lonlat = map.getLonLatFromPixel(e.xy);
                  var xhr = new XMLHttpRequest();
                  // Create a small bbox such that the point is at the bottom left of the box
                  var xlow = lonlat.lon;
                  var xhigh = lonlat.lon + 50;
                  var ylow = lonlat.lat;
                  var yhigh = lonlat.lat + 50;
                  var bbox = xlow + ',' + ylow + ',' + xhigh + ',' + yhigh;

                  // Determine layers
                  var layers = '';
                  ['temperature', 'humidity', 'wind_speed', 'rain', 'evaporation',
                   'solar_radiation'].forEach(function (s) {
                      if (layers !== '') {
                          layers = layers + ',';
                      }
                      layers = layers + 'Daily_' + s + '_' + dateToRequest;
                  });

                  // Assemble URL
                  var urlPoing = url + dateToRequest + '/';
                  urlPoing = urlPoing + '?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&SRS=EPSG:3857&info_format=text/html';
                  urlPoing = urlPoing + '&BBOX=' + bbox + '&WIDTH=2&HEIGHT=2&X=0&Y=0';
                  urlPoing = urlPoing + '&LAYERS=' + layers + '&QUERY_LAYERS=' + layers;

                  xhr.open('GET', urlPoing, false);
                  xhr.send();
                  /* The test "length < 250" below is an ugly hack for not showing
                   * popups at a masked area. The masked area has the value nodata,
                   * which displays as a large negative number with very many digits.
                   */
                  if (xhr.readyState === 4  &&  xhr.responseText.length < 250) {
                      map.addPopup(new OpenLayers.Popup.FramedCloud(
                                   null, lonlat, null,
                                   xhr.responseText,
                                   null, true));
                  }
              }
          });
            var click = new OpenLayers.Control.Click();
            map.addControl(click);
            click.activate();
        }

        // Add control and center
        map.setCenter (new OpenLayers.LonLat(20.98, 39.15).transform('EPSG:4326', 'EPSG:3857'), 10);
    };

    var initTimestampView = function () {
        $('#datetimepickerMirrorField').val(aira.yesterday);
        $('#datepickerInputSelector').val(aira.yesterday);
        window.keepLastDailyValue = aira.yesterday;
        selectTimestampView();
        selectRasterMap();
    };

    var betweenDatesBtns = function (date, timestamp, dateFormat) {
        var addTimestamp;
        if (dateFormat === "YYYY-MM-DD") {
            addTimestamp = 'days';
        } else {
            addTimestamp = 'month';
        }
        $('#current').html(aira.trans_viewing + ' ' + moment(date, dateFormat).format(dateFormat));
        var plusOneDate = moment(date, dateFormat).add(1, addTimestamp);
        var minusOneDate = moment(date, dateFormat).subtract(1, addTimestamp);
        $('#next').html(plusOneDate.format(dateFormat) + "&nbsp;<i class='fa fa-chevron-right'></i>&nbsp;");
        $('#next').val(plusOneDate.format(dateFormat));
        if (plusOneDate.isAfter(aira.yesterday)) {
            $('#next').hide();
        } else {
            $('#next').show();
        }
        $('#previous').html("&nbsp;<i class='fa fa-chevron-left'></i>&nbsp;" + minusOneDate.format(dateFormat));
        $('#previous').val(minusOneDate.format(dateFormat));
        if (minusOneDate.isBefore("2015-01-01")) {
            $('#previous').hide();
        } else {
            $('#previous').show();
        }
    };

    var createNextRasterMap = function () {
        var timestamp = $('#timestampSelectorBtn').attr('raster-timestamp');
        if (timestamp === 'daily') {
            createRasterMap($('#next').val(),
                            $('#dailyMeteoVar').val(),
                            'http://arta.irrigation-management.eu/mapserver/historical/',
                            'YYYY-MM-DD',
                            'daily');
        }
        if (timestamp === 'monthly') {
            createRasterMap($('#next').val(),
                            $('#monthlyMeteoVar').val(),
                            'http://arta.irrigation-management.eu/mapserver/historical/monthly',
                            'YYYY-MM',
                            'monthly');
        }
    };

    var createPreviousRasterMap = function () {
        var timestamp = $('#timestampSelectorBtn').attr('raster-timestamp');
        if (timestamp === 'daily') {
            createRasterMap($('#previous').val(),
                            $('#dailyMeteoVar').val(),
                            'http://arta.irrigation-management.eu/mapserver/historical/',
                            'YYYY-MM-DD',
                            'daily');
        }
        if (timestamp === 'monthly') {
            createRasterMap($('#previous').val(),
                            $('#monthlyMeteoVar').val(),
                            'http://arta.irrigation-management.eu/mapserver/historical/monthly',
                            'YYYY-MM',
                            'monthly');
        }
    };

    return {
        selectRasterMap: selectRasterMap,
        selectTimestampView: selectTimestampView,
        createRasterMap: createRasterMap,
        createNextRasterMap: createNextRasterMap,
        createPreviousRasterMap: createPreviousRasterMap,
        initTimestampView: initTimestampView
    };
}());
