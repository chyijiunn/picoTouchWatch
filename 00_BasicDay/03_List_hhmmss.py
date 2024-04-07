import utime
import touch
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

LCD.fill_rect(0,0,240,40,LCD.black)
LCD.text("Now",110,25,LCD.white)

now = list(utime.gmtime())
LCD.text(str(now[3:6]),80,120,LCD.black)#list格式 3 ~ 6 ，不含 6
LCD.show()

print(now)#電腦螢幕上的是否相同