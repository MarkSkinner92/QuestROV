"""
Pca 9554 test for the MiniROV2
"""
import time
import smbus
import pca9554
i2c1 = smbus.SMBus(1)
ESC_EN1 = 3
ESC_EN2 = 2
ESC_EN3 = 5
ESC_EN4 = 0
ESC_EN5 = 4
ESC_EN6 = 1
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
	time.sleep(2)
	#chech that the address responds
	if checkForDevice(0x2a) is None:
		print("No ESC Found. FAIL")
	else:
		print("ESC Found.    PASS")
	#turn off the ESC
	set_ESC(n,0)
	print("Turning off ESC",n ,"... ", end="",flush=True)
	time.sleep(1)
	#check that the address does not respond
	if checkForDevice(0x2a) is None:
		print("No ESC Found. PASS")
	else:
		print("ESC Found.    FAIL")
	
	time.sleep(0.2)

#Init the IO expander. This starts with everything off
print("--------- ESC IO Expander Test ---------")
print("----------------------------------------")
pca9554_init()
#set_fan(1)
print("All ESCs OFF.        ",end=" ",flush=True)
#check to ensure the ESCs are not responding since power is off
if checkForDevice(0x2a) is None:
	print("No ESC Found. PASS")
else:
	print("ESC Found. FAIL")
#check each one
for i in range(1, 7):
	checkESC(i)
print("ESC cooling fan ON .. ",end="",flush=True)
set_fan(1)
time.sleep(4)
set_fan(0)
print("Fan OFF.")