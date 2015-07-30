import sys

source = sys.argv[1]
file_name = sys.argv[2]
source_name = sys.argv[3]
html = """<html>
  <head>
    <h2 align = "center">""" + source_name + """</h2>
    <script type="text/javascript" src="https://www.google.com/jsapi?autoload={'modules':[{'name':'visualization','version':'1.1','packages':['timeline']}]}"></script>
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <script type="text/javascript">

$.getJSON(\""""

html += str(source)
html += """", function(json) {
    google.setOnLoadCallback(drawChart(json));
});



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
            dataTable.addRow([source, new Date(json[source]['Start'][i], 0, 1), new Date(json[source]['End'][i] + 1, 0, 1)]);
        }
    }

    var options = {
            'width': 1000,
            'height': 1000
    };

    chart.draw(dataTable, options);
}
    </script>
  </head>
  <body>
    <div id="timeline" style="height: 180px;"></div>
  </body>
</html>"""

Html_file = open(file_name, 'w')
Html_file.write(html)
Html_file.close()
