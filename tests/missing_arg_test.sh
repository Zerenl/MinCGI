cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
sleep 1
python3 ../webserv.py | diff - missing_arg.out
kill $PID
