from machine import Pin, PWM
from utime import sleep
import touch,math,utime
LCD = touch.LCD_1inch28()
color = LCD.color
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)
LCD.set_bl_pwm(15535)

while Touch.Gestures != 0x01:
    LCD.fill(LCD.black)
    LCD.write_text('SlideUP',40,45,3,color(90,250,200))
    LCD.write_text('to',100,100,2,color(190,250,200))
    LCD.write_text('Start',60,135,3,color(250,180,250))
    LCD.show()

def runDotRing(tic , spinLen , color):
    r = 10
    now = list(time.localtime())
    x = int(spinLen*math.sin(math.radians(now[tic]*6)))
    y = int(spinLen*math.cos(math.radians(now[tic]*6)))
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(cx+x+i,cy-y+j,color)
while 1:
    xyz = touch.QMI8658().Read_XYZ()
    if xyz[0]  == 1:angle = 90
    
    LCD.fill(0)
 
    LCD.show()
    

