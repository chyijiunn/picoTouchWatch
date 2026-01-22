import time, math
from hw import LCD

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)

while True:
    now = list(time.localtime())
    print(str(now[3])+':'+str(now[4])+':'+str(now[5]))
    time.sleep(1)