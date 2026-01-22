import time, math
from hw import LCD, IMU

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)        
while True:
    z_a = IMU.Read_XYZ()[5]/500
    y = int(120 * z_a)
    LCD.line(120,120,120, 120+y, c)
    LCD.scroll(-1,0)
    print(y)

    LCD.show()
    time.sleep(0.1)


