class LibTwo:
    def __init__(self) -> None:
        pass

    def create_response():
        return {
            "type": "Table",
            "config": {
                "a": 1,
                "b": [1, 2, 3],
                "c": {
                    [1, 2, 3],
                    [4, 5, 6]
                }
            }
        }

# client.py

import socket
from os.path import exists
from errors import PyPodNotStartedError
def client_program():
    # Define the Unix domain socket file path
    socket_file = "/tmp/uds_socket"
    if not exists(socket_file):
        raise PyPodNotStartedError(f"Pod has not started yet!")
    
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(socket_file)
        while True:
            # Send message
            msg = "op".encode()
            client_socket.sendall(msg)
            
            # Receive response
            data = client_socket.recv(1024)
            print("Received from server:", data.decode())

if __name__ == '__main__':
    client_program()

