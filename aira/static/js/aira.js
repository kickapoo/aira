$(document).ready(function(){
    // Enable tooltip when page is fully loaded
    $('[data-toggle="tooltip"]').tooltip();

    $('#daily-datepicker').datepicker({
        format: "dd/mm/yyyy",
        startDate: "01/01/2015",
        todayBtn: true,
    });

    $("#monthly-datepicker").datepicker( {
        format: "mm/yyyy",
        viewMode: "months",
        minViewMode: "months"
    });

    $('.clockpicker').clockpicker({
                    donetext: 'Done'
    });



    // From: https://godjango.com/18-basic-ajax/
    // CSRF code
    function getCookie(name) {
        var cookieValue = null;
        var i = 0;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (i; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});


aira.Map = (function namespace() {
    'use strict';

    function createMap(){
        $('#wms_map').html('');

        var meteoVar = get_meteo(get_timestamp())
        var timestamp = get_timestamp()
        var date = get_date(get_timestamp())

        if (timestamp === 'daily') {
            var dateFormat = 'YYYY-MM-DD';
            var dateToRequest = moment(date, 'DD/MM/YYYY').add(1, 'days').format(dateFormat);
            var urlToRequest = 'http://arta.irrigation-management.eu/mapserver/historical/' + dateToRequest + "/";
            var layersToRequest = meteoVar + dateToRequest;
            var url = 'http://arta.irrigation-management.eu/mapserver/historical/';
        }
        if (timestamp === 'monthly') {
            var dateToRequest = moment("01/"+date, 'DD/MM/YYYY').format('YYYY-MM');
            var urlToRequest = 'http://arta.irrigation-management.eu/mapserver/historical/monthly/';
            var layersToRequest = meteoVar + dateToRequest;
            var url = 'http://arta.irrigation-management.eu/mapserver/historical/monthly/';
        }
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

        // Base layer
        var openCycleMap = new OpenLayers.Layer.OSM.CycleMap(
                  "Open Cycle Map",
                  {isBaseLayer: true,
                   projection: 'EPSG:3857'});
        map.addLayer(openCycleMap);
        //Loop to add WMS layers
        var ktimatologioMap = new OpenLayers.Layer.WMS("Hellenic Cadastre",
                   "http://gis.ktimanet.gr/wms/wmsopen/wmsserver.aspx",
                     {   layers: 'KTBASEMAP', transparent: false},
                     {   isBaseLayer: true,
                         projection: new OpenLayers.Projection("EPSG:900913"),
                         iformat: 'image/png'});
        map.addLayer(ktimatologioMap);

        var meteoVarWMS = new OpenLayers.Layer.WMS(
                  meteoVar + dateToRequest,
                  urlToRequest,
                  {layers: layersToRequest,
                   format: 'image/png'},
                  {isBaseLayer: false,
                   projection: 'EPSG:3857',
                   opacity: 0.65});

        map.addLayer(meteoVarWMS);

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
                  if (timestamp === 'daily')  {
                      var layers = '';
                      ['temperature', 'humidity', 'wind_speed', 'rain', 'evaporation',
                       'solar_radiation'].forEach(function (s) {
                        if (layers !== '') {
                            layers = layers + ',';
                        }
                        layers = layers + 'Daily_' + s + '_' + dateToRequest;
                    });
                      urlPoint = url + dateToRequest + '/';
                  }
                  if (timestamp === 'monthly')  {
                      var layers = '';
                      // forEach is used because in near future more monthly
                      // meteorogical variables will be added.
                      ['evaporation'].forEach(function (s) {
                        if (layers !== '') {
                            layers = layers + ',';
                        }
                        layers = layers + 'Monthly_' + s + '_' + dateToRequest;
                    });
                      var urlPoint = url;
                  }
                  // Assemble URL
                  urlPoint = urlPoint + '?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&SRS=EPSG:3857&info_format=text/html';
                  urlPoint = urlPoint + '&BBOX=' + bbox + '&WIDTH=2&HEIGHT=2&X=0&Y=0';
                  urlPoint = urlPoint + '&LAYERS=' + layers + '&QUERY_LAYERS=' + layers;

                  xhr.open('GET', urlPoint, false);
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
        // Add control and center
        map.setCenter (new OpenLayers.LonLat(20.98, 39.15).transform('EPSG:4326', 'EPSG:3857'), 10);

    }

    function get_timestamp(){
        if ($('#timestamp').prop('checked')) {
            $('#meteo-monthly').hide();
            $('#meteo-daily').show();
            $('#monthly-datepicker').hide();
            $('#daily-datepicker').show();
            return "daily"
        } else {
            $('#meteo-monthly').show();
            $('#meteo-daily').hide();
            $('#daily-datepicker').hide();
            $('#monthly-datepicker').show();
            return "monthly"
        }
    }

    function get_meteo(timestamp){
        if (timestamp == 'daily'){
            return $('#meteo-daily').find(":selected").val()
        }
        if (timestamp == 'monthly'){
            return $('#meteo-monthly').find(":selected").val()
        }
    }

    function get_date(timestamp){
        if (timestamp == 'daily'){
            $('#current').html(moment( $('#daily-datepicker').datepicker('getDate')).format('DD/MM/YYYY'))
            return moment($('#daily-datepicker').datepicker('getDate')).format('DD/MM/YYYY')
        }
        if (timestamp == 'monthly'){
            $('#current').html(moment($('#monthly-datepicker').datepicker('getDate')).format('MM/YYYY'))
            return moment($('#monthly-datepicker').datepicker('getDate')).format('MM/YYYY')
        }
    }



    var next = function(){
        if (get_timestamp() === "daily") {
            var date = moment( $('#daily-datepicker').datepicker('getDate')).format('DD/MM/YYYY')
            var plusOneDate = moment(date, 'DD/MM/YYYY').add(1, 'days')
            $('#daily-datepicker').datepicker('update', new Date(plusOneDate))
        } else {
            var date = moment($('#monthly-datepicker').datepicker('getDate')).format('MM/YYYY')
            var plusOneMonth = moment(date, 'MM/YYYY').add(1, 'month')
            $('#monthly-datepicker').datepicker('update', new Date(plusOneMonth))

        }
        createMap()
    }

    var previous = function(){
        if (get_timestamp() === "daily") {
            var date = moment( $('#daily-datepicker').datepicker('getDate')).format('DD/MM/YYYY')
            var minusOneDate = moment(date, 'DD/MM/YYYY').subtract(1, 'days')
            $('#daily-datepicker').datepicker('update', new Date(minusOneDate))
        } else {
            var date = moment($('#monthly-datepicker').datepicker('getDate')).format('MM/YYYY')
            var minusOneMonth = moment(date, 'MM/YYYY').subtract(1, 'month')
            $('#monthly-datepicker').datepicker('update', new Date(minusOneMonth))
        }
        createMap()
    }

    return {
        createMap: createMap,
        next: next,
        previous: previous
    };
}());


aira.LeafletMap = (function namespace(){
    'use strict';
    // Use of aira namespace, determine in base-default.html
    var violet_icon = new L.Icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-violet.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    var yellow_icon = new L.Icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    function selectedAgrifieldCircle(agrifields_list, div, mapid, center, circle, radius){
        $('#map-box').html('')
        $("#map-box").html('<div id="' + mapid + '" class="map"></div>');

        this.createMap(mapid, agrifields_list, center, 10, false, circle, radius)

        if (aira.previous_div) {
             $("#" + aira.previous_div).attr("style", "");
        }
        if (aira.previous_marker) {
             $("#card-" + aira.previous_marker).attr("style", "");
        }

        $("#" + div).attr("style", "border-color: red;border-style: solid");
        aira.previous_div = div
    }

    function selectedAgrifield(agrifield_id, name, lat, log, virtual, div , mapid, radius){
        // store previous selection to temp variable
        $('#map-box').html('')
        $("#map-box").html('<div id="' + mapid + '" class="map"></div>');

        this.createMap(mapid,
                      [{'latitude': lat, 'longitude': log, 'name': name,
                        'virtual': eval(virtual.toLowerCase()),
                        'id': agrifield_id,
                        'radius': radius }],
                      [lat, log ], 16, false, [lat,log], radius)

        if (aira.previous_div) {
             $("#" + aira.previous_div).attr("style", "");
        }
        if (aira.previous_marker) {
             $("#card-" + aira.previous_marker).attr("style", "");
        }
        $("#" + div).attr("style", "border-color: red;border-style: solid");
        // reinit temp variables
        aira.previous_div = div
    }

    function createMap(mapid, agrifields, center, zoom, selector, circle, radius){

        var tempMarker = null
        var map = L.map(mapid).setView(center, zoom);
        L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
            maxZoom: 18
        }).addTo(map);
        var kml_file = "/static/kml/study_area.kml"
        var study_area = omnivore.kml(kml_file).addTo(map);

        if (selector){
            // If selector means that A new agrifield is created
            map.on('click', function(e){
                if (tempMarker){
                    map.removeLayer(tempMarker)
                }
                var newMarker = new L.marker(e.latlng).addTo(map);
                $("#id_latitude").val(e.latlng.lat);
                $("#id_longitude").val(e.latlng.lng);
                tempMarker = newMarker;
            });
        }

        if (aira.previous_circle){
            map.removeLayer(aira.previous_circle)
        }

        if (circle.length > 0) {
            var new_circle = L.circle(circle, radius,
                            { color: 'red',
		                      fillColor: '#f03',
		                      fillOpacity: 0.5 }).addTo(map)
            aira.previous_circle = new_circle
        }

        $.each(agrifields || [], function(i, agrifield){
          if (agrifield.virtual) {
               L.marker([agrifield.latitude, agrifield.longitude],
                {icon:violet_icon, agrifield_id:  agrifield.id, radius: agrifield.radius }).on('click', markerOnClick).addTo(map).bindPopup(agrifield.name)
          }
          else {
              L.marker([agrifield.latitude, agrifield.longitude],
                {icon:yellow_icon, agrifield_id: agrifield.id, radius: agrifield.radius }).on('click', markerOnClick).addTo(map).bindPopup(agrifield.name)
          }
        })

        function markerOnClick(e){

            if (aira.previous_div) {
                 $("#" + aira.previous_div).attr("style", "");
            }

            if (aira.previous_marker) {
                 $("#card-" + aira.previous_marker).attr("style", "");
            }

            if (aira.previous_circle){
                map.removeLayer(aira.previous_circle)
            }
            var new_circle = L.circle(e.latlng, this.options.radius, {
		                              color: 'red',
		                              fillColor: '#f03',
		                              fillOpacity: 0.5 }).addTo(map)
           $("#card-" + this.options.agrifield_id).attr("style", "border-color: red;border-style: solid");
           aira.previous_marker = this.options.agrifield_id
           aira.previous_circle = new_circle

           $('#list-of-agrifields').animate({
               scrollTop: $('#list-of-agrifields').scrollTop() - $('#list-of-agrifields').offset().top  + $("#card-" + this.options.agrifield_id).offset().top
           });



        }
    }

    return {
        createMap: createMap,
        selectedAgrifield:selectedAgrifield,
        selectedAgrifieldCircle:selectedAgrifieldCircle
    };
}());
