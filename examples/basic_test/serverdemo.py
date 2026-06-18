import rNet
import time

Server = rNet.Host(debug=False)

with Server:
    Server.start()

    while True:
        time.sleep(0.1)