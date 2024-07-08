#!/bin/bash

echo "Thruster Test"
sleep 1



i2cset -y 1 0x2a 0x00 0x0000 w

#Check for ESC1
if i2cget -y 1 0x2a >/dev/null
then
    echo "ESC 1 Detected"
else
    echo "ESC 1 Not Detected"
fi

#Check for ESC2
if i2cget -y 1 0x2b >/dev/null
then
    echo "ESC 2 Detected"
else
    echo "ESC 2 Not Detected"
fi

#Check for ESC3
if i2cget -y 1 0x2c >/dev/null
then
    echo "ESC 3 Detected"
else
    echo "ESC 3 Not Detected"
fi

#Check for ESC4
if i2cget -y 1 0x2d >/dev/null
then
    echo "ESC 4 Detected"
else
    echo "ESC 4 Not Detected"
fi

#Check for ESC5
if i2cget -y 1 0x2e >/dev/null
then
    echo "ESC 5 Detected"
else
    echo "ESC 5 Not Detected"
fi

#Check for ESC6
if i2cget -y 1 0x2f >/dev/null
then
    echo "ESC 6 Detected"
else
    echo "ESC 6 Not Detected"
fi

#
echo "ESC 1 Forward"
i2cset -y 1 0x2a 0x00 0x0000 w
sleep 1
i2cset -y 1 0x2a 0x00 0x000F w
sleep 2
i2cset -y 1 0x2a 0x00 0x0000 w