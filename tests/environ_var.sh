cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
sleep 1
curl -H 'Accept: text/html' -H 'Accept-Encoding: gzip' -H 'Host: localhost' -H 'User-Agent: X11' 'localhost:8070/cgibin/environ.py?id=20&name=testname' | diff - environ_expected.out
kill $PID