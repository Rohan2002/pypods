import socket
import os

def server_program():
    # Define the Unix domain socket file path
    socket_file = "/tmp/uds_socket"

    # Ensure the socket does not already exist
    if os.path.exists(socket_file):
        os.remove(socket_file)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as pod_socket:
        pod_socket.bind(socket_file)
        pod_socket.listen(1)

        conn, client_address = pod_socket.accept()
        print(f"client_address: {client_address}")
        while True:
            # Receive data
            data = conn.recv(1024)
            if not data:
                break
            print(f"Received {data.decode()}")

            # Send a response
            response = "op readback"
            conn.sendall(response.encode())

    os.remove(socket_file)

if __name__ == '__main__':
    server_program()
