FROM balenalib/raspberry-pi-debian:latest

WORKDIR /flasksocket

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    build-essential \
    libzmq3-dev \
    supervisor

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Copy the supervisor configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

LABEL version="1.0.1"
LABEL permissions='{\
  "ExposedPorts": {\
    "5000/tcp": {}\
  },\
  "HostConfig": {\
    "Privileged": true,\
    "PortBindings": {\
      "5000/tcp": [\
        {\
          "HostPort": ""\
        }\
      ]\
    },\
    "Binds":[\
      "/dev:/dev"\
    ]\
  }\
}'

LABEL authors='[\
    {\
        "name": "Mark Skinner",\
        "email": "markhskinner@gmail.com"\
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

CMD ["supervisord", "-n"]