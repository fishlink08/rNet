import rNet
import time
import json

Client = rNet.Client(debug=False)

with Client:
    Client.wait_connection()

    while True:
        time.sleep(0.1)
        
        jsonData = {"message": "yo whats up"}
        Client.send(json.dumps(jsonData))

        for data in Client.recieve():
            pass