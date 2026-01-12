from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl

IP = "192.168.1.2"
CLIENT_KEY = '001a999104fa430a302bb726da73881c'

def connect():
    # Connect to LG TV using secure connection
    client = WebOSClient(IP, secure=True)
    # We first get client key by passing an empty dict. This key is saved from a previos run
    store = {'client_key': CLIENT_KEY}  
    # store = {}

    # Must connect first
    client.connect()
    print("Connected!")

    print(client.register(store))
    # Must register (will use saved client_key, no TV prompt needed)
    for status in client.register(store):
        if status == WebOSClient.PROMPTED:
            print("Please accept the connection on your TV...")
        elif status == WebOSClient.REGISTERED:
            print("Successfully registered!")
    print(store)

    # Now you can use MediaControl
    media = MediaControl(client)
    
    return media

if __name__ == "__main__":
    media = connect()

    volume = media.get_volume()
    print(f"Current volume: {volume}")
