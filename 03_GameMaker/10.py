#shoot
from machine import Pin, PWM
from utime import sleep
import touch
LCD = touch.LCD_1inch28()
color = LCD.color
LCD.set_bl_pwm(35535)
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
Touch.tim.init(period=1, callback=Touch.Timer_callback)
Touch.Flag = 0
LCD.fill(color(0,0,0))
def shoot(x,y):
    shootsize = 20
    for j in range(y/shootsize):
        for i in range(shootsize):
            LCD.vline(x,y-(shootsize*j),shootsize,color(150,150,20))
            LCD.show()
        for i in range(shootsize):
            LCD.vline(x,y-(shootsize*j),shootsize,color(0,0,0))
            
        
while 1:
    if Touch.Flag == 1:
        x , y = Touch.X_point , Touch.Y_point
        shoot(x,y)
        Touch.Flag = 0
 


