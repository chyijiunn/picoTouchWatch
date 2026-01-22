import time, math
from hw import LCD

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)

while True:
    now = list(time.localtime())
    tic = str(now[3])+':'+str(now[4])
    sec = now[5] * 6#一分鐘60秒,轉360˚= 每一秒轉6˚
    
    radian = math.radians(sec)
    
    x_sin = math.sin(radian)
    y_cos = math.cos(radian)
    
    LCD.line(120,120,int(120*x_sin+120),int(-120*y_cos+120),c)#從圓心120,120開始，結束在sin,cos，其中cos需用減的，因為y軸往上為負往下為正
    LCD.write_text(tic ,60,120,3,c )
    LCD.show()
    LCD.fill(0)
    time.sleep(1)
