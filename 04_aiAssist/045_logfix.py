import time, math
from hw import LCD, IMU
c = LCD.color(255,255,0)
data = open('record','w') 
walkNum = 0 # 計步器 = 0
while 1:
    LCD.fill(0)
    yg0 = IMU.Read_XYZ()[1]-1
    time.sleep(0.05)
    yg1 = IMU.Read_XYZ()[1]-1
    if yg0 * yg1 < 0:
        walkNum = walkNum + 1
        LCD.write_text(str(walkNum),120,120,3,c)
        data.write(str(walkNum))
        LCD.show()