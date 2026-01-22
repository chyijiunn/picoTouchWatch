import time, math
from hw import LCD, IMU

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)        
while True:
    z_a = IMU.Read_XYZ()[5]/500
    y = int(120 * (1 + z_a ))
    LCD.pixel(120, y, c)
    LCD.scroll(-1,0)
    print(z_a)
    #print(round(xyz[5],2))

    LCD.show()
    time.sleep(0.01)

