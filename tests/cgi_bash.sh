cd ..
python3 webserv.py config_bash.cfg &
PID=$!
cd -
sleep 0.1
curl localhost:8070/cgibin/bash.sh
kill $PID