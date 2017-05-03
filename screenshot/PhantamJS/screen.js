var page = require('webpage').create();
//viewportSize being the actual size of the headless browser
page.viewportSize = { width: 1024, height: 768 };
//the clipRect is the portion of the page you are taking a screenshot of
page.clipRect = { top: 0, left: 0, width: 1024, height: 768 };
//the rest of the code is the same as the previous example
page.open('https://www.google.com/search?q=image&rlz=1C5CHFA_enUS732US732&oq=image&aqs=chrome..69i57j69i61j69i57j69i60l3.663j0j7&sourceid=chrome&ie=UTF-8', function() {
  page.render('screenshot.png');
  phantom.exit();
});
