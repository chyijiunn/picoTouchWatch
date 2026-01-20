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
    tic = str(now[3])
    LCD.write_text(tic ,60,120,3,c )
    spin(now[4] , 100 , c)
    spin(now[5] , 110 , c)
    LCD.show()
    LCD.fill(0)
    time.sleep(1)


