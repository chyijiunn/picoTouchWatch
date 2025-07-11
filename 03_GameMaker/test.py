from machine import Pin, PWM
from utime import sleep
import touch
LCD = touch.LCD_1inch28()
color = LCD.color
LCD.set_bl_pwm(35535)
LCD.vline(120,120,200,color(222,222,222))
LCD.show()