Useful commands include:

docker ps

build to hub
docker build . -t markskinner92/testflask:latest --output type=registry

build locally
docker build . -t testflask

run locally (allows access to usb devices)
docker run -p 5000:5000 --privileged testflask

ssh pi@adr

{
ExposedPorts:{
5000/tcp:{}
}
HostConfig:{
Privileged:true
PortBindings:{
5000/tcp:[
0:{
HostPort:""
}
]
}
Binds:[
0:"/dev:/dev"
]
}
}