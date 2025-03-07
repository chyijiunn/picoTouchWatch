from machine import Pin, PWM
from utime import sleep
import touch,math,utime
LCD = touch.LCD_1inch28()
color = LCD.color
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)
LCD.set_bl_pwm(15535)

R = 110
r = 5
cx = 120
cy = 120
while True:
    LCD.fill(color(20,20,20))
    xyz = touch.QMI8658().Read_XYZ()
    y = int(-xyz[0]*R + cy)
    if xyz[1] > 0:#牽涉到開根號，需要根據數據修正 x 座標
        x = int(pow(R*R-pow((y-cy),2),0.5)+cx)
    else:
        x = cx - int(pow(R*R-pow((y-cy),2),0.5))

    LCD.pixel(x,y,LCD.white)
    LCD.show()
