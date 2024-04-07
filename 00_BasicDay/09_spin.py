import time , touch, math

LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

while 1:
    now = list(time.localtime())
    sec = now[5] * 6#一分鐘60秒,轉360˚= 每一秒轉6˚
    radian = math.radians(sec)
    x_sin = math.sin(radian)
    y_cos = math.cos(radian)
    LCD.line(120,120,int(120*x_sin+120),int(-120*y_cos+120),LCD.black)#從圓心120,120開始，結束在sin,cos，其中cos需用減的，因為y軸往上為負往下為正
    LCD.show()
    LCD.line(120,120,int(120*x_sin+120),int(-120*y_cos+120),LCD.white)#做一個抹除作業，若整行加註記不執行會怎樣呢？
    print(now[5])