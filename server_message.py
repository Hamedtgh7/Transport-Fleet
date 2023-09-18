import socket
import threading

HOST = '127.0.0.1'
PORT = 1373
clients = {}


def handle_client(conn, addr):
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break

            command, *params = data.decode().strip().split(' ')
            if command == 'Subscribe':
                topic = params[0]
                if addr in clients:
                    clients[addr].append(topic)
                else:
                    clients[addr] = [topic]

                conn.sendall(b'SubAck')
            elif command == 'Publish':

                topic = params[0]
                message = params[1]
                for client_addr, topics in clients.items():
                    if topic in topics:

                        send_message(client_addr, message, topic)

                conn.sendall(b'PubAck')
            elif command == 'Ping':
                pass
            else:
                print('Invalid command:', command)

    if addr in clients:
        del clients[addr]
    print('Disconnected by', addr)


def send_message(client_addr, message, topic):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((client_addr[0], PORT))
        data = f'Message {topic} {message}'.encode()
        sock.sendall(data)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print('Server is listening on', HOST, 'port', PORT)

while True:
    conn, addr = server_socket.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
