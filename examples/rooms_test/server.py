import rNet
import time

Server = rNet.Host(debug=False, connections_allowed=10)

with Server:
    Server.start()
    MyRoom = Server.create_room("Room 1", 2)

    while True:
        time.sleep(0.1)