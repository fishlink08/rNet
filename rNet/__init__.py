"""rNet is a functional wrapper for the Socket.IO library, designed to simplify development for connection-heavy applications."""

from rNet.core import socket
from rNet.core import data

import time
import threading

def ProcessData(self): #using sendall
    while True:
        time.sleep(self.ProcessorDelay)
        for QueueItem in list(self.ProcessDataQueue):
            userid, data = QueueItem

            for userId, conn in self.Connected.items():
                try:
                    conn.sendall(data.encode())
                except Exception as e:
                    if self.debug:
                        print(f"Error sending data to user {userId}: ", e)
                
            self.ProcessDataQueue.remove(QueueItem)

def RecieveData(self): # Process Data Recieved (threaded)
    while self.connected:
        time.sleep(0.1)
        try:
            data = self.Sock.recv(1024)
            if data:
                self.RecieveQueue.append(data.decode())
        except BlockingIOError:
            time.sleep(0.01)
            continue
        except Exception as e:
            if self.debug:
                print("Error receiving data: ", e)
            break

class Host:
    def __init__(self, dest : str = '127.0.0.1:8001', debug : bool=True):
        '''Create a new Host instance. \nParams:
        dest: The destination address for the server.
        debug: Whether to enable debug mode.
        '''
        self.dest = dest
        self.debug = debug

        self.ServerSocket = None
        self.Connected = {}
        self.ProcessorDelay = 0.10

        self.ProcessDataQueue = []

    def __enter__(self):
        if self.debug: 
            print("Server Starting await")

    def __exit__(self, exc_type, exc, tb):
        if self.debug:
            print("Server Error, Disconnecting: ", exc_type, exc, tb)

    def start(self):
        self.ServerSocket = socket.ServerStart_PythonSocket(self.dest, self.debug, self.Connected)

        while not self.ServerSocket:
            time.sleep(0.1)


        def RecieveData(): # ON SEPERATE THREAD -- ORGANIZE SOON
            RemoveCache = set()

            while True:
                for userId, conn in list(self.Connected.items()):
                    try:
                        data = conn.recv(1024)
                        if data:
                            if self.debug:
                                print(f"Received data from user {userId}: {data.decode()}")

                            if data.decode() in ["ping"]:
                                continue

                            self.ProcessDataQueue.append((userId, data.decode()))
                    except BlockingIOError:
                        continue
                    except Exception as e:
                        if self.debug:
                            print(f"Error receiving data from user {userId}: {e}")
                        RemoveCache.add(userId)
                
                for toRemove in RemoveCache:
                   self.Connected.pop(toRemove, None)
                RemoveCache.clear()
                
        RecvDataThread = threading.Thread(target=RecieveData, daemon=True)
        RecvDataThread.start()

        ProcessDataThread = threading.Thread(target=ProcessData, daemon=True, args=(self,))
        ProcessDataThread.start()



class Client:
    '''Create a new Client instance. \nParams:
    dest: The destination address for the client.
    debug: Whether to enable debug mode.
    '''
    def __init__(self, dest : str = '127.0.0.1:8001', debug : bool=True):
        self.dest = dest
        self.debug = debug

        self.connected = False
        self.Sock = None
        self.UserId = None

        self.RecieveThread = None
        self.RecieveQueue = []

    def __enter__(self):
        if self.debug: 
            print("Client Connecting")

    def __exit__(self, exc_type, exc, tb):
        if self.debug:
            print("Client Error, Disconnecting: ", exc_type, exc, tb)

    def wait_connection(self):
        result = socket.ClientConnect_PythonSocket(self.dest, self.debug)
        while not result:
            time.sleep(1)

            if self.debug:
                print("Retrying")
            result = socket.ClientConnect_PythonSocket(self.dest, self.debug)

        self.Sock = result[0]
        self.UserId = result[1]
        
        self.connected = True

        self.Sock.setblocking(False)

        self.RecieveThread = threading.Thread(target=RecieveData, daemon=True, args=(self,))
        self.RecieveThread.start()

        if self.debug:
            print("Connected")
        
    def send(self, data : str):
        if not self.connected:
            if self.debug:
                print("Not connected, cannot send data")
            return False

        try:
            self.Sock.send(data.encode())
            return True
        except Exception as e:
            if self.debug:
                print("Error sending data: ", e)
            return False

    def recieve(self, filter = None) -> dict:
        '''Recieve current thread of sent data by the server (room if avail)
        \n Filter : Optional Parameter = Filter out data recieved by server'''

        if not self.connected: 
            if self.debug:
                print("error: not connected")
            return None
        
        for dataItem in self.RecieveQueue:
            del self.RecieveQueue[0]
            return {dataItem}
        return {}
