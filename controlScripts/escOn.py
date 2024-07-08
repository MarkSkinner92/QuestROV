import smbus
import pca9554


i2c_address = 0x38
pca_driver = pca9554.Pca9554(i2c_address)
# enable all as be outputs and set low
for i in range(0, 8):
    pca_driver.write_config_port(i, pca9554.OUTPUT)
    pca_driver.write_port(i,1)



