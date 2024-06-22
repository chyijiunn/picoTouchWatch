from machine import ADC ,Pin
import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
Vbat_Pin = 29
color = LCD.color
LCD.set_bl_pwm(35535)
cx , cy =120 ,120 #center of watch
R,G,B = (random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))

c1 = color(R,G,B)
c2 = color(256 - R,255,100)
c3 = color(256-R,120 ,B)

def lineCharacterCount(string,charactersize):
    lenth = 8*len(string)*charactersize
    x = int(cx - lenth/2)
    return x 
    
def displayWord(word,charactersize):
    LCD.write_text(word,lineCharacterCount(word,charactersize),cy,charactersize,c1)

def dot(cx,cy,r,color):
    for i in range(-r,r):
        for j in range(-r,r):
            if i*i + j*j < r*r:LCD.pixel(cx+i,cy+j,color)
    
def function_1():
    LCD.fill(0)
    displayWord('Right',5)
    dot(b1,cy,r,c3)
    LCD.show()
    while 1:
        if Touch.Flag == 1:
            x = Touch.X_point
            y = Touch.Y_point
            Touch.Flag = 0
            if x > b1-r and x < b1+r and y >cy-r and y < cy+r:
                break
def function_2():
    LCD.fill(0)
    displayWord('Left',5)
    dot(b2,cy,r,c3)
    LCD.show()
    while 1:
        if Touch.Flag == 1:
            x = Touch.X_point
            y = Touch.Y_point
            Touch.Flag = 0
            if x > b2-r and x < b2+r and y >cy-r and y < cy+r :
                break
            


Touch.Flgh = 0
Touch.Flag = 0
r = 10
b1 ,b2 = 10 ,230

while 1:
    #功能 1
    if Touch.Flag == 1:
        x = Touch.X_point
        y = Touch.Y_point
        if x > b2-r and x < b2+r and y >cy-r and y < cy+r :function_1()#R
        if x > b1-r and x < b1+r and y >cy-r and y < cy+r :function_2()#L
        time.sleep(0.3)

    else:
        LCD.fill(0)
        displayWord('Main',4)
        dot(b1,cy,r,c3)#L
        dot(b2,cy,r,c3)#R
        dot(cx,b1,r,c3)#U
        dot(cx,b2,r,c3)#D
        
        LCD.show()
        