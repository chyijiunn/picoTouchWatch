import time , hw , math # import math
IMU   = hw.IMU
LCD = hw.LCD

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)        
while True:
    yg = IMU.Read_XYZ()[1]
    degree = math.degrees(math.asin(yg))
    y = int(120 * (1 + yg ))#the end of spin
    
    LCD.pixel(120, y, c)
    print(degree)

    LCD.show()
    time.sleep(0.01)


