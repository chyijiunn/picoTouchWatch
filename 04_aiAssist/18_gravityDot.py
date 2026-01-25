import time, math
from hw import LCD, IMU

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)
c0 = LCD.color(0,0,0)

def runDot(r , x , y , color):
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(x+i,y+j,color)
while True:
    yg = IMU.Read_XYZ()[1]
    xg = IMU.Read_XYZ()[0]
    if yg > 1: yg =  1
    if yg <-1: yg = -1
    if xg > 1: xg =  1
    if xg <-1: xg = -1

    y = 120 - int(120 * xg)
    x = 120 + int(120 * yg)
    
    LCD.fill_rect(0,0,240,240,c0 )
    runDot(5 , x , y , c)

    LCD.show()
    time.sleep(0.01)




