import core.socket

import time

class ServerThread:
    def __init__(self, Instance):
        self.Queue = {}
        self.ClassSocket = Instance

        self.system_flags = ["ping", "room_info"]

    def process_send(self):
        for QueueItem in list(self.Queue):
            userid, data = QueueItem

            for userId, conn in self.Connected.items():
                try:
                    if userId != userid:
                        conn.send(data.encode())
                except Exception as e:
                    if self.debug:
                        print(f"Error sending data to user {userId}: ", e)
                
            self.Queue.remove(QueueItem)

    def filter_data(self, data, userId):
        if data.decode() in self.system_flags:
            # handle flags
            #self.Queue.append((userId, data.decode()))
            pass
        else:
            self.Queue.append((userId, data.decode()))

    def recieve_data(self):
        while self.ClassSocket.ServerSocket:
            for userId, conn in list(self.ClassSocket.Connected.items()):
                try:
                    data = conn.recv(1024)
                    if data:
                        if self.ClassSocket.debug:
                            print("Received data from user {}: {}".format(userId, data.decode()))
                        
                    self.filter_data(data.decode(), userId)

                except BlockingIOError:
                    continue

                except Exception as e:
                    if self.ClassSocket.debug:
                        print("Error receiving data from user {}: {}".format(userId, e))
                    del self.ClassSocket.Connected[userId]
            
            self.process_send()

    def run(self):
        self.recieve_data()

class ClientThread:
    def __init__(self, Instance):
        self.Queue = []
        self.Instance = Instance

    def filter_data(self, data):
        self.Instance.RecieveQueue.append(data)

    def recieve_data(self):
        while self.Instance.Connected:
            time.sleep(0.1)
            try:
                data = self.Instance.ClientSocket.recv(1024)
                if data:
                    self.filter_data(data.decode())
                    
            except BlockingIOError:
                time.sleep(0.01)
                continue
            except Exception as e:
                if self.Instance.debug:
                    print("Error receiving data: ", e)
                break

    def run(self):
        self.recieve_data()