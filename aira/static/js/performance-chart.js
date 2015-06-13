console.log("Hello from static motherfucker !!!");


$(function () {
    $('#irrchart').highcharts({
      chart: {
          type: 'column'
      },
      title: {
          text: performance.title
      },
      subtitle: {
          text: performance.subtitle
      },
      xAxis: {
          categories: performance.dates,
          type: 'datetime',
          dateTimeLabelFormats: {
                  day: '%d-%m-%Y'
                },
          crosshair: true
      },
      yAxis: {
          min: 0,
          title: {
              text: 'performance'
          }
      },
      tooltip: {
          headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
          pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
              '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
          footerFormat: '</table>',
          shared: true,
          useHTML: true
      },
      plotOptions: {
          column: {
              pointPadding: 0.2,
              borderWidth: 0
          }
      },
      series: [{
          name: performance.ifinal_title,
          data: performance.ifinal

      }, {
          name: performance.applied_water_title,
          data: performance.applied_water

      }]
  });
});
