class Room:
    def __init__(self, name, host, connections_allowed : int):
        self.name = name
        self.host = host
        self.connections_allowed = connections_allowed
        self.clients : list[int] = []
        
    def add_client(self, client_userid : int):
        '''Add a client to the room.'''
        self.clients.append(client_userid)

    def remove_client(self, client):
        '''Remove a client from the room.'''
        self.clients.remove(client)
    
    def get_client_list(self) -> list:
        '''Get the list of clients in the room.'''
        return self.clients
    
    