cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
sleep 1
curl localhost:8070/greetings.html | diff - greetings_expected.out 
kill $PID
