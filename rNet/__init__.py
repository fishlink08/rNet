"""rNet is a functional wrapper for the Socket.IO library, designed to simplify development for connection-heavy applications."""

from rNet.core import socket
from rNet.core.room import Room
from rNet.core.threaded import ServerThread, ClientThread

import time
import threading
import json

def ClientSystemInformation(self):
    while True:
        time.sleep(0.5)
        if self.Connected:
            try:
                self.Sock.send("room_info".encode())
                
                room_info = json.loads(self.Sock.recv(1024).decode())
                if 'room_info' in room_info:
                    self.SystemInformation['rooms'] = room_info
            except BlockingIOError:
                continue
            except Exception as excp:
                pass

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
        '''Get the list of Connected users.'''
        return list(self.Connected.keys())

    def start(self):
        self.ServerSocket = socket.ServerStart_PythonSocket(self.dest, self.debug, self.Connected, self.connections_allowed)

        while not self.ServerSocket:
            time.sleep(0.1)

        ServerThreadClass = ServerThread(self)
            
        RecvDataThread = threading.Thread(target=ServerThreadClass.run, daemon=True)
        RecvDataThread.start()

    def create_room(self, name: str, connections_allowed: int) -> Room:
        '''Create a new room. \nParams:
        name: The name of the room.
        connections_allowed: The maximum number of connections allowed in the room.
        '''
        room = Room(name, connections_allowed)
        self.Rooms.append(room)

        return room
    
    def room_information(self) -> list:
        '''Return information about all rooms.'''
        info = [[room.name, room.get_client_list()] for room in self.Rooms]
        if len(info) == 0:
            return ['room_info', 'No Rooms']
        info.append('room_info')
        return info
    
class Client:
    '''Create a new Client instance. \nParams:
    dest: The destination address for the client.
    debug: Whether to enable debug mode.
    '''
    def __init__(self, dest : str = '127.0.0.1:8001', debug : bool=True):
        self.dest = dest
        self.debug = debug

        self.Connected = False
        self.ClientSocket = None
        self.UserId = None

        self.RecieveThread = None
        self.RecieveQueue = []

        self.SystemPingThread = None
        self.SystemInformation = {
            'rooms': []
        }

    def __enter__(self):
        if self.debug: 
            print("Client Connecting")

    def __exit__(self, exc_type, exc, tb):
        if self.debug:
            print("Client Error, Disconnecting: ", exc_type, exc, tb)

    def disconnect(self):
        '''Disconnect the client from the server.'''
        if self.ClientSocket:
            self.ClientSocket.close()
        self.Connected = False
    
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

        self.ClientSocket = result[0]
        self.UserId = result[1]
        
        self.Connected = True
        self.ClientSocket.setblocking(False)

        self.ClientThreadObject = ClientThread(self)

        self.ClientThread = threading.Thread(target=self.ClientThreadObject.run, daemon=True)
        self.ClientThread.start()

        self.SystemPingThread = threading.Thread(target=ClientSystemInformation, daemon=True, args=(self,))
        self.SystemPingThread.start()

        if self.debug:
            print("Connected")
        
    def send(self, data : any) -> bool:
        '''Send data to the current server. \nParams:
        Data: The data to send to the server and other clients'''
        if not self.Connected:
            if self.debug:
                print("Not Connected, cannot send data")
            return False

        try:
            self.ClientSocket.send(data.encode())
            return True
        except Exception as e:
            if self.debug:
                print("Error sending data: ", e)
            return False

    def recieve(self, filter = None) -> dict:
        '''Recieve current thread of sent data by the server (room data if avail)'''

        if not self.Connected: 
            if self.debug:
                print("error: not Connected")
            return None
        
        for dataItem in self.RecieveQueue:
            del self.RecieveQueue[0]
            return {dataItem}
        return {}

    def room_information(self) -> list:
        if self.Connected:
            return self.SystemInformation['rooms']
        return ["Not Connected to Server"]