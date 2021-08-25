cd ..
python3 webserv.py config_bash.cfg &
PID=$!
cd -
sleep 1
curl localhost:8070/cgibin/bash.sh &
curl localhost:8070/cgibin/bash2.sh
kill $PID