import requests
response = requests.get("http://0.0.0.0:9111/v1.0/ip")
print(response.json())