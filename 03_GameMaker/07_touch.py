#add touch shoot
from machine import Pin, PWM
from utime import sleep
import touch
LCD = touch.LCD_1inch28()
color = LCD.color
LCD.set_bl_pwm(35535)
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
Touch.tim.init(period=1, callback=Touch.Timer_callback)
Touch.Flag = 0
while 1:
    LCD.fill(color(0,0,0))
    if Touch.Flag == 1:
        LCD.write_text('Touch',65 , 120,2 , color(200,200,200))
        Touch.Flag = 0
    LCD.show()
    sleep(0.02)
 