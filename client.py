import socket

soc = socket.socket()

connection = soc.connect(('127.0.0.1', 1234))

while True:
    data = input()
    soc.send(data.encode('utf-8'))

    if not data or data == 'exit':
        break

    result = soc.recv(1024).decode('utf-8')
    print(result)

soc.close()
