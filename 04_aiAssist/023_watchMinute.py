import time, math
from hw import LCD

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)

while True:
    now = list(time.localtime())
    tic = str(now[3])
    sec = now[5] * 6
    minute = now[4] * 6 #一時 60 分,轉360˚= 每一分轉6˚
    radian_s = math.radians(sec)
    radian_m = math.radians(minute)
    
    x_sin_s = math.sin(radian_s)
    y_cos_s = math.cos(radian_s)
    x_sin_m = math.sin(radian_m)
    y_cos_m = math.cos(radian_m)
    
    LCD.line(120,120,int(120*x_sin_s+120),int(-120*y_cos_s+120),c)#從圓心120,120開始，結束在sin,cos，其中cos需用減的，因為y軸往上為負往下為正
    LCD.line(120,120,int(100*x_sin_m+120),int(-100*y_cos_m+120),c)
    LCD.write_text(tic ,60,120,3,c )
    LCD.show()
    LCD.fill(0)
    time.sleep(1)

