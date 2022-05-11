import socket
import sys
import pickle
import os

def handle_msg(message, sock):
    cmd = message["command"]
    sock.sendall(pickle.dumps(message))
    if (cmd == "list"):
        res = pickle.loads(sock.recv(1024))
        print(res.get("cache_list"))
    elif (cmd == "read"):
        filename = message["filename"]
        msg = pickle.loads(sock.recv(1024))
        if (msg.get("error")):
            print(msg["error"])
        else:
            with open(filename, 'wb') as f:
                while True:
                    data = sock.recv(1024)
                    if not data:
                        break
                    f.write(data)
            print("File received.")
            
def client(ip, port, message, directory):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        handle_msg(message, sock)
        sock.close()

HOST, PORT= sys.argv[1], int(sys.argv[2])

if (len(sys.argv) == 4):
    client(HOST, PORT, {"command": "list"}, None)
elif (len(sys.argv) == 5):
    filename, directory = sys.argv[3], sys.argv[4]
    os.chdir(directory)
    client(HOST, PORT, {"command": "read", "filename": filename}, directory)