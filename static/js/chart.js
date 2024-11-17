    var cv = document.getElementById('lineChart')
    var ctx = cv.getContext('2d');
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: {{ template_labels | tojson }},
            datasets: [{
                label: "Peso",
                data: {{ template_values_confirmed }},
                backgroundColor: "#3399ff",
                borderColor: "#3399ff",
                fill: false,
            },
            //{
            //    label: "Covid 19 deaths",
            //    data: {{ template_values_deaths }},
            //    backgroundColor: "#000066",
            //    borderColor: "#000066",
            //    fill: false,
            //},
            //{
            //    label: "Covid 19 recovered",
            //    data: {{ template_values_recovered }},
            //    backgroundColor: "#33cc33",
            //    borderColor: "#33cc33",
            //    fill: false,
            //},
            ]
        },
        options: {
            title: {
                display: false,
                text: 'line chart with drilldowns'
            },
            legend: {
                onHover: function(e) {
                    e.target.style.cursor = 'pointer';
                }
            },
            hover: {
                onHover: function(e) {
                    var point = this.getElementAtEvent(e);
                    if (point.length) e.target.style.cursor = 'pointer';
                    else e.target.style.cursor = 'default';
                }
            }
        },
    });
    cv.onclick = function(evt) {
        var activePoints = chart.getElementsAtEventForMode(evt, 'point', chart.options);
        var firstPoint = activePoints[0];

        // if activePoints array len > 0, build up the link, and go to the drilldown page
        // this is to cover the case when the legend is clicked

        if (activePoints.length > 0) {
            var label = chart.data.labels[firstPoint._index];
            // in case you need to get also the value
            // var value = chart.data.datasets[firstPoint._datasetIndex].data[firstPoint._index];

            //var url = "/" + label;
            //window.location = url
        }
    };
