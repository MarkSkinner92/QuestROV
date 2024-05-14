import requests, json

# THIS IS SO COOL!

# Here are the API endpoints for managing ethernet
# https://github.com/bluerobotics/BlueOS/blob/bc262360f993c9bdeff9cd1ff55c4a080c76f6c8/core/services/cable_guy/main.py#L53

# Retrieve ethernet interfaces
# response = requests.get('http://192.168.1.65:9090/v1.0/ethernet').json()

# Configure a ethernet interface
# POST /ethernet


# Add an IP Address

# msg = {
#   "interface_name": "eth0",
#   "mode": "unmanaged",
#   "ip_address": "192.168.1.20"
# }
# response = requests.post('http://192.168.1.65:9090/v1.0/address', params=msg)


# Remove an IP Address

# msg = {
#   "interface_name": "eth0",
#   "ip_address": "192.168.1.20"
# }
# response = requests.delete('http://192.168.1.65:9090/v1.0/address', params=msg)

#print(response.content)
# print(json.dumps(response, indent=4))