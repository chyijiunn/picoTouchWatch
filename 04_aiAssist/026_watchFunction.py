import time, math
from hw import LCD

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)

def spin(value , length , color):
    x = math.sin(math.radians(value*6))
    y = math.cos(math.radians(value*6))
    LCD.line(120,120,int(length*x+120),int(-length*y+120),color)
def watch(cx , cy , factor):
    now = list(time.localtime())
    r = factor * 120
    h = now[3]
    if h > 12: h = h-12
    spin((now[4]/60 + h)*5,r*5/12,c)
    spin(now[4],r*10/12,c)
    spin(now[5],r*11/12,c)
while True:
    watch(120,120,1)
    LCD.show()
    LCD.fill(0)
    time.sleep(1)
