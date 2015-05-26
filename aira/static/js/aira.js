$("#form_datetime").datetimepicker({
    format: "yyyy-mm-dd",
    startDate: "2015-01-01",
    initialDate: aira.yesterday,
    endDate: aira.yesterday,
    autoclose: true,
    pickerPosition: "bottom-left",
    minView:2,
    startView:2,
    todayHighlight:false,
    linkField: "mirror_field",
    linkFormat: "yyyy-mm-dd",
    pickerPosition: "bottom-left"
});

function create_map(date, meteo_var)
{
    date = (date === undefined) ? aira.yesterday : date;
    meteo_var = (meteo_var === undefined) ? 'Daily_rain_' : meteo_var;
    // Clear previous map
    document.getElementById('wms_map').innerHTML = ""
    // Map object
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
    var base_cycle = new OpenLayers.Layer.OSM.CycleMap(
              "Open Cycle Map",
              {isBaseLayer: true,
               projection: 'EPSG:3857'});
    map.addLayer(base_cycle);
    // Loop to add WMS layers
    var ktimatologio = new OpenLayers.Layer.WMS("Hellenic Cadastre",
               "http://gis.ktimanet.gr/wms/wmsopen/wmsserver.aspx",
                 {   layers: 'KTBASEMAP', transparent: false},
                 {   isBaseLayer: true,
                     projection: new OpenLayers.Projection("EPSG:900913"),
                     iformat: 'image/png'});
    map.addLayer(ktimatologio);
    var map_variable = new OpenLayers.Layer.WMS(
              meteo_var + date,
              "http://megdobas.irrigation-management.eu/cgi-bin/mapserver?map=/var/cache/pthelma/mapserver-historical.map",
              {layers: meteo_var + date,
               format: 'image/png'},
              {isBaseLayer: false,
               projection: 'EPSG:3857',
               opacity: 0.65});
    map.addLayer(map_variable);
    document.getElementById('current').innerHTML = aira.trans_viewing + date;
    document.getElementById('next').value = moment(date, "YYYY-MM-DD").add(1,'days').format("YYYY-MM-DD");
    var n = moment(document.getElementById('next').value, "YYYY-MM-DD");
    if (n.isAfter(aira.yesterday)) {
        document.getElementById('next').style.display ='none';
    } else {
        document.getElementById('next').style.display = 'inline-block';
        document.getElementById('next').innerHTML = moment(date, "YYYY-MM-DD").add(1,'days').format("YYYY-MM-DD") + "&nbsp;<i class='fa fa-chevron-right'></i>&nbsp;";
    }

    document.getElementById('previous').value = moment(date, "YYYY-MM-DD").subtract(1,'days').format("YYYY-MM-DD");
    var pr = moment(document.getElementById('previous').value, "YYYY-MM-DD");
    if (pr.isBefore('2015-01-01')) {
        document.getElementById('previous').style.display ='none';
    } else {
        document.getElementById('previous').style.display ='inline-block';
        document.getElementById('previous').innerHTML = "&nbsp;<i class='fa fa-chevron-left'></i>&nbsp;" + moment(date, "YYYY-MM-DD").subtract(1,'days').format("YYYY-MM-DD");
    }

    // When clicking on the map, show popup with values of variables
    OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {
        defaultHandlerOptions: {
            'single': true,
            'double': false,
            'pixelTolerance': 0,
            'stopSingle': false,
            'stopDouble': false
        },
        initialize: function(options) {
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
        trigger: function(e) {
            var lonlat = map.getLonLatFromPixel(e.xy);
            var xhr = new XMLHttpRequest();

            // Create a small bbox such that the point is at the bottom left of the box
            var xlow = lonlat.lon;
            var xhigh = lonlat.lon + 50;
            var ylow = lonlat.lat;
            var yhigh = lonlat.lat + 50;
            var bbox = xlow + ',' + ylow + ',' + xhigh + ',' + yhigh

            // Determine layers
            var layers='';
            ['temperature', 'humidity', 'wind_speed', 'rain', 'evaporation',
             'solar_radiation'].forEach(function(s) {
                if (layers != '') {
                    layers = layers + ',';
                }
                layers = layers + 'Daily_' + s + '_' + date;
            })

            // Assemble URL
            var url = 'http://arta.irrigation-management.eu/mapserver-historical/';
            url = url + '?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&SRS=EPSG:3857&info_format=text/html';
            url = url + '&BBOX=' + bbox + '&WIDTH=2&HEIGHT=2&X=0&Y=0';
            url = url + '&LAYERS=' + layers + '&QUERY_LAYERS=' + layers;

            xhr.open('GET', url, false);
            xhr.send()
            /* The test "length < 250" below is an ugly hack for not showing
             * popups at a masked area. The masked area has the value nodata,
             * which displays as a large negative number with very many digits.
             */
            if (xhr.readyState == 4  &&  xhr.responseText.length < 250) {
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

    // Add controll and center
    map.setCenter (new OpenLayers.LonLat(20.98, 39.15).transform('EPSG:4326', 'EPSG:3857'), 10);
 }

function previous_map() {
    var swap_date = document.getElementById('previous').value
    var meteo_var = document.getElementById('meteo_var').value
    create_map(swap_date, meteo_var);
}

function next_map() {
    var swap_date = document.getElementById('next').value
    var meteo_var = document.getElementById('meteo_var').value
    create_map(swap_date, meteo_var);
}

function current() {
    var swap_date = document.getElementById('current').value
    var meteo_var = document.getElementById('meteo_var').value
    create_map(swap_date, meteo_var);
}
