var system = require('system');
var page = require('webpage').create();
page.open('index.html', function () {
    page.paperSize = { format: 'A4', orientation: 'landscape'};
    page.render(system.args[1]);
    phantom.exit();
});