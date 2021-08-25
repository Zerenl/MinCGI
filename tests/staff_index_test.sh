cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
sleep 1
curl localhost:8070/ | diff - index_expected.out 
kill $PID
