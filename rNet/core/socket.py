import threading
import time
import socket

def ClientConnect_PythonSocket(dest, debug=True):
    AF_INET_ADDRESS = dest.split(':')[0]
    PORT = int(dest.split(':')[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def checkConnection():
        while True:
            time.sleep(5)
            if sock is None:
                return False
            try:
                sock.send(b'ping')
                return True
            except Exception as e:
                if debug:
                    print("Connection lost: ", e)
                return False
    
    threading.Thread(target=checkConnection, daemon=True).start()
    
    try:
        r = sock.connect((AF_INET_ADDRESS, PORT))
        if r != None:
            if debug:
                print("Connection failed with error code: ", r)
            return False
        if debug:
            print("Connected to server")

        userId = sock.recv(1024).decode()

        return [sock, userId]
    except Exception as e:
        if debug:
            print("Connection failed: ", e)
        return False
    
    

def ServerStart_PythonSocket(dest, debug=True, connected : dict={}):
    AF_INET_ADDRESS = dest.split(':')[0]
    PORT = int(dest.split(':')[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    sock.bind((AF_INET_ADDRESS, PORT))
    sock.listen()
    sock.setblocking(False)

    if debug:
        print("Server started on: ", dest)

    def run():
        while True:
            try:
                conn, addr = sock.accept()
            except BlockingIOError:
                time.sleep(0.01)
                continue

            conn.send(str(addr[1]).encode())
            connected[str(addr[1])] = conn

    threading.Thread(target=run, daemon=True).start()

    return sock