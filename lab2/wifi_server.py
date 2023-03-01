import socket
from server_utils import MessageHelper

#HOST = "192.168.0.101" # IP address of your Raspberry PI
HOST = "localhost"
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    try:
        while 1:
            print("before accept")
            client, clientInfo = s.accept()
            print("server recv from: ", clientInfo)
            print("before recv")
            # receive 1024 Bytes of message in binary format
            sh = MessageHelper(client)
            data = sh.receive()
            print(data)
            sh.send(data)
            #data = client.recv(1024)
            if data != b"":
                print(data)
                client.sendall(data) # Echo back to client
    except:
        print("Closing socket")
        client.close()
        s.close()