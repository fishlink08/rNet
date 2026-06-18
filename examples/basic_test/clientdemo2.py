import rNet
import time

Client = rNet.Client(debug=False)

with Client:
    Client.wait_connection()

    while True:
        time.sleep(0.1)

        for data in Client.recieve():
            print(f"Received data: {data}")