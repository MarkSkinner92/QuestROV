import requests

# Write number of conencted clients to bag of holding
resp = requests.post("http://192.168.1.188:9101/v1.0/set/fleetManager/connections", json=1)