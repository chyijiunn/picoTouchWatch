import time, math
from hw import LCD

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)

def spin(value , length , color):
    x = math.sin(math.radians(value*6))
    y = math.cos(math.radians(value*6))
    LCD.line(120,120,int(length*x+120),int(-length*y+120),color)

while True:
    now = list(time.localtime())
    h = now[3]
    if h > 12: h = h-12
    spin((now[4]/60 + h)*5,50,c)
    spin(now[4],100,c)
    spin(now[5],110,c)
    LCD.show()
    LCD.fill(0)
    time.sleep(1)



