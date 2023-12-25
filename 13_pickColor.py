import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)
color = LCD.color

LCD.set_bl_pwm(15535)
BG = color(0,0,0)
FG = color(255,255,255)
LCD.fill(BG)
LCD.show()

def pickcolor():
    Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
    x = y  = 0
    Touch.Flgh = 0
    Touch.Flag = 0
    Touch.tim.init(period=1, callback=Touch.Timer_callback)
    while True:
        '''
        if Touch.Flag == 1:
            x = Touch.X_point
            y = Touch.Y_point
            LCD.pixel(x,y,FG)
            LCD.show()'''
        x = Touch.X_point
        y = Touch.Y_point
        LCD.pixel(x,y,FG)
        LCD.show()

pickcolor()



