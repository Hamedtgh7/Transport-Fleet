import socket
import threading

HOST = '127.0.0.1'
PORT = 1373
list_topics = {}


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
                if topic in list_topics:
                    list_topics[topic].append(conn)
                else:
                    list_topics[topic] = [conn]

                conn.sendall(b'SubAck')
            elif command == 'Publish':

                topic = params[0]
                message = params[1:]
                conn.sendall(b'PubAck')
                for title, connections in list_topics.items():
                    if topic == title:
                        for connection in connections:
                            send_message(connection, message, topic)

            elif command == 'Ping':
                pass
            else:
                print('Invalid command:', command)

    print('Disconnected by', addr)


def send_message(connection, message, topic):
    data = f'Message {topic} {message}'.encode()
    connection.sendall(data)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print('Server is listening on', HOST, 'port', PORT)

while True:
    conn, addr = server_socket.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
