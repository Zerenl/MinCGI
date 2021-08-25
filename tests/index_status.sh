cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
sleep 1
curl -I localhost:8070/ 2> /dev/null | grep '200 OK' | diff - index_status_expected.out 
kill $PID
