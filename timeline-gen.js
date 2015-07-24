var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
var google = require('googleapis');
var xmlhttp = new XMLHttpRequest();
var url = "https://dl.dropboxusercontent.com/u/108441540/dates_and_sources.json";

xmlhttp.onreadystatechange=function() {
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
        google.setOnLoadCallback(drawChart(JSON.parse(xmlhttp.responseText)));
    }
}
xmlhttp.open("GET", url, true);
xmlhttp.send();

function drawChart(json) {
    var container = document.getElementById('timeline');
    var chart = new google.visualization.Timeline(container);
    var dataTable = new google.visualization.DataTable();

    dataTable.addColumn({
        type: 'string',
        id: 'Source'
    });
    dataTable.addColumn({
        type: 'date',
        id: 'Start'
    });
    dataTable.addColumn({
        type: 'date',
        id: 'End'
    });

    for (source in json) {
        for (i = 0; i < json[source]['Start'].length; i++) {
            dataTable.addRow([source, new Date(json[source]['Start'][i], 0, 1), new Date(json[source]['End'][i], 11, 31)]);
        }
    }

    var options = {
        'title': 'Austria Source Information',
            'width': 1000,
            'height': 1000,
    };

    chart.draw(dataTable, options);
}