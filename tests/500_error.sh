cd ..
python3 webserv.py config_error.cfg &
PID=$!
cd -
sleep 1
curl -I localhost:8070/bgibin/hello.py | grep '500' | diff - 500_status_expected.out 
kill $PID