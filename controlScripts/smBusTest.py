import smbus
import time

bus = smbus.SMBus(1)

class Motor:
    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        self.lastWriteTime = 0
        self.lastWrittenSpeed = 0

        self.upperSpeedLimit = 20
        self.lowerSpeedLimit = -20

        self.setSpeed(0)

    def writeBus(self,speed):
        
        try:
            requestedSpeed = max(self.lowerSpeedLimit, min(speed, self.upperSpeedLimit))
            bus.write_word_data(self.address, 0, requestedSpeed)
            self.lastWrittenSpeed = requestedSpeed
        except OSError as e:
            print(f"Error occurred: {e}")

    def setSpeed(self, speed):
        if(time.time() - self.lastWriteTime > 5):
            self.writeBus(0)

        # TODO: Do something to ramp if the requested speed is much different than self.lastWrittenSpeed

        self.writeBus(speed)
        self.lastWriteTime = time.time()


motors = [Motor(bus, 0x2a),Motor(bus, 0x2b),Motor(bus, 0x2c),Motor(bus, 0x2d),Motor(bus, 0x2e),Motor(bus, 0x2f)]


# Write the 16-bit value to the specified register address
# bus.write_word_data(device_address, register_address, value)

for i in range(-10,10,1):
    motors[0].setSpeed(i)
    time.sleep(0.5)


        
