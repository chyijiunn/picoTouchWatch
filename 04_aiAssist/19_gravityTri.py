import time, math
from hw import LCD, IMU

LCD.fill(0)
c = LCD.color(255,255,0)
c0 = LCD.color(0,0,0)
while True:
    yg = IMU.Read_XYZ()[1]
    xg = IMU.Read_XYZ()[0]
    if yg > 1:
        yg =  1
    if yg <-1:
        yg = -1
    if xg > 1:
        xg =  1
    if xg <-1:
        xg = -1

    y0 = 120 - int(120 * xg)
    x0 = 120 + int(120 * yg)
    
    y1 = 120 + int(10 * xg)
    x1 = 120 + int(10 * yg)
    
    y2 = 120 - int(10 * xg)
    x2 = 120 - int(10 * yg)

    LCD.fill_tri(x0,y0,x1,y1,x2,y2,c)
    LCD.show()
    LCD.fill(0)
    time.sleep(0.01)