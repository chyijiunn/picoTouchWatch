import time , touch, math

LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

def spin( tic , spinLen , color):#讀取tic = 3,4,5分別為時分秒
    now = list(time.localtime())
    x = spinLen*math.sin(math.radians(now[tic]*6))#x = 要水平位移的點
    y = spinLen*math.cos(math.radians(now[tic]*6))
    LCD.line(120,120,int(spinLen+x),int(spinLen-y),color)

while 1:
    LCD.fill_rect(0,0,240,240,LCD.white)
    spin(5,120,LCD.red)
    spin(4,110,LCD.black)

    LCD.show()