"""rNet is a functional wrapper for the Socket.IO library, designed to simplify development for connection-heavy applications."""

from rNet.core import socket
from rNet.core.room import Room

import time
import threading

def ProcessData(self): 
    while True:
        time.sleep(self.ProcessorDelay)
        for QueueItem in list(self.ProcessDataQueue):
            userid, data = QueueItem

            for userId, conn in self.Connected.items():
                try:
                    if userId != userid:
                        conn.send(data.encode())
                except Exception as e:
                    if self.debug:
                        print(f"Error sending data to user {userId}: ", e)
                
            self.ProcessDataQueue.remove(QueueItem)

def ClientRecieveData(self): # Process Data Recieved (threaded)
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

def ServerRecieveData(self): # ON SEPERATE THREAD -- ORGANIZE SOON
    RemoveCache = set()

    while True:
        for userId, conn in list(self.Connected.items()):
            try:
                data = conn.recv(1024)
                if data:
                    if self.debug:
                        print(f"Received data from user {userId}: {data.decode()}")

                    if data.decode() in ["ping", "room_info"]:
                        if data.decode() == "room_info":
                            info = self.room_information()
                            conn.send(str(info).encode())

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



class Host:
    def __init__(self, dest : str = '127.0.0.1:8001', debug : bool=True, connections_allowed : int=10):
        '''Create a new Host instance. \nParams:
        dest: The destination address for the server.
        debug: Whether to enable debug mode.
        connections_allowed: The maximum number of connections allowed.
        '''
        self.dest = dest
        self.debug = debug
        self.connections_allowed = connections_allowed

        self.ServerSocket = None
        self.Connected = {}
        self.Rooms : list[Room] = []
        self.ProcessorDelay = 0.10

        self.ProcessDataQueue = []

    def __enter__(self):
        if self.debug: 
            print("Server Starting await")

    def __exit__(self, exc_type, exc, tb):
        if self.debug:
            print("Server Error, Disconnecting: ", exc_type, exc, tb)

    def get_user_list(self) -> list:
        '''Get the list of connected users.'''
        return list(self.Connected.keys())

    def start(self):
        self.ServerSocket = socket.ServerStart_PythonSocket(self.dest, self.debug, self.Connected, self.connections_allowed)

        while not self.ServerSocket:
            time.sleep(0.1)
            
        RecvDataThread = threading.Thread(target=ServerRecieveData, daemon=True, args=(self,))
        RecvDataThread.start()

        ProcessDataThread = threading.Thread(target=ProcessData, daemon=True, args=(self,))
        ProcessDataThread.start()

    def create_room(self, name: str, connections_allowed: int) -> Room:
        '''Create a new room. \nParams:
        name: The name of the room.
        connections_allowed: The maximum number of connections allowed in the room.
        '''
        room = Room(name, self.get_user_id(), connections_allowed)
        self.Rooms.append(room)
        return room
    
    def room_information(self) -> dict:
        '''Return information about all rooms.  '''
        return {room.name: {"host": room.host, "connections_allowed": room.connections_allowed, "clients": room.get_client_list()} for room in self.Rooms}

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

    def disconnect(self):
        '''Disconnect the client from the server.'''
        if self.Sock:
            self.Sock.close()
        self.connected = False
    
    def get_user_id(self) -> int:
        '''Get the user ID of the client.'''
        return self.UserId

    def wait_connection(self):
        '''Await connection to the server.'''
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

        self.RecieveThread = threading.Thread(target=ClientRecieveData, daemon=True, args=(self,))
        self.RecieveThread.start()

        if self.debug:
            print("Connected")
        
    def send(self, data : any) -> bool:
        '''Send data to the current server. \nParams:
        Data: The data to send to the server and other clients'''
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
        '''Recieve current thread of sent data by the server (room data if avail)'''

        if not self.connected: 
            if self.debug:
                print("error: not connected")
            return None
        
        for dataItem in self.RecieveQueue:
            del self.RecieveQueue[0]
            return {dataItem}
        return {}

    def room_information(self) -> dict:
        if self.connected:
            try:
                self.Sock.send("room_info".encode())
                
                info = self.Sock.recv(1024).decode()
                print(info)

            except Exception as e:
                if self.debug:
                    print("Error getting room information: ", e)
                return {}
        return {}