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
    print()
    y = int(round(-xyz[0]*R,2) + cy)
    
    if xyz[1] > 0 and xyz[1] <= 1:
        x = int(pow(R*R-pow((y-cy),2),0.5)+cx)
    elif xyz[1] < 0 and xyz[1] >= -1:
        x = cx - int(pow(R*R-pow((y-cy),2),0.5))
    else:pass
    
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(x+i,y+j,LCD.white)
    LCD.show()
    sleep(0.01)
