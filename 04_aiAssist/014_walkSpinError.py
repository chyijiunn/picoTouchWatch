import time, math
from hw import LCD, IMU

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)

while True:
    yg = IMU.Read_XYZ()[1]
    if yg > 1: yg =  1#restrick |sin| <= 1
    if yg <-1: yg = -1
    degree = math.degrees(math.asin(yg))
    
    y = int(120 * (1 + yg ))
    
    LCD.pixel(120, y, c)
    print(degree)

    LCD.show()
    time.sleep(0.01)


