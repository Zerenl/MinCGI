# MinCGI
The Common Gateway Interface is used by web-servers to allow compatible programs to be executed on the server, to process HTTP requests and compute a HTTP response. The web-server uses standard input and output as well as environment variables for communication between the CGI program and the itself. HTTP requests that are received by the web-server can be passed to a CGI program via shell environment variables and standard input.  
  

This application is assumeing the length of each web request are no more then 1024 bytes and the output of cgi program is also less than 1024 bytes
In addition, it also assume the context type for a cgi program that will not contains a context type that is text/html in they output  
  
This application will send a compressed response body back to the browser by gzip when browser's request accept gzip encoding.
The testcase compres_test.sh shows that when request header contains Accept-Encodeing and it also contains gizp
for both cgi program and static file request then this server will send back a compressed data that need to be decompressd to browser.
