"""
Pca 9554 test for the MiniROV2
"""
import time
import smbus
import pca9554
i2c1 = smbus.SMBus(1)

esc1 = smbus.SMBus(1)

ESC_EN1 = 2
ESC_EN2 = 3
ESC_EN3 = 0
ESC_EN4 = 5
ESC_EN5 = 1
ESC_EN6 = 4
FAN_EN  = 6
ESC_EN = [7,ESC_EN1,ESC_EN2,ESC_EN3,ESC_EN4,ESC_EN5,ESC_EN6]
i2c_address = 0x38
pca_driver = pca9554.Pca9554(i2c_address)



def pca9554_init():
# enable all as be outputs and set low
	for i in range(0, 8):
		pca_driver.write_config_port(i, pca9554.OUTPUT)
		pca_driver.write_port(i,0)

def set_fan(state):
	pca_driver.write_port(FAN_EN,state);

def set_ESC(esc_id, state):
	pca_driver.write_port(ESC_EN[esc_id],state)

def checkForDevice(address):
    #Read incoming logic levels of the ports (returns actual pin value)."""
    try:
        return i2c1.read_byte_data(address, 0)
    except:
        return None

def checkESC(n):
    #turn on the ESC
    set_ESC(n,1)
    print("Turning on  ESC",n ,"... ", end="",flush=True)
    time.sleep(1)
    
    for i in range(1, 7):
        #chech that the address responds
        if checkForDevice(0x29 + i) is None:
            print("-", end="",flush=True)
        else:
            print(i, end="",flush=True)
        time.sleep(0.2)
            
    #turn off the ESC
    set_ESC(n,0)
    print(" ")
    #print("Turning off ESC",n ,"... ", end="",flush=True)
    time.sleep(1)

def ESC1on():
    data = [200,100]
    esc1.write_i2c_block_data(0x2a, 0, data)

def ESC1off():
    data = [0,0]
    esc1.write_i2c_block_data(0x2a, 0, data)

#Init the IO expander. This starts with everything off
print("--------- ESC IO Expander Test ---------")
print("----------------------------------------")
pca9554_init()

print("on")
set_ESC(1,1)

# for i in range(5):
    
    
#     ESC1on()
#     time.sleep(2)
#     ESC1off()
#     time.sleep(2)


# set_ESC(1,0)

#for i in range(1, 7):
#	checkESC(i)

