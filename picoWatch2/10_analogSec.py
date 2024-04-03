import time , touch, math

LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

while 1:
    LCD.fill_rect(0,0,240,240,LCD.white)
    now = list(time.localtime())
    #秒針
    sec = now[5] * 6
    radian = math.radians(sec)
    x_sin = math.sin(radian)
    y_cos = math.cos(radian)
    LCD.line(120,120,int(120*x_sin+120),int(-120*y_cos+120),LCD.red)
    
    #分針
    minute = now[4] * 6
    radian = math.radians(minute)
    x_sin = math.sin(radian)
    y_cos = math.cos(radian)
    LCD.line(120,120,int(110*x_sin+110),int(-110*y_cos+110),LCD.black)
    
    #分針和秒針有相同程式碼，可以合併作業嗎？
    #時針的設計也會一樣嗎？

    LCD.show()
    time.sleep(1)
    