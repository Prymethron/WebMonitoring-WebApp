function plot(i) {
    $('#plot_text').val($('#plotbutton' + i).val());
}

function sendDeleteRequest(selectedcontainer) {
    selectedcontainer.style.display = 'none';
    var valueholder = selectedcontainer.querySelector('button')
    $('#del').val(valueholder.value);
    document.getElementById('formDelete').submit();
}


function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function getRandomColor_Specified() {
    var colors = ['#df8dc7', '#fe97a8', '#5e9ca5', '#ebccd4'];
    var color_number = Math.floor(Math.random() * 4);
    return colors[color_number];
}

$(document).ready(function () {
    if (document.location.pathname == "/home") {
        $(sitelist_div).css('margin-left', '-1200px')
        $('#sitelist_div').animate({
            marginLeft: "+=1200px"
        }, 2000);
    }
});

if (document.location.pathname == "/plot") {
    document.getElementById('b1').style.display = 'block';
    document.getElementById('b2').style.display = 'block';
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
var color = getRandomColor_Specified();
var prevButton = document.getElementById('b1');
var nextButton = document.getElementById('b2');
var timeofdayData = [];
for(let i=0;i<=23;i++){
    timeofdayData.push([i,0,0]);
}
var minhour = 0;
var maxhour = 12;
var MAX = 24;

google.charts.load("current", { packages: ["corechart"] });
google.charts.setOnLoadCallback(drawChart);

function drawChart() {

    prevButton.disabled = true;
    nextButton.disabled = true;

    var dataTable = new google.visualization.DataTable();
    dataTable.addColumn('timeofday', 'Time of Day');
    dataTable.addColumn('number', 'Elapsed Time');
    dataTable.addColumn({ type: 'string', role: 'tooltip' });

    for (let i = 0; ; i++) {
        dataTable.addRows([[[parseInt(zValues[i].split(":")[0]), parseInt(zValues[i].split(":")[1]), 0]
            , yValues[i], "Status Code : " + xValues[i].toString() + "\n Elapsed Time : "  + yValues[i] + "\n Time of Day : " + zValues[i]]]);
        if (xValues[i + 1] == null) {
            break;
        }
    }

    var options = {
        height: 500,
        width: 800,
        title: chart_title,
        legend: { position: 'none' },
        colors: [color],
        animation: {
            duration: 1000,
            easing: 'in'
        },
        backgroundColor: { stroke: '#dee8ec', strokeWidth: 10 },
        chartArea: {
            left: 50,
            right: 50,
            top: 60,
            bottom: 50,
        },
        hAxis: {
            viewWindow: {
                min: [minhour,0,0],
                max: [maxhour,0,0],
            },
        }

    };

    chart = new google.visualization.ColumnChart(document.getElementById('Chart'));

    google.visualization.events.addListener(chart, 'ready',
        function () {
            prevButton.disabled = minhour <= 0;
            nextButton.disabled = maxhour >= MAX;
        });

    chart.draw(dataTable, options);
}

prevButton.onclick = function () {
    minhour -= 4;
    maxhour -= 4;
    drawChart();
}

nextButton.onclick = function () {
    minhour += 4;
    maxhour += 4;
    drawChart();
}