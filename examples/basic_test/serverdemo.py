import rNet
import time

Server = rNet.Host(debug=False, connections_allowed=10)

with Server:
    Server.start()

    while True:
        time.sleep(0.1)