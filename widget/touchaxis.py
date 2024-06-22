from machine import ADC ,Pin
import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)

color = LCD.color
LCD.set_bl_pwm(35535)
cx , cy =120 ,120 #center of watch
R,G,B = (random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))

c1 = color(R,G,B)
c2 = color(256 - R,255,100)
c3 = color(256-R,120 ,B)


def dot(cx,cy,r,color):
    for i in range(-r,r):
        for j in range(-r,r):
            if i*i + j*j < r*r:LCD.pixel(cx+i,cy+j,color)
    
def function_1():
    LCD.fill(0)
    dot(b1,cy,r,c3)
    LCD.show()
    while 1:
        if Touch.Flag == 1:
            x = Touch.X_point
            y = Touch.Y_point
            print(x,y)
            time.sleep(0.1)
            Touch.Flag = 0
            if x > b1-r and x < b1+r and y >cy-r and y < cy+r:break


Touch.Flgh = 0
Touch.Flag = 0
r = 10
b1 ,b2 = 10 ,230


function_1()       
