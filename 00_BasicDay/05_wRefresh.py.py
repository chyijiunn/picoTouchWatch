import time
import touch
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

LCD.fill_rect(0,0,240,40,LCD.black)
LCD.text("Now",110,25,LCD.white)
LCD.show()
while 1:
    LCD.fill_rect(0,40,240,200,LCD.white)#局部更新範圍
    now = list(time.localtime())
    LCD.text(str(now[3:6]),80,120,LCD.black)
    LCD.show()
    time.sleep(1)