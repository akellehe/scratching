var http = require('http');

http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.write(`${req.url} => Hello World!`);
  setTimeout(function() {
    res.end();
  }, 5000);
}).listen(8080);