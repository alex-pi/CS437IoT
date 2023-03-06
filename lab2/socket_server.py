import socket
from utils import debug,info
from server_utils import MessageHelper
from request_controller import RequestController
#from request_controller_mock import RequestControllerMock


class SocketServer:
    """
    """

    def __init__(self, host="192.168.0.101", port=65432):
        self.host = host
        self.port = port
        self.listening = True
        #self.sel = selectors.DefaultSelector()
        #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.bind((host, port))
        self.lsock.listen()

        info(f"Listening on {(host, port)}")

        self.rc = RequestController()
        #self.rc = RequestControllerMock()

    def start(self):
        client = None
        try:
            # Main socket server loop
            while self.listening:
                debug("Waiting for client")
                client, clientInfo = self.lsock.accept()
                with client:
                    debug(f"Connection from: {clientInfo}")
                    # Message Helper sends and receives messages in json format
                    mh = MessageHelper(client)
                    # data is a dictionary object with command details for the PiCar.
                    data = mh.receive(use_header=False)
                    # the command object
                    response = self.rc.handle(data)
                    if response:
                        debug(f"Sending response: {response}")
                        mh.send_obj(response, use_header=False)
        except IOError as e:
            print("Socket server error.", e)
        except KeyboardInterrupt:
            print("Exit by ctrl-c")
        finally:
            self.lsock.close()
            if client:
                client.close()
            self.rc.finish()
            print("Socket closed")

    def stop(self):
        self.listening = False


if __name__ == '__main__':
    #ss = SocketServer(host="localhost")
    ss = SocketServer()
    ss.start()