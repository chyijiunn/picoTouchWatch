import time
from hw import LCD

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)

while True:
    now = list(time.localtime())
    tic = str(now[3])+':'+str(now[4])+':'+str(now[5])
    LCD.write_text(tic ,30,120,3,c )
    LCD.show()
    LCD.fill(0)						# refresh
    time.sleep(1)
