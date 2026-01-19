import time, math
from hw import LCD, IMU

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)
c0 = LCD.color(0,0,0)
while 1:
    now = list(time.localtime())
    sec = now[5]#讀取系統秒數
    LCD.show()
    time.sleep(0.51)





