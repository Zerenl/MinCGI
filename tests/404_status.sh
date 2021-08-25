cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
sleep 1
curl -I localhost:8070/missing.html 2> /dev/null | grep '404' | diff - 404_status_expected.out 
kill $PID
