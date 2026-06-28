import rNet
import time
import json

Client = rNet.Client(debug=True)

with Client:
    Client.wait_connection()

    while True:
        time.sleep(0.1)

        recieved_info = Client.room_information()
        print(recieved_info)