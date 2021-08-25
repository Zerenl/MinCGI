import sys
import socket
import os
import gzip


def load_config(filepath):
	try:
		file = open(filepath, 'r')
	except FileNotFoundError:
		sys.exit("Unable To Load Configuration File")

	content = file.readlines()
	staticfiles = None
	cgibin = None
	port = None
	execute = None
	for line in content:
		line = line.strip().split("=")
		if line[0] == "staticfiles":
			staticfiles = line[1]
		elif line[0] =="cgibin":
			cgibin = line[1]
		elif line[0] =="port":
			port = int(line[1])
		elif line[0] == "exec":
			execute = line[1]
	
	return staticfiles,cgibin,port,execute


def create_socket(port):
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
	s.bind(("localhost", port))
	s.listen(5)

	return s



def send_404FilenotFound(conn):
	
	status = "HTTP/1.1 404 File not found\n".encode()
	content_type = "Content-Type: text/html\n".encode()
	response = "\n<html>\n<head>\n	<title>404 Not Found</title>\n</head>\n<body bgcolor=\"white\">\n<center>\n	<h1>404 Not Found</h1>\n</center>\n</body>\n</html>\n".encode()
	conn.send(status)
	conn.send(content_type)
	conn.send(response)
	conn.close()
	

def send_500InternalServerError(conn):
    	
	status = "HTTP/1.1 500 Internal Server Error\n".encode()
	content_type = "Content-Type: text/html\n".encode()
	response = "\n<html>\n<head>\n	<title>500 Internal Server Error</title>\n</head>\n<body bgcolor=\"white\">\n<center>\n	<h1>500 Internal Server Error</h1>\n</center>\n</body>\n</html>\n".encode()
	conn.send(status)
	conn.send(content_type)
	conn.send(response)
	conn.close()


#function that handle the situation when requst a static file
#send the content of the static file back to brower
#if file does not exist send 404 error back
def static_file_handler(conn, staticfiles, request_url, Is_response_compress):
    	
	#send 404 error message to client if file not exists 
	if not os.path.isfile(staticfiles+request_url):
		send_404FilenotFound(conn)
		conn.close()
		return


	status = "HTTP/1.1 200 OK\n"
	
	#check the type of request static file
	type = None
	if request_url.endswith(".txt"):
		type = "text/plain"
	elif request_url.endswith(".html"):
		type = "text/html"
	elif request_url.endswith(".js"):
		type = "application/javascript"
	elif request_url.endswith(".css"):
		type = "text/css"
	elif request_url.endswith(".png"):
		type = "image/png"
	elif request_url.endswith(".jpg"):
		type = "image/jpeg"
	elif request_url.endswith(".xml"):
		type = "text/xml"

	
	if type == "image/png" or type == "image/png":
    		
		try:
			file = open(staticfiles+request_url, "rb")
			content = file.read()
		except Exception:
			send_404FilenotFound(conn)
			conn.close()
			return
	else:
		try:
			file = open(staticfiles+request_url, "r")
			content = "".join([str(line) for line in file.readlines()])
		except Exception:
			send_404FilenotFound(conn)
			conn.close()

			return
	
	content_type = ""
	if type != None:
		content_type = "Content-Type: {}\n".format(type)

	#when the type of this file is a picture then we dont need to encode since it is already in binary
	if type == "image/png" or type == "image/png":
		response = content
	else:
		response = content.encode()

	conn.send(status.encode())
	conn.send(content_type.encode())
	conn.send("\n".encode())

	#extension part if browser request compress the data
	if Is_response_compress:
		response = gzip.compress(response)
		
	conn.send(response)

#setup environ variable when request cgi program file
def set_envir_var(request_header, client_addr, request_method, request_url, s):
    	
	for header in request_header:
		header = header.split(": ")
		if "Accept" == header[0]:
			os.environ['HTTP_ACCEPT'] = header[1]
		elif "Host" == header[0]:
			os.environ['HTTP_HOST'] = header[1]
		elif "User-Agent" == header[0]:
			os.environ['HTTP_USER_AGENT'] = header[1]
		elif "Accept-Encoding" == header[0]:
			os.environ['HTTP_ACCEPT_ENCODING'] = header[1]
		
	
	os.environ['REMOTE_ADDRESS'] = str(client_addr[0])
	os.environ['REMOTE_PORT'] = str(client_addr[1])
	os.environ['REQUEST_METHOD'] = request_method
	os.environ['REQUEST_URI'] = request_url
	os.environ['SERVER_ADDR'] = str(s.getsockname()[0])
	os.environ['SERVER_PORT'] = str(s.getsockname()[1])

	if "?" in request_url:
		query_string = request_url.split("?")[1]
		os.environ["QUERY_STRING"] = query_string


#if request a cgi program then fork again and use pipe to recive the output and send back to browser
def cgi_program_handler(conn, execute, cgibin):
    	
	program_name = os.environ['REQUEST_URI'].replace("/cgibin/", "")
	if "?" in program_name:
		program_name = program_name.split("?")[0]
	program_name = cgibin+"/"+program_name


	pid = os.fork()

	if pid == -1:
		return None
	if pid != 0:
		return pid

	if os.path.isfile(program_name) == False:
    	
		send_404FilenotFound(conn)
		conn.close()
		sys.exit(-1)
	
	try:

		if "QUERY_STRING" in os.environ:
			
			os.execlp(os.path.basename(execute), os.path.basename(execute), program_name, os.environ['QUERY_STRING'])
		else:
			os.execlp(os.path.basename(execute), os.path.basename(execute), program_name)

	except Exception:
		sys.exit(-1)

	#exec fail
	sys.exit(-1)
	

def parse_data(request):
    
	first_line = request[0].split(" ")
	request_method = first_line[0]
	request_url = first_line[1]
	request_protocol = first_line[2]
	request_header = []
	i = 1
	while i < len(request):
		if request[i] != "\r":
			request_header.append(request[i].strip())
			i += 1
		else:
			break
	

	Is_request_for_CGI = False

	#if url contains ./cgibin then this ia cgi program
	if request_url.startswith("/cgibin/"):
		Is_request_for_CGI = True


	return Is_request_for_CGI, request_method, request_url, request_protocol, request_header


def create_process(s, conn, addr , staticfiles, execute , cgibin):
    	
	request = conn.recv(1024).decode().split("\n")

	Is_request_for_CGI, request_method, request_url, request_protocol, request_header = parse_data(request)

	Is_response_compress = False
	
	#extension part, check compress need or not
	for header in request_header:
		if "Accept-Encoding" == header.split(": ")[0]:
			if "gzip" in header.split(": ")[1]:
				Is_response_compress = True

	pid = os.fork()

	if pid == -1:
		return None

	if pid != 0:
		conn.close()
		return pid

	if Is_request_for_CGI:
		
		pipe_read, pipe_write = os.pipe()
		pipe_write = os.fdopen(pipe_write, 'w')
		os.dup2(pipe_write.fileno(),1)

		set_envir_var(request_header, addr, request_method, request_url, s)

		pid = cgi_program_handler(conn, execute, cgibin)

		if pid == None:
			conn.close()
			sys.exit(0)

		pipe_write.close()

		# check whether child process exits normally
		child_pid,status = os.waitpid(pid, 0)
		status = os.WEXITSTATUS(status)
		
		#if child process exit non-zero status than send 500 error back to browser
		if status != 0:
			send_500InternalServerError(conn)
			conn.close()
			sys.exit(0)
		
		#handle cgi program's output and send to client
		#assume cgi program will always has output
		pipe_read = os.fdopen(pipe_read)
		cgi_output = os.read(pipe_read.fileno(), 1024)
		cgi_output = cgi_output.decode().strip("\n").split("\n")

		if cgi_output[0] == "ERROR":
			conn.close()
			sys.exit(0)
		
		#default status info for cgi	
		status_code_value = "200"
		status_code_message = "OK"
		#if cgi program's output contains status code then replace default status code
		Is_status_exist = False
		if "Status-Code" in cgi_output[0]:
			Is_status_exist = True
			status_code = cgi_output[0].split(": ")[1]
			status_code_value = status_code.split(" ")[0]
			status_code_message = " ".join(status_code.split(" ")[1:]).strip("\n")
			cgi_output.pop(0)

		status = "HTTP/1.1 {} {}\n".format(status_code_value, status_code_message)

		#default type
		type ="text/html"
		
		#if output contains content type of request then replacce default type with it
		#only first content type is valid
		for line in cgi_output:
			if line.startswith("Content-Type"):
				type = line.split(": ")[1].strip("\n")
				cgi_output.remove(line)
				break
			
		content_type = "Content-Type: {}\n".format(type)
		
		pipe_read.close()
		response = "\n".join(cgi_output).strip("\n")+"\n"
		response = response.encode()

		#send data to client
		conn.send(status.encode())
		conn.send(content_type.encode())
		conn.send("\n".encode())
		if Is_response_compress:
			response = gzip.compress(response)
		conn.send(response)
		conn.close()

	else:
		if request_url == "/":
			request_url = "/index.html"

		static_file_handler(conn, staticfiles, request_url, Is_response_compress)

	sys.exit(0)
	

def main():
    	
	if len(sys.argv) != 2:
		sys.exit("Missing Configuration Argument")
	
	staticfiles,cgibin,port,execute = load_config(sys.argv[1])

	#config file missing field
	if staticfiles == None or cgibin == None or port == None or execute == None:
		sys.exit("Missing Field From Configuration File")

	s = create_socket(port)

	#mian loop
	while True:
		conn,addr = s.accept()
		#fork every connection
		pid = create_process(s, conn,addr,staticfiles,execute,cgibin)

		if pid == None:
			conn.close()
			
		

if __name__ == '__main__':
	main()

		
		