import threading
import socket


class Calculator(threading.Thread):
    def __init__(self, connection: socket.socket):
        super().__init__()
        self.conn = connection

    def run(self) -> None:
        while True:
            data = self.conn.recv(
                1024).decode('utf-8').split()

            if not data or data == 'exit':
                break

            operator = data[0]
            op1 = int(data[1])
            op2 = int(data[2])

            if operator == 'add':
                result = op1+op2
            elif operator == 'sub':
                result = op1-op2
            elif operator == 'mul':
                result = op1*op2
            elif operator == 'div':
                result = op1/op2

            self.conn.send(str(result).encode('utf-8'))
            print(result)


soc = socket.socket()
soc.bind(('127.0.0.1', 1234))
soc.listen()

while True:
    c_socket, c_address = soc.accept()
    Calculator(c_socket).start()
