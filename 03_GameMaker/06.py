#妥協好了...
from machine import Pin, PWM
from utime import sleep
import touch,math,utime
from math import sqrt
LCD = touch.LCD_1inch28()
color = LCD.color
LCD.set_bl_pwm(15535)

R = 110
r = 10
cx = 120
cy = 120
while True:
    LCD.fill(color(20,20,20))
    xyz = touch.QMI8658().Read_XYZ()
    if xyz[1] < 1 and xyz[1] > -1:
        y = int(-xyz[0]*R)+ cy
        xsqrt = int(sqrt(R*R-pow((y-cy),2)))
        #print(xsqrt)
        if xyz[1] >= 0:
            x = cx + xsqrt
        else:
            x = cx - xsqrt
    
        for i in range(-r,r,1):
            for j in range(-r,r,1):
                if i*i + j*j <= r*r:
                    LCD.pixel(x+i,y+j,LCD.white)
        LCD.show()