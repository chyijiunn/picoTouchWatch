#shoot
from machine import Pin, PWM
from utime import sleep
import touch , random
LCD = touch.LCD_1inch28()
color = LCD.color
LCD.set_bl_pwm(35535)
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
Touch.tim.init(period=1, callback=Touch.Timer_callback)
Touch.Flag = 0
LCD.fill(color(0,0,0))
def shoot(x,y):
        LCD.line(x,y,120,120,color(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        LCD.show()
        
while 1:
    
    if Touch.Flag == 1:
        x , y = Touch.X_point , Touch.Y_point
        shoot(x,y)
        #LCD.write_text('Touch',65 , 120,2 , color(200,200,200))
        Touch.Flag = 0
    LCD.show()
    sleep(0.02)
 
