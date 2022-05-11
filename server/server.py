import socket
import threading
import socketserver
import sys
import pickle
import os


HOST, PORT, directory = "localhost", int(sys.argv[1]), sys.argv[2]
os.chdir(directory)
BUFFER_SIZE = 1024
MAX_CACHE_SIZE = 64 * 1024 * 1024

cache_files = {}
files_metadata = {}

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    
    def update_metadata(self, filename, file_size):
        global files_metadata
        if (filename in files_metadata):
            files_metadata[filename]["times_requested"]+=1
        else:
            files_metadata[filename] = {"times_requested": 1, "size": file_size}
    
    def get_cache_size(self):
        global cache_files
        global files_metadata
        total_size = 0
        for filename in cache_files:
            total_size += files_metadata[filename]["size"]
        return total_size

    def handle_caching(self, filename, file_size, file_data):
        global cache_files
        global files_metadata
        if file_size <= MAX_CACHE_SIZE:
            current_cache_size = self.get_cache_size()
            if (current_cache_size + file_size) > MAX_CACHE_SIZE:
                removed_size = 0
                for key in list(cache_files):
                    removed_size += files_metadata[key]["size"]
                    del cache_files[key]
                    if (removed_size >= file_size):
                        break      
            cache_files[filename] = file_data

    def list_cache(self):
        global cache_files
        cache_filenames = []
        for item in list(cache_files):
            cache_filenames.append(item)
        res = pickle.dumps({"cache_list": cache_filenames})
        self.request.sendall(res)
        return cache_filenames

    def is_existing_file(self,filename):
        if filename in os.listdir():
            return True
        else:
            return False

    def transfer_file(self, filename):
        global cache_files

        if (filename in cache_files):
            lock = threading.Lock()
            lock.acquire()
            self.request.sendall(pickle.dumps({"ok": "sending file..."}))
            file_data = cache_files.get(filename)
            for chunk in file_data:
                self.request.sendall(chunk)
            lock.release()
            print("Cache hit. File ", filename, " sent to client.")

        elif self.is_existing_file(filename):
            file_size = os.stat(filename).st_size
            file_data = []
            self.request.sendall(pickle.dumps({"ok": "sending file..."}))
            with open(filename, "rb") as f:
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    file_data.append(bytes_read)
                    if not bytes_read:
                        break
                    self.request.sendall(bytes_read)
            lock = threading.Lock()
            lock.acquire()
            self.update_metadata(filename, file_size)
            self.handle_caching(filename, file_size, file_data)
            lock.release()
            
            print("Cache miss. File ", filename, " sent to client.")
                
        else:
            error_msg = "File " + filename + " does not exist in the server."
            print(error_msg)
            res = pickle.dumps({"error": error_msg})
            self.request.sendall(res) 

    def handle_command(self, data, client_ip):
        command = data.get("command")
        if (command=="list"):
            return self.list_cache()
        elif (command=="read"):
            filename = data.get("filename")
            print("Client ", client_ip, " is requesting file ", filename)
            return self.transfer_file(filename)

    def handle(self):
        #data = str(self.request.recv(1024), 'ascii')
        req = pickle.loads(self.request.recv(BUFFER_SIZE))
        peer = (self.request.getpeername())
        peer_address = peer[0]
        self.handle_command(req, peer_address)
       
       # self.req.close()
        
       
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def run_server():
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)
        while server_thread:
            #print("Active clients:", threading.active_count())
            #time.sleep(1)
            pass

if __name__ == "__main__":
    run_server()
    