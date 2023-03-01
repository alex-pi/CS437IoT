import socket
import json
from utils import debug


class MessageHelper:
    """demonstration class only
      - coded for clarity, not efficiency
    """

    def __init__(self, sock=None, header_len=10):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        self.header_len = header_len

    def connect(self, host, port):
        self.sock.connect((host, port))

    def __send(self, msg, use_header):
        total_sent = 0
        msg_to_send = msg.encode('utf-8')

        if not use_header:
            debug(f"Sending message {msg_to_send}")
            self.sock.send(msg_to_send)
            return

        message_header = f"{len(msg):<{self.header_len}}".encode('utf-8')
        msg_to_send = message_header + msg.encode('utf-8')
        debug(f"Sending message {msg_to_send}")
        while total_sent < len(msg_to_send):
            sent = self.sock.send(msg_to_send[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

    def receive(self, use_header=True):
        chunks = []
        bytes_recd = 0
        msg_len = 1024

        if not use_header:
            json_str = self.sock.recv(msg_len).decode('utf-8')
        else:
            header = self.sock.recv(self.header_len)
            msg_len = int(header.decode('utf-8').strip())
            while bytes_recd < msg_len:
                chunk = self.sock.recv(min(msg_len - bytes_recd, 1024))
                if chunk == b'':
                    raise RuntimeError("socket connection broken")
                chunks.append(chunk)
                bytes_recd = bytes_recd + len(chunk)
            json_str = (b''.join(chunks)).decode('utf-8')

        debug(f"Message received: {json_str}")
        if not json_str:
            return {}
        return json.loads(json_str)

    def send_obj(self, obj, use_header=True):
        json_msg = json.dumps(obj)
        self.__send(json_msg, use_header)

    def send_cmd(self, cmd, params, use_header=True):
        req = {
            "cmd": cmd,
            "params": params
        }
        json_msg = json.dumps(req)
        self.__send(json_msg, use_header)

        return req

