import time, math
from hw import LCD, IMU

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)
c0 = LCD.color(0,0,0)    
while True:
    yg = IMU.Read_XYZ()[1]
    if yg > 1: yg =  1	
    if yg <-1: yg = -1
    degree = math.degrees(math.asin(yg))
    
    y = int(120 * (1 + yg ))
    
    LCD.fill_rect(120,100,120,40,c0 )#refresh
    LCD.write_text(str(degree),120,100,3,c) #(str , x , y , color )
    
    LCD.show()
    time.sleep(0.01)


