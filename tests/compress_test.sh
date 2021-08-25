cd ..
python3 webserv.py config.cfg &
PID=$!
cd -
sleep 1
curl  -H 'Accept-Encoding: gzip' localhost:8070/cgibin/compress.py | gunzip | diff - cgi_compress_expected.out
curl  -H 'Accept-Encoding: gzip' localhost:8070 | gunzip | diff - index_expected.out
kill $PID