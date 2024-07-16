import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
color = LCD.color

LCD.set_bl_pwm(15535)
BG = color(0,0,0)
FG = color(255,255,255)
c1 = color(55,25,125)
c2 = color(255,225,255)
LCD.fill(BG)
LCD.show()
xstart,ystart,xlen,ylen = 80,160 , 80 , 20

def adjust():
    
    