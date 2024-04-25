FROM arm32v7/python:3.12

WORKDIR /flasksocket

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .


LABEL version="1.0.1"
LABEL permissions='{\
  "ExposedPorts": {\
    "5000/tcp": {}\
  },\
  "HostConfig": {\
    "PortBindings": {\
      "5000/tcp": [\
        {\
          "HostPort": ""\
        }\
      ]\
    }\
  }\
}'
LABEL authors='[\
    {\
        "name": "Willian Galvani",\
        "email": "willian@bluerobotics.com"\
    }\
]'
LABEL company='{\
        "about": "",\
        "name": "Blue Robotics",\
        "email": "support@bluerobotics.com"\
    }'
LABEL type="example"
LABEL readme='https://raw.githubusercontent.com/Williangalvani/BlueOS-examples/{tag}/example1-statichtml/Readme.md'
LABEL links='{\
        "website": "https://github.com/Williangalvani/BlueOS-examples/",\
        "support": "https://github.com/Williangalvani/BlueOS-examples/"\
    }'
LABEL requirements="core >= 1.1"

EXPOSE 5000
#CMD ["sh", "-c", "python3 app.py & python3 serial_com.py & tail -f /dev/null"]
ENTRYPOINT python3 app.py