function selected() {
    $('#d').val($('#site').find(':selected').val());
    $('#del').val($('#site').find(':selected').val());
    $('#plot_text').val($('#site').find(':selected').val());
}

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function getRandomColor_Black() {
    var colors = ['#352f35', '#8c8c8c', '#2c2c2c', '#535353'];
    var color_number = Math.floor(Math.random() * 4);
    return colors[color_number];
}

var chart_title = document.getElementById("Chart").getAttribute("value");
var xValues = $('#statuscode').val();
xValues = JSON.parse(xValues);
var yValues = $('#eltime').val();
yValues = JSON.parse(yValues);
var zValues = $('#currenttime').val();
zValues = zValues.replace(/'/g, '"');
zValues = JSON.parse(zValues);

var data;
var chart;
var prevButton = document.getElementById('b1');
var nextButton = document.getElementById('b2');
var MAX = 24;

var options = {
    height: 500,
    width: 800,
    title: chart_title,
    legend: { position: 'none' },
    colors: [getRandomColor_Black()],
    animation: {
        duration: 1000,
        easing: 'in'
      },
    backgroundColor: { stroke: 'gray', strokeWidth: 10 },
    chartArea: {
        left: 50,
        right: 50,
        top: 60,
        bottom: 50,
    },
    hAxis: {
        ticks: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
        viewWindow: {
            min: 0,
            max: 12
        }
    }
};

google.charts.load("current", { packages: ["corechart"] });
google.charts.setOnLoadCallback(drawChart);

dataArray = [[{ label: 'status code' }, { label: 'Time Of Day' }]]
for (let i = 0; ; i++) {
    dataArray.push(["Status code : " + xValues[i].toString() + " Elapsed Time : " + yValues[i].toString(), parseInt(zValues[i].split(":")[0])]);
    if (xValues[i + 1] == null) {
        break;
    }
}

function drawChart() {
    prevButton.disabled = true;
    nextButton.disabled = true;

    data = google.visualization.arrayToDataTable(dataArray);
    chart = new google.visualization.Histogram(document.getElementById('Chart'));
    
    google.visualization.events.addListener(chart, 'ready',
        function () {
            prevButton.disabled = options.hAxis.viewWindow.min <= 0;
            nextButton.disabled = options.hAxis.viewWindow.max >= MAX;
        });

    chart.draw(data, options);
}

prevButton.onclick = function () {
    options.hAxis.viewWindow.min -= 4;
    options.hAxis.viewWindow.max -= 4;
    drawChart();
}

nextButton.onclick = function () {
    options.hAxis.viewWindow.min += 4;
    options.hAxis.viewWindow.max += 4;
    drawChart();
}

 