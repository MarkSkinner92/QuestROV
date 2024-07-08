import requests
response = requests.get("http://host.docker.internal:9090/v1.0/ethernet")
jdata = response.json()
if(len(jdata) > 0):
    print(jdata[0]['addresses'][0]['ip'])