import socket
import sys
import threading
import time

HOST = sys.argv[1]
PORT = int(sys.argv[2])


def send_message(sock, message):
    sock.sendall(message.encode())


def handle_server_response(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break

        command, *params = data.decode().strip().split(' ')
        if command == 'Ping':

            send_message(sock, 'Pong')
        elif command == 'Message':

            topic = params[0]
            message = params[1]
            print(f'{topic}: {message}')
        else:
            print('Invalid command:', command)


def subscribe_topics(sock: socket.socket, topics):
    try:
        sock.settimeout(10)
        for topic in topics:
            send_message(sock, f'Subscribe {topic}')
            response = sock.recv(1024).decode().strip()
            if response == 'SubAck':
                print(f'Subscribing on {topic}')
            else:
                print('subscribing failed')
                return False
        return True
    except socket.timeout:
        print('subscribing failed')
    finally:
        sock.settimeout(None)


def publish_message(sock: socket.socket, topic, message):
    try:
        sock.settimeout(10)
        send_message(sock, f'Publish {topic} {message}')
        response = sock.recv(1024).decode().strip()
        if response == 'PubAck':
            print('Your message published successfully')
        else:
            print('Your message publishing failed')
    except socket.timeout:
        print('Your message publishing failed')
    finally:
        sock.settimeout(None)


operation = sys.argv[3]


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))

    if operation == 'publish':
        topic = sys.argv[4]
        message = sys.argv[5:]
        publish_message(sock, topic, message)
    elif operation == 'subscribe':
        topics = sys.argv[4:]
        if not subscribe_topics(sock, topics):
            sys.exit(1)

        thread = threading.Thread(target=handle_server_response, args=(sock,))
        thread.start()

        while True:
            # send_message(sock, 'Ping')
            # time.sleep(10)
            pass
    else:
        print('Invalid operation')
