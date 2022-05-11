# *Multi threaded TCP server*

## *Architecture*
### This server starts a thread with a socket which listens forever on a given port. Every time a client connects to the socket, a new thread is created. When a file is requested to the client, it will first be looked on the server's cache. If it is on cache, file will be sent to the client. If not, the file will be searched on the current working directory (which is set when running the server). If the given file is on the directory, the server will open the file and start reading and sending chunks of the file's data to the client. At the end, all these chunks of datas is stored on the variable `cache_files`, which is a dict that follows this pattern: `cache_files = {"name_of_the_file": [chunks of file data]}`.  At last, if the file doesn't exists, an error will be sent in a dict: `{"error": error_msg}` using pickle.

### Handling caching
#### Cache can store up to 64mb of data. There is a variable called `files_metadata` which stores the file size of all of the files, and also how many times they were requested. Every time a new file is requested, it will be stored in Cache. But, if storing a new file in cache would surpass 64mb of data, then it will start removing all files from the cache (from the oldest entry to the newest) up until the required space to store the new file is reached. 

## Running this project

### Server
#### running server: `python server.py port_to_listen_on file_directory`

### Client 
#### listing files in cache: `python client.py server_host server_port list`
#### requesting file: `python client.py server_host server_port filename directory_to_save`
