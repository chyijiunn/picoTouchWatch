from machine import Pin, PWM
from utime import sleep
import touch,math,utime
LCD = touch.LCD_1inch28()
color = LCD.color
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)
LCD.set_bl_pwm(15535)

r = 10
ori_x = 120
ori_y = 120
while True:
    LCD.fill(color(100,20,20))
    xyz = touch.QMI8658().Read_XYZ()
    x_shift = int(xyz[0]*100)
    y_shift = int(xyz[1]*100)

    LCD.text("x_shift",70,25,LCD.white)
    LCD.text(str(x_shift),60,40,LCD.white)
    print(xyz[5])
    LCD.text("y_shift",160,25,LCD.white)
    LCD.text(str(y_shift),150,40,LCD.white)
    LCD.show()