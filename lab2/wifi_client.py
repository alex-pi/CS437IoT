import socket
from server_utils import MessageHelper

#HOST = "192.168.0.101" # IP address of your Raspberry PI
HOST = "localhost"
PORT = 65432          # The port used by the server

while True:
    # Note change to the old (Python 2) raw_input
    params = {}
    cmd_test = input("Enter your command: ")
    if cmd_test == "quit":
        break
    if cmd_test in ['f', 'b']:
        cmd_test = 'forward' if cmd_test == 'f' else 'backward'
        params['distance'] = int(input("Enter the distance: "))
    if cmd_test in ['l', 'r']:
        cmd_test = 'left' if cmd_test == 'l' else 'right'
        params['angle'] = int(input("Enter the angle: "))
    if cmd_test == 'm':
        cmd_test = 'metrics'
    if cmd_test == 's':
        cmd_test = 'stop'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        mh = MessageHelper(s)
        
        #s.send(text.encode())     # send the encoded message (send in binary format)
        mh.send_cmd(cmd_test, params, use_header=False)

        if cmd_test == 'metrics':
            data = mh.receive(use_header=False)
            print(f"Client received: {data}")

        #data = s.recv(1024)
        #data = sh.receive()
        #print("echo from server: ", data)