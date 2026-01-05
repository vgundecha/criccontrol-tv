from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl

# Connect to TV using secure connection
client = WebOSClient("192.168.1.6", secure=True)
# We first get client key by passing an empty dict. This key is saved from a previos run
store = {'client_key': '001a999104fa430a302bb726da73881c'}  

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

# Now you can use MediaControl
media = MediaControl(client)
volume = media.get_volume()
print(f"Current volume: {volume}")
